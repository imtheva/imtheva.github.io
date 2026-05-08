#!/usr/bin/env python3
"""
_scripts/update_citations.py
Fetches Google Scholar data and writes _data/citations.json.
Run by GitHub Actions every Sunday. Also run manually anytime.
"""

import json, datetime
from pathlib import Path

SCHOLAR_ID  = "MpKhKEUAAAAJ"
OUTPUT_PATH = Path("_data/citations.json")

def main():
    from scholarly import scholarly
    print(f"Fetching Scholar profile: {SCHOLAR_ID}")

    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    # Build per-year dict from Scholar
    cites_per_year = {str(k): v for k, v in author.get("cites_per_year", {}).items()}

    # ── Always include the current year, even if Scholar hasn't
    #    recorded any citations yet (Scholar lags by a few weeks)
    current_year = str(datetime.date.today().year)
    if current_year not in cites_per_year:
        cites_per_year[current_year] = 0

    # Sort by year ascending
    cites_per_year = dict(sorted(cites_per_year.items()))

    papers = sorted([
        {
            "title":      p["bib"].get("title", ""),
            "year":       p["bib"].get("pub_year", ""),
            "cites":      int(p.get("num_citations", 0)),
            "scholar_id": p.get("author_pub_id", ""),
        }
        for p in author.get("publications", [])
    ], key=lambda x: x["cites"], reverse=True)

    data = {
        "scholar_id":     SCHOLAR_ID,
        "updated":        datetime.date.today().isoformat(),
        "total":          int(author.get("citedby",    0)),
        "since_2021":     int(author.get("citedby5y",  0)),
        "h_index":        int(author.get("hindex",     0)),
        "h_index_5y":     int(author.get("hindex5y",   0)),
        "i10_index":      int(author.get("i10index",   0)),
        "i10_index_5y":   int(author.get("i10index5y", 0)),
        "cites_per_year": cites_per_year,
        "papers":         papers,
    }

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Done. total={data['total']}, h={data['h_index']}, years={list(cites_per_year.keys())}")

if __name__ == "__main__":
    main()
