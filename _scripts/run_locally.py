#!/usr/bin/env python3
"""
_scripts/run_locally.py
─────────────────────────────────────────────────────────────────────
Run this script on YOUR OWN MACHINE to update citations.
Your personal IP is not blocked by Google Scholar.

Usage:
    pip install scholarly
    python _scripts/run_locally.py

Then commit and push the result:
    git add _data/citations.json
    git commit -m "chore: update scholar citations"
    git push
─────────────────────────────────────────────────────────────────────
"""

import json
import datetime
from pathlib import Path

SCHOLAR_ID   = "MpKhKEUAAAAJ"
OUTPUT_PATH  = Path("_data/citations.json")
CURRENT_YEAR = str(datetime.date.today().year)


def main():
    from scholarly import scholarly

    print(f"Fetching Google Scholar profile: {SCHOLAR_ID}")
    print("(Running on your local machine — no IP blocking)")

    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    cites_per_year = {
        str(k): v for k, v in author.get("cites_per_year", {}).items()
    }
    if CURRENT_YEAR not in cites_per_year:
        cites_per_year[CURRENT_YEAR] = 0
    cites_per_year = dict(sorted(cites_per_year.items()))

    papers = sorted(
        [
            {
                "title":      p["bib"].get("title", ""),
                "year":       p["bib"].get("pub_year", ""),
                "cites":      int(p.get("num_citations", 0)),
                "scholar_id": p.get("author_pub_id", ""),
            }
            for p in author.get("publications", [])
        ],
        key=lambda x: x["cites"],
        reverse=True,
    )

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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"\n✅ Written to {OUTPUT_PATH}")
    print(f"   total={data['total']}  h={data['h_index']}  i10={data['i10_index']}")
    print(f"   years={list(data['cites_per_year'].keys())}")
    print(f"   papers={len(papers)}")
    print(f"\nNow run:")
    print(f"   git add _data/citations.json")
    print(f"   git commit -m 'chore: update scholar citations'")
    print(f"   git push")


if __name__ == "__main__":
    main()
