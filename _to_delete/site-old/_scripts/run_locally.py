#!/usr/bin/env python3
"""
_scripts/run_locally.py
─────────────────────────────────────────────────────────────────────
Run this script on YOUR OWN MACHINE to update citations.
Your personal IP is not blocked by Google Scholar.

Usage:
    pip install playwright beautifulsoup4
    playwright install chromium
    python _scripts/run_locally.py

Then commit and push the result:
    git add _data/citations.json
    git commit -m "chore: update scholar citations"
    git push
─────────────────────────────────────────────────────────────────────
"""

import json
import datetime
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SCHOLAR_ID   = "MpKhKEUAAAAJ"
OUTPUT_PATH  = Path("_data/citations.json")
CURRENT_YEAR = int(datetime.date.today().year)

PROFILE_URL = (
    f"https://scholar.google.com/citations"
    f"?user={SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank"
)


# ── browser fetch ─────────────────────────────────────────────────────────────

def fetch_page():
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: Run:  pip install playwright beautifulsoup4 && playwright install chromium")
        sys.exit(1)

    import time

    print("  Launching Chromium…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled", "--lang=en-US"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US", timezone_id="America/New_York",
        )
        page = ctx.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )

        print(f"  Navigating to Scholar…")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=60000)

        # Dismiss EU consent wall if present
        try:
            btn = page.locator(
                'button:has-text("Accept all"), button:has-text("Reject all"), '
                'button:has-text("I agree"), form[action*="consent"] button'
            ).first
            if btn.is_visible(timeout=3000):
                print("  Consent wall detected — dismissing…")
                btn.click()
                page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        try:
            page.wait_for_selector("#gsc_rsb_st", timeout=15000)
            print("  Profile table loaded ✓")
        except Exception:
            pass

        try:
            page.wait_for_selector("a.gsc_g_a", timeout=10000)
            print("  Histogram bars found ✓")
        except Exception:
            print("  WARNING: Histogram bars not found in DOM")

        time.sleep(2)

        # ── Read histogram directly from the live DOM ──────────────────
        # Scholar's actual structure (confirmed from debug output):
        #
        #   Year labels  → <span class="gsc_g_t">  — ALL years on x-axis (e.g. 2021–2026)
        #   Bar counts   → <span class="gsc_g_al"> — ONLY years with ≥1 citation
        #
        # These two lists have DIFFERENT lengths, so we cannot zip by index.
        # Instead we read the CSS `left` position of each element.
        # Both year labels and bar anchors share the same x-axis pixel grid,
        # so matching by `left` value gives us the correct year↔count pairing.
        js_year_data = page.evaluate("""
            () => {
                const result = {};

                // Build a map of left-px → year from the year label spans
                const yearByLeft = {};
                document.querySelectorAll('#gsc_g_x span.gsc_g_t').forEach(span => {
                    const yr  = span.textContent.trim();
                    const lft = parseInt(span.style.left, 10);
                    if (/^\\d{4}$/.test(yr) && !isNaN(lft)) {
                        yearByLeft[lft] = yr;
                    }
                });

                // Match each bar anchor to a year by its left-px value
                document.querySelectorAll('#gsc_g_bars a.gsc_g_a').forEach(bar => {
                    const lft    = parseInt(bar.style.left, 10);
                    const alSpan = bar.querySelector('span.gsc_g_al');
                    const cnt    = alSpan
                        ? parseInt(alSpan.textContent.trim(), 10)
                        : parseInt(bar.getAttribute('title') || '0', 10);
                    const yr = yearByLeft[lft];
                    if (yr && !isNaN(cnt)) {
                        result[yr] = cnt;
                    }
                });

                // If left-px matching found nothing, fall back to
                // reading counts from bars in document order and
                // pairing with only the year labels that have a bar
                // (i.e. years with ≥1 citation — same count as bars).
                if (Object.keys(result).length === 0) {
                    const bars     = Array.from(document.querySelectorAll('#gsc_g_bars a.gsc_g_a'));
                    const allYears = Array.from(document.querySelectorAll('#gsc_g_x span.gsc_g_t'))
                                         .map(s => s.textContent.trim())
                                         .filter(y => /^\\d{4}$/.test(y));
                    // Years with bars are the LAST N year labels
                    // (Scholar only draws bars for non-zero years,
                    //  but always labels every year on the axis)
                    const yearsWithBars = allYears.slice(allYears.length - bars.length);
                    bars.forEach((bar, i) => {
                        const alSpan = bar.querySelector('span.gsc_g_al');
                        const cnt    = alSpan
                            ? parseInt(alSpan.textContent.trim(), 10)
                            : parseInt(bar.getAttribute('title') || '0', 10);
                        if (yearsWithBars[i]) result[yearsWithBars[i]] = cnt;
                    });
                }

                return result;
            }
        """)
        print(f"  Raw histogram from live DOM: {js_year_data}")

        html = page.content()
        browser.close()

    Path("_data").mkdir(parents=True, exist_ok=True)
    Path("_data/scholar_debug.html").write_text(html, encoding="utf-8")

    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser"), js_year_data


# ── scrapers ──────────────────────────────────────────────────────────────────

def scrape_summary(soup) -> dict:
    cells = soup.select("td.gsc_rsb_std")
    def iv(i):
        return int(cells[i].get_text(strip=True)) if i < len(cells) else 0
    return {
        "total":        iv(0),
        "since_2021":   iv(1),
        "h_index":      iv(2),
        "h_index_5y":   iv(3),
        "i10_index":    iv(4),
        "i10_index_5y": iv(5),
    }


def build_cites_per_year(js_year_data: dict, soup) -> dict:
    """
    Build cites_per_year for the last 3 years.

    Priority:
      1. JS left-px matched data from live DOM  (most accurate)
      2. HTML regex with length-mismatch fix:
         align count tags to the LAST N year tags (where N = len(counts))
    """
    result = {str(k): int(v) for k, v in js_year_data.items()} if js_year_data else {}

    if not result or all(v == 0 for v in result.values()):
        print("  JS extraction empty — trying HTML regex with alignment fix…")
        raw      = str(soup)
        yr_list  = re.findall(r'<span[^>]*class="gsc_g_t"[^>]*>(\d{4})</span>', raw)
        cnt_list = re.findall(r'<span[^>]*class="gsc_g_al"[^>]*>(\d+)</span>', raw)
        print(f"    year tags  ({len(yr_list)}): {yr_list}")
        print(f"    count tags ({len(cnt_list)}): {cnt_list}")

        if yr_list and cnt_list:
            # Scholar draws bars only for years with ≥1 citation.
            # The count tags align to the LAST len(cnt_list) year tags.
            aligned_years = yr_list[-len(cnt_list):]
            result = {yr: int(cnt) for yr, cnt in zip(aligned_years, cnt_list)}
            print(f"    Aligned result: {result}")
        else:
            print("  WARNING: No histogram data found at all.")
            print("  → Open _data/scholar_debug.html and search for 'gsc_g_a' to inspect.")

    # Trim to last 3 years, always include current year
    keep    = {str(CURRENT_YEAR - 2), str(CURRENT_YEAR - 1), str(CURRENT_YEAR)}
    trimmed = {yr: result.get(yr, 0) for yr in sorted(keep)}
    print(f"  Final cites_per_year (last 3 years): {trimmed}")
    return trimmed


def scrape_papers(soup) -> list:
    papers = []
    for row in soup.select("tr.gsc_a_tr"):
        title_tag  = row.select_one("a.gsc_a_at")
        title      = title_tag.get_text(strip=True) if title_tag else ""
        href       = title_tag.get("href", "") if title_tag else ""
        sid        = ""
        m = re.search(r"citation_for_view=([^&\"]+)", href)
        if m:
            sid = unquote(m.group(1))
        cites_tag  = row.select_one("a.gsc_a_ac")
        cites_text = cites_tag.get_text(strip=True) if cites_tag else ""
        cites      = int(cites_text) if cites_text.isdigit() else 0
        year_tag   = row.select_one("span.gsc_a_hc")
        year       = year_tag.get_text(strip=True) if year_tag else ""
        papers.append({"title": title, "year": year, "cites": cites, "scholar_id": sid})
    papers.sort(key=lambda p: p["cites"], reverse=True)
    return papers


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Fetching Google Scholar profile for: {SCHOLAR_ID}\n")

    soup, js_year_data = fetch_page()

    print("\nScraping summary indices…")
    summary = scrape_summary(soup)
    print(f"  total={summary['total']}  h={summary['h_index']}  i10={summary['i10_index']}")

    print("\nScraping papers…")
    papers = scrape_papers(soup)
    print(f"  {len(papers)} papers found")

    print("\nBuilding citations-per-year…")
    cites_per_year = build_cites_per_year(js_year_data, soup)

    data = {
        "scholar_id":     SCHOLAR_ID,
        "updated":        datetime.date.today().isoformat(),
        "total":          summary["total"],
        "since_2021":     summary["since_2021"],
        "h_index":        summary["h_index"],
        "h_index_5y":     summary["h_index_5y"],
        "i10_index":      summary["i10_index"],
        "i10_index_5y":   summary["i10_index_5y"],
        "cites_per_year": cites_per_year,
        "papers":         papers,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"\n✅  Written to {OUTPUT_PATH}")
    print(f"\nNext steps:")
    print(f"   git add _data/citations.json")
    print(f"   git commit -m 'chore: update scholar citations'")
    print(f"   git push")


if __name__ == "__main__":
    main()
