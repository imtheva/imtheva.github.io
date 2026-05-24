#!/usr/bin/env python3
"""
_scripts/update_citations.py
─────────────────────────────────────────────────────────────────────
Fetches Google Scholar data → writes _data/citations.json

TWO STRATEGIES — pick whichever suits you:

  OPTION A: SerpAPI (recommended — free, no credit card, 100 req/mo)
  ─────────────────────────────────────────────────────────────────
  1. Go to https://serpapi.com/users/sign_up
  2. Create a free account (email only, no card needed)
  3. Copy your API key from https://serpapi.com/manage-api-key
  4. GitHub repo → Settings → Secrets → Actions → New secret
       Name:  SERP_API_KEY
       Value: <your key>
  You use ~4 requests/month. Free tier gives 100. Never runs out.

  OPTION B: Playwright browser (zero signup, zero keys, slower)
  ─────────────────────────────────────────────────────────────────
  Launches a real Chromium browser in the Actions runner, navigates
  to your Scholar profile, and extracts the data from the rendered
  HTML. Slower (~60s) but needs no API key at all.
  Set USE_PLAYWRIGHT=true in the workflow env to activate.
─────────────────────────────────────────────────────────────────────
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
SCHOLAR_URL  = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank"


# ─────────────────────────────────────────────────────────────────────
# OPTION A — SerpAPI (free, no credit card)
# https://serpapi.com/google-scholar-author-api
# ─────────────────────────────────────────────────────────────────────
def fetch_serpapi(api_key: str) -> dict:
    import urllib.request
    import urllib.parse

    print("[SerpAPI] Fetching author profile…")
    params = urllib.parse.urlencode({
        "engine":    "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key":   api_key,
        "hl":        "en",
        "num":       "100",
    })
    url = f"https://serpapi.com/search.json?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        raw = json.loads(resp.read().decode())

    if "error" in raw:
        raise RuntimeError(f"SerpAPI error: {raw['error']}")

    author = raw.get("author", {})
    cited_by = raw.get("cited_by", {})
    table = cited_by.get("table", [])

    def _tbl(key):
        for row in table:
            if key in row:
                return int(row[key].get("all", 0))
        return 0

    # Citations per year from the graph data
    graph = cited_by.get("graph", [])
    cites_per_year = {str(g["year"]): g["citations"] for g in graph if "year" in g}

    # Papers
    papers_raw = raw.get("articles", [])
    papers = sorted(
        [
            {
                "title":      p.get("title", ""),
                "year":       str(p.get("year", "")),
                "cites":      int(p.get("cited_by", {}).get("value", 0)),
                "scholar_id": p.get("citation_id", ""),
            }
            for p in papers_raw
        ],
        key=lambda x: x["cites"],
        reverse=True,
    )

    return _build(
        total  = _tbl("citations"),
        since5 = _tbl("citations") if not table else int(table[0].get("citations", {}).get("since_2021", _tbl("citations"))),
        h      = _tbl("h_index"),
        h5     = _tbl("h_index"),
        i10    = _tbl("i10_index"),
        i105   = _tbl("i10_index"),
        cites_per_year = cites_per_year,
        papers = papers,
    )


# ─────────────────────────────────────────────────────────────────────
# OPTION B — Playwright (zero signup, real browser, no keys needed)
# ─────────────────────────────────────────────────────────────────────
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
                "--disable-blink-features=AutomationControlled",
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
        )
        page = ctx.new_page()

        # Remove webdriver flag
        page.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )

        print(f"[Playwright] Navigating to Scholar profile…")
        page.goto(SCHOLAR_URL, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        html = page.content()
        browser.close()

    if "unusual traffic" in html.lower() or "captcha" in html.lower():
        raise RuntimeError("Scholar returned a CAPTCHA page — try again later")

    return _parse_html(html)


# ─────────────────────────────────────────────────────────────────────
# HTML parser (used by Playwright result)
# ─────────────────────────────────────────────────────────────────────
def _parse_html(html: str) -> dict:
    # Summary index table — order: Citations-All, Citations-5y, h-All, h-5y, i10-All, i10-5y
    indices = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    def idx(i): return int(indices[i]) if i < len(indices) else 0

    # Per-paper rows
    papers = []
    for block in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.DOTALL):
        title_m = re.search(r'class="gsc_a_at"[^>]*>([^<]+)</a>', block)
        cites_m = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)<', block)
        year_m  = re.search(r'class="gsc_a_y"[^>]*><span[^>]*>(\d{4})</span>', block)
        href_m  = re.search(r'href="(/citations\?[^"]*citation_for_view=[^"]+)"', block)
        sid = ""
        if href_m:
            m2 = re.search(r'citation_for_view=([^&"]+)', href_m.group(1))
            if m2:
                import urllib.parse
                sid = urllib.parse.unquote(m2.group(1))
        papers.append({
            "title":      title_m.group(1).strip() if title_m else "",
            "year":       year_m.group(1) if year_m else "",
            "cites":      int(cites_m.group(1)) if cites_m and cites_m.group(1) else 0,
            "scholar_id": sid,
        })
    papers.sort(key=lambda p: p["cites"], reverse=True)

    # Year histogram — labels in gsc_g_t, values in gsc_g_a
    year_labels = re.findall(r'<span class="gsc_g_t"[^>]*>(\d{4})</span>', html)
    year_values = re.findall(r'<span class="gsc_g_al">(\d+)</span>', html)
    cites_per_year = {}
    for yr, val in zip(year_labels, year_values):
        cites_per_year[yr] = int(val)

    return _build(idx(0), idx(1), idx(2), idx(3), idx(4), idx(5), cites_per_year, papers)


# ─────────────────────────────────────────────────────────────────────
# Build final data dict
# ─────────────────────────────────────────────────────────────────────
def _build(total, since5, h, h5, i10, i105, cites_per_year, papers) -> dict:
    if CURRENT_YEAR not in cites_per_year:
        cites_per_year[CURRENT_YEAR] = 0
    cites_per_year = dict(sorted(cites_per_year.items()))
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


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def main():
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_ID}")

    serp_key     = os.environ.get("SERP_API_KEY", "").strip()
    use_playwright = os.environ.get("USE_PLAYWRIGHT", "").lower() in ("1", "true", "yes")

    data   = None
    errors = []

    # ── SerpAPI ───────────────────────────────────────────────────────
    if serp_key:
        try:
            data = fetch_serpapi(serp_key)
            print("✓ Success via SerpAPI")
        except Exception as e:
            errors.append(f"SerpAPI: {e}")
            print(f"✗ SerpAPI failed: {e}")
    else:
        print("SerpAPI skipped — SERP_API_KEY not set")

    # ── Playwright ────────────────────────────────────────────────────
    if data is None and use_playwright:
        try:
            data = fetch_playwright()
            print("✓ Success via Playwright")
        except Exception as e:
            errors.append(f"Playwright: {e}")
            print(f"✗ Playwright failed: {e}")
    elif data is None and not use_playwright:
        print("Playwright skipped — set USE_PLAYWRIGHT=true in workflow to enable")

    # ── All failed ────────────────────────────────────────────────────
    if data is None:
        print("\n❌ Failed to fetch citation data.")
        for e in errors:
            print(f"   • {e}")
        print("""
Choose one of these options and update your workflow:

  OPTION A (easiest — free, no card):
    1. Sign up at https://serpapi.com/users/sign_up  (email only)
    2. Get your key from https://serpapi.com/manage-api-key
    3. Add GitHub secret: SERP_API_KEY = <your key>

  OPTION B (zero signup):
    Set USE_PLAYWRIGHT=true in the workflow env section.
    (already installed in the workflow — just flip the flag)
""")
        sys.exit(1)

    # ── Write output ──────────────────────────────────────────────────
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n✅ Written to {OUTPUT_PATH}")
    print(f"   total={data['total']}  h={data['h_index']}  i10={data['i10_index']}")
    print(f"   years={list(data['cites_per_year'].keys())}")
    print(f"   papers={len(data['papers'])}")


if __name__ == "__main__":
    main()
