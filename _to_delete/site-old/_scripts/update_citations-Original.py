#!/usr/bin/env python3
"""
update_citations.py
-------------------
Scrapes Google Scholar for citation metrics and per-paper counts,
then writes them to _data/citations.json for use by Jekyll/Liquid.

Usage:
    python _scripts/update_citations.py

Dependencies (already in al-folio's requirements.txt, or install manually):
    pip install scholarly requests
"""

import json
import os
import time
import datetime
from pathlib import Path

SCHOLAR_ID = "MpKhKEUAAAAJ"
OUTPUT_PATH = Path("_data/citations.json")

# ---------------------------------------------------------------------------
# Try scholarly first (best data), fall back to a minimal scraped approach
# ---------------------------------------------------------------------------

def fetch_via_scholarly():
    """Use the `scholarly` library to pull full profile + per-paper data."""
    from scholarly import scholarly, ProxyGenerator

    # Optional: use a free proxy to avoid rate-limiting on CI
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)

    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    total     = int(author.get("citedby", 0))
    since5    = int(author.get("citedby5y", 0))
    hindex    = int(author.get("hindex", 0))
    hindex5   = int(author.get("hindex5y", 0))
    i10index  = int(author.get("i10index", 0))
    i10index5 = int(author.get("i10index5y", 0))

    cites_per_year = author.get("cites_per_year", {})

    papers = []
    for pub in author.get("publications", []):
        papers.append({
            "title":  pub["bib"].get("title", ""),
            "year":   pub["bib"].get("pub_year", ""),
            "cites":  int(pub.get("num_citations", 0)),
            "scholar_id": pub.get("author_pub_id", ""),
        })

    # Sort descending by cites
    papers.sort(key=lambda p: p["cites"], reverse=True)

    return {
        "scholar_id":       SCHOLAR_ID,
        "updated":          datetime.date.today().isoformat(),
        "total":            total,
        "since_2021":       since5,
        "h_index":          hindex,
        "h_index_5y":       hindex5,
        "i10_index":        i10index,
        "i10_index_5y":     i10index5,
        "cites_per_year":   {str(k): v for k, v in cites_per_year.items()},
        "papers":           papers,
    }


def fetch_minimal_fallback():
    """
    Minimal fallback: fetches the public scholar page HTML and parses
    the summary table only (no per-paper breakdown).
    Use only if `scholarly` is unavailable.
    """
    import re
    import urllib.request

    url = (
        f"https://scholar.google.com/citations"
        f"?user={SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    req  = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # Parse summary indices table (#gsc_rsb_st)
    indices  = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    # Order: Citations-All, Citations-Since5y, h-All, h-5y, i10-All, i10-5y
    def idx(i):
        return int(indices[i]) if i < len(indices) else 0

    # Parse per-paper rows
    papers = []
    for m in re.finditer(
        r'<tr class="gsc_a_tr">.*?<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
        r'.*?<td class="gsc_a_c"><a[^>]*>(\d*)</a>',
        html, re.DOTALL
    ):
        href, title, cites = m.group(1), m.group(2), m.group(3)
        year_m = re.search(r'<td class="gsc_a_y"><span[^>]*>(\d+)</span>', m.group(0))
        papers.append({
            "title":      title.strip(),
            "year":       year_m.group(1) if year_m else "",
            "cites":      int(cites) if cites else 0,
            "scholar_id": href.split("citation_for_view=")[-1] if "citation_for_view=" in href else "",
        })

    papers.sort(key=lambda p: p["cites"], reverse=True)

    return {
        "scholar_id":     SCHOLAR_ID,
        "updated":        datetime.date.today().isoformat(),
        "total":          idx(0),
        "since_2021":     idx(1),
        "h_index":        idx(2),
        "h_index_5y":     idx(3),
        "i10_index":      idx(4),
        "i10_index_5y":   idx(5),
        "cites_per_year": {},
        "papers":         papers,
    }


def main():
    print(f"[update_citations] Fetching data for Scholar ID: {SCHOLAR_ID}")

    data = None
    try:
        import scholarly  # noqa: F401
        print("[update_citations] Using `scholarly` library …")
        data = fetch_via_scholarly()
    except ImportError:
        print("[update_citations] `scholarly` not installed — using HTML fallback …")
        data = fetch_minimal_fallback()
    except Exception as exc:
        print(f"[update_citations] scholarly failed ({exc}) — using HTML fallback …")
        data = fetch_minimal_fallback()

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    print(f"[update_citations] Wrote {OUTPUT_PATH}")
    print(f"  total={data['total']}  h={data['h_index']}  i10={data['i10_index']}")
    print(f"  papers found: {len(data.get('papers', []))}")


if __name__ == "__main__":
    main()
