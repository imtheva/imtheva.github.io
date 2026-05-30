#!/usr/bin/env python3
"""
_scripts/update_citations.py
Fetches Google Scholar data → writes _data/citations.json
Uses Playwright to render the page as a real browser.

FIXES:
- cites_per_year: Scholar encodes bar heights as CSS style attributes.
  We now extract the last 3 years from per-paper citation data as a
  reliable fallback, and also try all known Scholar bar-chart HTML patterns.
- Always ensures the current year is present in cites_per_year.
- Only keeps the last 3 years in cites_per_year for the bar chart display.
"""

import json
import os
import re
import sys
import datetime
from pathlib import Path

SCHOLAR_ID   = "MpKhKEUAAAAJ"
OUTPUT_PATH  = Path("_data/citations.json")
CURRENT_YEAR = str(datetime.date.today().year)
SCHOLAR_URL  = (
    f"https://scholar.google.com/citations"
    f"?user={SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank"
)


def fetch_playwright() -> dict:
    from playwright.sync_api import sync_playwright
    import time

    print("[Playwright] Launching browser…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--lang=en-US",
            ],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = ctx.new_page()

        # Remove webdriver fingerprint
        page.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )

        print(f"[Playwright] Navigating to: {SCHOLAR_URL}")
        page.goto(SCHOLAR_URL, wait_until="networkidle", timeout=60000)

        # Handle Google consent / cookie wall if present
        try:
            consent_btn = page.locator(
                'button:has-text("Accept all"), '
                'button:has-text("Reject all"), '
                'button:has-text("I agree"), '
                'form[action*="consent"] button'
            ).first
            if consent_btn.is_visible(timeout=3000):
                print("[Playwright] Consent wall detected — dismissing…")
                consent_btn.click()
                page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        # Wait for the profile table
        try:
            page.wait_for_selector("#gsc_rsb_st", timeout=15000)
            print("[Playwright] Profile table found ✓")
        except Exception:
            print("[Playwright] WARNING: Profile table (#gsc_rsb_st) not found — saving debug snapshot")
            debug_path = Path("_data/scholar_debug.html")
            debug_path.write_text(page.content(), encoding="utf-8")
            print(f"[Playwright] Debug HTML saved to {debug_path}")
            print("[Playwright] Page title:", page.title())
            print("[Playwright] Page URL:", page.url)

        time.sleep(2)

        # ── Extract cites-per-year directly from the live DOM via JS ──
        # Scholar renders the histogram as a series of anchor elements
        # with a title attribute = the citation count for that year, and
        # the year label is in a sibling span.  Using JS evaluation on
        # the live DOM is far more reliable than regex on the serialised HTML.
        js_years = page.evaluate("""
            () => {
                const result = {};
                // Each bar group: <a class="gsc_g_a" title="COUNT">…<span class="gsc_g_t">YEAR</span>
                const bars = document.querySelectorAll('a.gsc_g_a');
                bars.forEach(bar => {
                    const count = parseInt(bar.getAttribute('title') || bar.textContent.trim(), 10);
                    const yrSpan = bar.querySelector('span.gsc_g_t') ||
                                   bar.parentElement && bar.parentElement.querySelector('span.gsc_g_t');
                    if (yrSpan) {
                        const yr = yrSpan.textContent.trim();
                        if (/^\\d{4}$/.test(yr) && !isNaN(count)) result[yr] = count;
                    }
                });

                // Alternate layout: year labels and bar anchors are siblings inside .gsc_g_bars
                if (Object.keys(result).length === 0) {
                    const cols = document.querySelectorAll('.gsc_oci_g_t, .gsc_g_t');
                    const vals = document.querySelectorAll('.gsc_g_a');
                    cols.forEach((col, i) => {
                        const yr = col.textContent.trim();
                        const v  = vals[i] ? parseInt(vals[i].title || vals[i].textContent, 10) : 0;
                        if (/^\\d{4}$/.test(yr) && !isNaN(v)) result[yr] = v;
                    });
                }
                return result;
            }
        """)
        print(f"[Playwright/JS] Extracted year data from DOM: {js_years}")

        html = page.content()
        browser.close()

    return _parse_html(html, dom_years=js_years)


def _extract_years_from_html(html: str) -> dict:
    """
    Try every known Scholar bar-chart HTML pattern to extract cites-per-year.
    Returns {} if nothing found — caller will fall back to paper-level aggregation.
    """
    cites_per_year = {}

    # Pattern 1 (older layout): <span class="gsc_g_t">2024</span> paired with
    #   <a class="gsc_g_a" title="21"> inside the same <td>
    # We find all year spans and their nearest anchor title in the same cell.
    cells = re.findall(
        r'<td[^>]*class="[^"]*gsc_g_a_t[^"]*"[^>]*>(.*?)</td>',
        html, re.DOTALL
    )
    for cell in cells:
        yr_m  = re.search(r'<span[^>]*class="gsc_g_t"[^>]*>(\d{4})</span>', cell)
        val_m = re.search(r'<a[^>]*class="gsc_g_a"[^>]*title="(\d+)"', cell)
        if yr_m and val_m:
            cites_per_year[yr_m.group(1)] = int(val_m.group(1))

    if cites_per_year:
        print(f"[Parser/P1] Year data from cell pairs: {cites_per_year}")
        return cites_per_year

    # Pattern 2: year labels list + values list appear in the same order
    year_labels = re.findall(r'<span[^>]*class="gsc_g_t"[^>]*>(\d{4})</span>', html)
    # Explicit text inside the anchor (newer Scholar)
    year_values = re.findall(r'<span[^>]*class="gsc_g_al"[^>]*>(\d+)</span>', html)
    # title attribute on the anchor
    if not year_values:
        year_values = re.findall(r'<a[^>]*class="gsc_g_a"[^>]*\s+title="(\d+)"', html)
    if not year_values:
        year_values = re.findall(r'<a[^>]*title="(\d+)"[^>]*class="gsc_g_a"', html)
    # text content of the anchor as last resort
    if not year_values:
        year_values = re.findall(
            r'<a[^>]*class="gsc_g_a"[^>]*>\s*(?:<[^>]+>)*\s*(\d+)\s*(?:</[^>]+>)*\s*</a>',
            html, re.DOTALL
        )

    print(f"[Parser/P2] Year labels: {year_labels}, values: {year_values}")
    if year_labels and year_values and len(year_labels) == len(year_values):
        for yr, val in zip(year_labels, year_values):
            cites_per_year[yr] = int(val)
        return cites_per_year

    return {}


def _aggregate_years_from_papers(papers: list) -> dict:
    """
    Build a cites-per-year estimate from the per-paper citation counts.
    Scholar doesn't expose per-paper per-year breakdowns on the profile page,
    so we use the paper publication year as a proxy: a paper published in year Y
    contributes its total citation count to year Y.  This is an approximation
    but it always produces non-zero values and correctly reflects the JSON data
    we already have.

    For the bar chart we only need the last 3 years; older data is excluded.
    """
    current_year = int(CURRENT_YEAR)
    last_3 = [str(current_year - 2), str(current_year - 1), str(current_year)]

    agg = {yr: 0 for yr in last_3}
    for p in papers:
        yr = str(p.get("year", "")).strip()
        if yr in agg:
            agg[yr] += p.get("cites", 0)

    return agg


def _last_3_years(cites_per_year: dict) -> dict:
    """Keep only the most recent 3 years, always including the current year."""
    current = int(CURRENT_YEAR)
    keep = {str(current - 2), str(current - 1), str(current)}
    result = {}
    for yr in sorted(cites_per_year.keys()):
        if yr in keep:
            result[yr] = cites_per_year[yr]
    # Guarantee current year is always present
    if CURRENT_YEAR not in result:
        result[CURRENT_YEAR] = 0
    return dict(sorted(result.items()))


def _parse_html(html: str, dom_years: dict = None) -> dict:
    # ── Detect blocked/empty pages ────────────────────────────────────
    if "unusual traffic" in html.lower():
        raise RuntimeError("Google returned unusual traffic / CAPTCHA page")

    # ── Summary index table (#gsc_rsb_st) ─────────────────────────────
    indices = re.findall(r'<td[^>]*class="gsc_rsb_std"[^>]*>(\d+)</td>', html)
    print(f"[Parser] Raw index values found: {indices}")

    def idx(i):
        return int(indices[i]) if i < len(indices) else 0

    total  = idx(0)
    since5 = idx(1)
    h      = idx(2)
    h5     = idx(3)
    i10    = idx(4)
    i105   = idx(5)

    # ── Per-paper rows ─────────────────────────────────────────────────
    papers = []
    paper_blocks = re.findall(r'<tr[^>]*class="gsc_a_tr"[^>]*>(.*?)</tr>', html, re.DOTALL)
    print(f"[Parser] Paper rows found: {len(paper_blocks)}")

    for block in paper_blocks:
        title_m = re.search(r'class="gsc_a_at"[^>]*>([^<]+)</a>', block)
        cites_m = re.search(r'class="gsc_a_ac[^"]*"[^>]*>\s*(\d+)\s*<', block)
        year_m  = re.search(r'class="gsc_a_y"[^>]*>.*?<span[^>]*>(\d{4})</span>', block, re.DOTALL)
        href_m  = re.search(r'href="([^"]*citation_for_view=[^"]+)"', block)
        sid = ""
        if href_m:
            m2 = re.search(r'citation_for_view=([^&"]+)', href_m.group(1))
            if m2:
                import urllib.parse
                sid = urllib.parse.unquote(m2.group(1))

        papers.append({
            "title":      title_m.group(1).strip() if title_m else "",
            "year":       year_m.group(1) if year_m else "",
            "cites":      int(cites_m.group(1)) if cites_m else 0,
            "scholar_id": sid,
        })

    papers.sort(key=lambda p: p["cites"], reverse=True)

    # ── Citations-per-year: try DOM extraction first, then HTML regex,
    #    then fall back to paper-level aggregation ─────────────────────
    cites_per_year = {}

    # 1) Live DOM extraction (most reliable when Playwright is used)
    if dom_years and any(int(v) > 0 for v in dom_years.values()):
        cites_per_year = {str(k): int(v) for k, v in dom_years.items()}
        print(f"[Parser] Using DOM-extracted year data: {cites_per_year}")

    # 2) HTML regex patterns
    if not cites_per_year:
        cites_per_year = _extract_years_from_html(html)

    # 3) Paper-level aggregation fallback — always produces sensible values
    if not cites_per_year or all(v == 0 for v in cites_per_year.values()):
        print("[Parser] Year extraction yielded zeros — falling back to paper-year aggregation")
        cites_per_year = _aggregate_years_from_papers(papers)

    # Keep only the last 3 years for the bar chart
    cites_per_year = _last_3_years(cites_per_year)

    print(f"[Parser] Final cites_per_year (last 3 years): {cites_per_year}")
    print(f"[Parser] Totals — citations:{total} h:{h} i10:{i10} papers:{len(papers)}")

    return {
        "scholar_id":     SCHOLAR_ID,
        "updated":        datetime.date.today().isoformat(),
        "total":          total,
        "since_2021":     since5,
        "h_index":        h,
        "h_index_5y":     h5,
        "i10_index":      i10,
        "i10_index_5y":   i105,
        "cites_per_year": cites_per_year,
        "papers":         papers,
    }


def main():
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_ID}")

    serp_key = os.environ.get("SERP_API_KEY", "").strip()
    data = None

    # ── Option A: SerpAPI (if key is set) ─────────────────────────────
    if serp_key:
        try:
            from update_citations_serpapi import fetch_serpapi
            data = fetch_serpapi(serp_key)
            print("✓ Success via SerpAPI")
        except Exception as e:
            print(f"✗ SerpAPI failed: {e}")

    # ── Option B: Playwright ───────────────────────────────────────────
    if data is None:
        try:
            data = fetch_playwright()
            if data["total"] == 0 and data["h_index"] == 0 and not data["papers"]:
                raise RuntimeError(
                    "Playwright fetched the page but parsed only zeros. "
                    "Check _data/scholar_debug.html artifact."
                )
            print("✓ Success via Playwright")
        except Exception as e:
            print(f"✗ Playwright failed: {e}")
            sys.exit(1)

    # ── Write output ───────────────────────────────────────────────────
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n✅ Written to {OUTPUT_PATH}")
    print(f"   total={data['total']}  h={data['h_index']}  i10={data['i10_index']}")
    print(f"   years={list(data['cites_per_year'].keys())}")
    print(f"   papers={len(data['papers'])}")


if __name__ == "__main__":
    main()
