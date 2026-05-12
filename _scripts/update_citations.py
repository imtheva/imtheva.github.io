# #!/usr/bin/env python3
# """
# _scripts/update_citations.py
# Fetches Google Scholar data and writes _data/citations.json.
# Run by GitHub Actions every Sunday. Also run manually anytime.
# """

# import json, datetime
# from pathlib import Path

# SCHOLAR_ID  = "MpKhKEUAAAAJ"
# OUTPUT_PATH = Path("_data/citations.json")

# def main():
#     from scholarly import scholarly
#     print(f"Fetching Scholar profile: {SCHOLAR_ID}")

#     author = scholarly.search_author_id(SCHOLAR_ID)
#     author = scholarly.fill(author, sections=["basics", "indices", "publications"])

#     # Build per-year dict from Scholar
#     cites_per_year = {str(k): v for k, v in author.get("cites_per_year", {}).items()}

#     # ── Always include the current year, even if Scholar hasn't
#     #    recorded any citations yet (Scholar lags by a few weeks)
#     current_year = str(datetime.date.today().year)
#     if current_year not in cites_per_year:
#         cites_per_year[current_year] = 0

#     # Sort by year ascending
#     cites_per_year = dict(sorted(cites_per_year.items()))

#     papers = sorted([
#         {
#             "title":      p["bib"].get("title", ""),
#             "year":       p["bib"].get("pub_year", ""),
#             "cites":      int(p.get("num_citations", 0)),
#             "scholar_id": p.get("author_pub_id", ""),
#         }
#         for p in author.get("publications", [])
#     ], key=lambda x: x["cites"], reverse=True)

#     data = {
#         "scholar_id":     SCHOLAR_ID,
#         "updated":        datetime.date.today().isoformat(),
#         "total":          int(author.get("citedby",    0)),
#         "since_2021":     int(author.get("citedby5y",  0)),
#         "h_index":        int(author.get("hindex",     0)),
#         "h_index_5y":     int(author.get("hindex5y",   0)),
#         "i10_index":      int(author.get("i10index",   0)),
#         "i10_index_5y":   int(author.get("i10index5y", 0)),
#         "cites_per_year": cites_per_year,
#         "papers":         papers,
#     }

#     OUTPUT_PATH.parent.mkdir(exist_ok=True)
#     OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
#     print(f"Done. total={data['total']}, h={data['h_index']}, years={list(cites_per_year.keys())}")

# if __name__ == "__main__":
#     main()
#!/usr/bin/env python3
"""
_scripts/update_citations.py
─────────────────────────────────────────────────────────────────────
Fetches Google Scholar data and writes _data/citations.json.
Run by GitHub Actions every Sunday (see .github/workflows/update_citations.yml).

WHY IT FAILS IN GITHUB ACTIONS:
  GitHub Actions runner IPs are shared and flagged by Google Scholar
  as bot traffic. scholarly raises "Cannot Fetch from Google Scholar"
  because the raw request is blocked immediately.

THREE STRATEGIES (tried in order, first success wins):
  1. ScraperAPI   — most reliable, free tier = 1,000 req/mo (plenty for weekly)
                    Set secret SCRAPER_API_KEY in your repo settings.
  2. FreeProxies  — scholarly's built-in free proxy pool (unreliable but free)
  3. Direct HTML  — raw urllib request with a browser User-Agent (last resort,
                    works if GitHub's IP happens not to be blocked that day)

SETUP FOR STRATEGY 1 (recommended):
  1. Sign up free at https://www.scraperapi.com  (no credit card needed)
  2. Copy your API key
  3. In GitHub repo → Settings → Secrets → Actions → New repository secret
     Name:  SCRAPER_API_KEY
     Value: your_key_here
  4. Done. The script reads it automatically from the environment.
─────────────────────────────────────────────────────────────────────
"""

import json
import os
import re
import sys
import time
import datetime
import urllib.request
import urllib.error
from pathlib import Path

SCHOLAR_ID  = "MpKhKEUAAAAJ"
OUTPUT_PATH = Path("_data/citations.json")
CURRENT_YEAR = str(datetime.date.today().year)


# ─────────────────────────────────────────────────────────────────────
# STRATEGY 1 — scholarly + ScraperAPI (most reliable)
# ─────────────────────────────────────────────────────────────────────
def fetch_with_scraperapi(api_key: str) -> dict:
    from scholarly import scholarly, ProxyGenerator
    print("[Strategy 1] Using ScraperAPI proxy…")
    pg = ProxyGenerator()
    success = pg.ScraperAPI(api_key)
    if not success:
        raise RuntimeError("ScraperAPI proxy setup failed — check your API key")
    scholarly.use_proxy(pg)
    return _fetch_scholarly()


# ─────────────────────────────────────────────────────────────────────
# STRATEGY 2 — scholarly + FreeProxies (unreliable but no key needed)
# ─────────────────────────────────────────────────────────────────────
def fetch_with_freeproxies() -> dict:
    from scholarly import scholarly, ProxyGenerator
    print("[Strategy 2] Using FreeProxies… (may be slow/unreliable)")
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    # Retry up to 3 times — free proxies are flaky
    for attempt in range(1, 4):
        try:
            return _fetch_scholarly()
        except Exception as e:
            print(f"  Attempt {attempt}/3 failed: {e}")
            if attempt < 3:
                time.sleep(5)
    raise RuntimeError("FreeProxies: all 3 attempts failed")


# ─────────────────────────────────────────────────────────────────────
# STRATEGY 3 — Direct HTML scrape (no scholarly, no proxy)
# ─────────────────────────────────────────────────────────────────────
def fetch_direct_html() -> dict:
    print("[Strategy 3] Direct HTML scrape (no proxy)…")
    url = (
        f"https://scholar.google.com/citations"
        f"?user={SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    if "unusual traffic" in html.lower() or "captcha" in html.lower():
        raise RuntimeError("Google Scholar returned a CAPTCHA/bot-detection page")

    # ── Summary indices table (#gsc_rsb_st) ──────────────────────────
    # Order in table: All | Since-5yr
    # Rows:           Citations | h-index | i10-index
    indices = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    def idx(i): return int(indices[i]) if i < len(indices) else 0

    # ── Per-paper rows ────────────────────────────────────────────────
    papers = []
    paper_blocks = re.findall(
        r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.DOTALL
    )
    for block in paper_blocks:
        title_m  = re.search(r'class="gsc_a_at"[^>]*>([^<]+)</a>', block)
        cites_m  = re.search(r'class="gsc_a_ac gs_ibl"[^>]*>(\d*)</a>', block)
        year_m   = re.search(r'class="gsc_a_y"[^>]*><span[^>]*>(\d{4})</span>', block)
        href_m   = re.search(r'href="(/citations\?[^"]*citation_for_view=[^"]+)"', block)
        scholar_id = ""
        if href_m:
            m2 = re.search(r'citation_for_view=([^&"]+)', href_m.group(1))
            if m2: scholar_id = urllib.parse.unquote(m2.group(1))
        papers.append({
            "title":      title_m.group(1).strip() if title_m else "",
            "year":       year_m.group(1)  if year_m  else "",
            "cites":      int(cites_m.group(1)) if cites_m and cites_m.group(1) else 0,
            "scholar_id": scholar_id,
        })

    # ── Citations-per-year graph data ─────────────────────────────────
    # Encoded as histogram bars in <a class="gsc_g_a" style="z-index:...">N</a>
    # Year labels are in <span class="gsc_g_t">YYYY</span>
    year_labels = re.findall(r'<span class="gsc_g_t"[^>]*>(\d{4})</span>', html)
    year_values = re.findall(r'<a class="gsc_g_a"[^>]*><span[^>]*>(\d+)</span></a>', html)
    cites_per_year = {}
    for yr, val in zip(year_labels, year_values):
        cites_per_year[yr] = int(val)

    papers.sort(key=lambda p: p["cites"], reverse=True)
    return _build_result(idx(0), idx(1), idx(2), idx(3), idx(4), idx(5),
                         cites_per_year, papers)


# ─────────────────────────────────────────────────────────────────────
# SHARED — scholarly data fetch (used by strategies 1 & 2)
# ─────────────────────────────────────────────────────────────────────
def _fetch_scholarly() -> dict:
    from scholarly import scholarly
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])
    cites_per_year = {str(k): v for k, v in author.get("cites_per_year", {}).items()}
    papers = sorted([
        {
            "title":      p["bib"].get("title", ""),
            "year":       p["bib"].get("pub_year", ""),
            "cites":      int(p.get("num_citations", 0)),
            "scholar_id": p.get("author_pub_id", ""),
        }
        for p in author.get("publications", [])
    ], key=lambda x: x["cites"], reverse=True)
    return _build_result(
        int(author.get("citedby",    0)),
        int(author.get("citedby5y",  0)),
        int(author.get("hindex",     0)),
        int(author.get("hindex5y",   0)),
        int(author.get("i10index",   0)),
        int(author.get("i10index5y", 0)),
        cites_per_year, papers
    )


def _build_result(total, since5, h, h5, i10, i105, cites_per_year, papers) -> dict:
    # Always include current year even if Scholar hasn't tallied it yet
    if CURRENT_YEAR not in cites_per_year:
        cites_per_year[CURRENT_YEAR] = 0
    # Sort years ascending for chart display
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
# MAIN — try each strategy in order
# ─────────────────────────────────────────────────────────────────────
def main():
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_ID}")
    data = None
    errors = []

    # Strategy 1: ScraperAPI (requires SCRAPER_API_KEY secret in GitHub)
    api_key = os.environ.get("SCRAPER_API_KEY", "").strip()
    if api_key:
        try:
            data = fetch_with_scraperapi(api_key)
            print("[Strategy 1] Success ✓")
        except Exception as e:
            errors.append(f"Strategy 1 (ScraperAPI): {e}")
            print(f"[Strategy 1] Failed: {e}")
    else:
        print("[Strategy 1] Skipped — SCRAPER_API_KEY secret not set")
        print("  → Add it: GitHub repo → Settings → Secrets → Actions → SCRAPER_API_KEY")

    # Strategy 2: FreeProxies
    if data is None:
        try:
            import scholarly  # noqa
            data = fetch_with_freeproxies()
            print("[Strategy 2] Success ✓")
        except Exception as e:
            errors.append(f"Strategy 2 (FreeProxies): {e}")
            print(f"[Strategy 2] Failed: {e}")

    # Strategy 3: Direct HTML
    if data is None:
        try:
            import urllib.parse  # noqa (ensure available)
            data = fetch_direct_html()
            print("[Strategy 3] Success ✓")
        except Exception as e:
            errors.append(f"Strategy 3 (Direct HTML): {e}")
            print(f"[Strategy 3] Failed: {e}")

    # All strategies failed
    if data is None:
        print("\n❌ All strategies failed:")
        for err in errors:
            print(f"   • {err}")
        print(
            "\n💡 Fix: Add a free ScraperAPI key as a GitHub secret:\n"
            "   1. Sign up free at https://www.scraperapi.com\n"
            "   2. Go to your repo → Settings → Secrets → Actions\n"
            "   3. Add secret: SCRAPER_API_KEY = <your key>\n"
            "   4. Re-run the workflow"
        )
        sys.exit(1)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n✅ Wrote {OUTPUT_PATH}")
    print(f"   total={data['total']}  h={data['h_index']}  i10={data['i10_index']}")
    print(f"   years={list(data['cites_per_year'].keys())}")
    print(f"   papers={len(data['papers'])}")


if __name__ == "__main__":
    main()
