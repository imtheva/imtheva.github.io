#!/usr/bin/env python3
"""
_scripts/update_citations.py
Fetches Google Scholar data → writes _data/citations.json
Uses Playwright to render the page as a real browser.
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
            # EU consent button — click "Accept all" or "Reject all" (either works)
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
            pass  # No consent wall — fine

        # Wait for the profile table to actually appear
        try:
            page.wait_for_selector("#gsc_rsb_st", timeout=15000)
            print("[Playwright] Profile table found ✓")
        except Exception:
            print("[Playwright] WARNING: Profile table (#gsc_rsb_st) not found — saving debug snapshot")
            # Save HTML snapshot as an artifact for inspection
            debug_path = Path("_data/scholar_debug.html")
            debug_path.write_text(page.content(), encoding="utf-8")
            print(f"[Playwright] Debug HTML saved to {debug_path}")
            print("[Playwright] Page title:", page.title())
            print("[Playwright] Page URL:", page.url)

        time.sleep(2)
        html = page.content()
        browser.close()

    # ── Parse the page ────────────────────────────────────────────────
    return _parse_html(html)


def _parse_html(html: str) -> dict:
    # ── Detect blocked/empty pages ────────────────────────────────────
    if "unusual traffic" in html.lower():
        raise RuntimeError("Google returned unusual traffic / CAPTCHA page")

    # ── Summary index table (#gsc_rsb_st) ─────────────────────────────
    # Row order: Citations | h-index | i10-index
    # Col order: All time  | Since 2021
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
        # Title
        title_m = re.search(r'class="gsc_a_at"[^>]*>([^<]+)</a>', block)
        # Citations — the count link inside gsc_a_ac
        cites_m = re.search(r'class="gsc_a_ac[^"]*"[^>]*>\s*(\d+)\s*<', block)
        # Year
        year_m  = re.search(r'class="gsc_a_y"[^>]*>.*?<span[^>]*>(\d{4})</span>', block, re.DOTALL)
        # Scholar ID from href
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

    # ── Citations-per-year histogram ───────────────────────────────────
    # Scholar renders these as a bar chart with labels in gsc_g_t
    # and values encoded in the bar height style OR as text in gsc_g_al
    year_labels = re.findall(r'<span[^>]*class="gsc_g_t"[^>]*>(\d{4})</span>', html)
    # Try the text-in-span approach first (newer Scholar layout)
    year_values = re.findall(r'<span[^>]*class="gsc_g_al"[^>]*>(\d+)</span>', html)
    # Fall back: extract from anchor title attributes
    if not year_values:
        year_values = re.findall(r'<a[^>]*class="gsc_g_a"[^>]*title="(\d+)"', html)
    # Fall back further: extract numbers from the gsc_g_a anchors
    if not year_values:
        year_values = re.findall(r'<a[^>]*class="gsc_g_a"[^>]*>.*?(\d+).*?</a>', html, re.DOTALL)

    print(f"[Parser] Year labels: {year_labels}")
    print(f"[Parser] Year values: {year_values}")

    cites_per_year = {}
    for yr, val in zip(year_labels, year_values):
        cites_per_year[yr] = int(val)

    # Always include current year
    if CURRENT_YEAR not in cites_per_year:
        cites_per_year[CURRENT_YEAR] = 0
    cites_per_year = dict(sorted(cites_per_year.items()))

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

    # ── Option B: Playwright (always available, no key needed) ─────────
    if data is None:
        try:
            data = fetch_playwright()
            # Validate — if we got zeros for everything, the parse failed
            if data["total"] == 0 and data["h_index"] == 0 and not data["papers"]:
                raise RuntimeError(
                    "Playwright fetched the page but parsed only zeros. "
                    "Check _data/scholar_debug.html artifact to see what Scholar returned."
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
