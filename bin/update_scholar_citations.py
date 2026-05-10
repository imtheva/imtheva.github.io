#!/usr/bin/env python

import json
import os
import sys
import yaml
from datetime import datetime
from scholarly import scholarly


def load_scholar_user_id() -> str:
    """Load the Google Scholar user ID from the configuration file."""
    config_file = "_data/socials.yml"
    if not os.path.exists(config_file):
        print(
            f"Configuration file {config_file} not found. Please ensure the file exists and contains your Google Scholar user ID."
        )
        sys.exit(1)
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        scholar_user_id = config.get("scholar_userid")
        if not scholar_user_id:
            print(
                "No 'scholar_userid' found in the configuration file. Please add 'scholar_userid' to _data/socials.yml."
            )
            sys.exit(1)
        return scholar_user_id
    except yaml.YAMLError as e:
        print(
            f"Error parsing YAML file {config_file}: {e}. Please check the file for correct YAML syntax."
        )
        sys.exit(1)


SCHOLAR_USER_ID: str = load_scholar_user_id()
OUTPUT_YML: str = "_data/citations.yml"
OUTPUT_JSON: str = "_data/citations.json"


def get_scholar_citations() -> None:
    """Fetch and update Google Scholar citation data."""
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_USER_ID}")
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if the output file was already updated today
    existing_data = None
    if os.path.exists(OUTPUT_YML):
        try:
            with open(OUTPUT_YML, "r") as f:
                existing_data = yaml.safe_load(f)
            if (
                existing_data
                and "metadata" in existing_data
                and "last_updated" in existing_data["metadata"]
            ):
                print(f"Last updated on: {existing_data['metadata']['last_updated']}")
                if existing_data["metadata"]["last_updated"] == today:
                    print("Citations data is already up-to-date. Skipping fetch.")
                    return
        except Exception as e:
            print(
                f"Warning: Could not read existing citation data from {OUTPUT_YML}: {e}. The file may be missing or corrupted."
            )

    citation_data = {"metadata": {"last_updated": today}, "papers": {}}

    scholarly.set_timeout(15)
    scholarly.set_retries(3)

    # ── Fetch author data (publications + author-level stats) ──────────────
    try:
        print("Fetching author profile and publications...")
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        author_data = scholarly.fill(author)
    except Exception as e:
        print(
            f"Error fetching author data from Google Scholar for user ID '{SCHOLAR_USER_ID}': {e}."
        )
        sys.exit(1)

    if not author_data:
        print(f"Could not fetch author data for user ID '{SCHOLAR_USER_ID}'.")
        sys.exit(1)

    if "publications" not in author_data:
        print(f"No publications found in author data for user ID '{SCHOLAR_USER_ID}'.")
        sys.exit(1)

    # ── Extract per-paper citations ────────────────────────────────────────
    for pub in author_data["publications"]:
        try:
            pub_id = pub.get("author_pub_id") or pub.get("pub_id")
            if not pub_id:
                print(
                    f"Warning: No ID found for publication: {pub.get('bib', {}).get('title', 'Unknown')}. Skipping."
                )
                continue

            title = pub.get("bib", {}).get("title", "Unknown Title")
            year = pub.get("bib", {}).get("pub_year", "Unknown Year")
            citations = pub.get("num_citations", 0)

            print(f"Found: {title} ({year}) - Citations: {citations}")

            citation_data["papers"][pub_id] = {
                "title": title,
                "year": year,
                "citations": citations,
            }
        except Exception as e:
            print(
                f"Error processing publication '{pub.get('bib', {}).get('title', 'Unknown')}': {e}. Skipping."
            )

    # ── Extract author-level stats ─────────────────────────────────────────
    total        = author_data.get("citedby",    0) or 0
    total_5y     = author_data.get("citedby5y",  0) or 0
    h_index      = author_data.get("hindex",     0) or 0
    h_index_5y   = author_data.get("hindex5y",   0) or 0
    i10_index    = author_data.get("i10index",   0) or 0
    i10_index_5y = author_data.get("i10index5y", 0) or 0
    cites_per_year = author_data.get("cites_per_year", {}) or {}

    print(f"\nAuthor stats:")
    print(f"  Total citations : {total}")
    print(f"  Since 5y        : {total_5y}")
    print(f"  h-index         : {h_index}")
    print(f"  i10-index       : {i10_index}")
    print(f"  Cites per year  : {cites_per_year}")

    # ── Compare with existing data — skip write if unchanged ───────────────
    if existing_data and existing_data.get("papers") == citation_data["papers"]:
        print("No changes in citation data. Skipping file update.")
        return

    # ── Write citations.yml (per-paper, existing format) ──────────────────
    try:
        with open(OUTPUT_YML, "w") as f:
            yaml.dump(citation_data, f, width=1000, sort_keys=True)
        print(f"\nCitation YAML saved to {OUTPUT_YML}")
    except Exception as e:
        print(f"Error writing {OUTPUT_YML}: {e}.")
        sys.exit(1)

    # ── Write citations.json (dashboard format) ────────────────────────────
    papers_list = [
        {
            "scholar_id": pub_id,
            "title": p["title"],
            "year": p["year"],
            "cites": p["citations"],
        }
        for pub_id, p in sorted(
            citation_data["papers"].items(),
            key=lambda x: x[1]["citations"],
            reverse=True,
        )
    ]

    json_data = {
        "scholar_id": SCHOLAR_USER_ID,
        "updated": today,
        "total": total,
        "since_2021": total_5y,
        "h_index": h_index,
        "h_index_5y": h_index_5y,
        "i10_index": i10_index,
        "i10_index_5y": i10_index_5y,
        "cites_per_year": cites_per_year,
        "papers": papers_list,
    }

    try:
        with open(OUTPUT_JSON, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"Citation JSON saved to {OUTPUT_JSON}")
    except Exception as e:
        print(f"Error writing {OUTPUT_JSON}: {e}.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
