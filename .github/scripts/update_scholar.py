from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os
import sys

def update_scholar_stats():
    try:
        # Enable proxy to avoid blocks
        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg)

        print("Fetching author data...")
        author = scholarly.search_author_id('MpKhKEUAAAAJ')
        author = scholarly.fill(author, sections=["publications"])  # Fetch all publications
        
        stats = {
            'citations': author.get('citedby', 0),
            'h_index': author.get('hindex', 0),
            'publications': len(author.get('publications', [])),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'recent_publications': []
        }

        publications = author.get('publications', [])
        publications.sort(key=lambda x: int(x.get('bib', {}).get('pub_year', '0')), reverse=True)

        for i, pub in enumerate(publications):
            try:
                filled_pub = scholarly.fill(pub)

                # Extract abstract with multiple fallback options
                abstract = (
                    filled_pub.get('bib', {}).get('abstract') or 
                    filled_pub.get('abstract') or 
                    filled_pub.get('summary') or 
                    "Abstract not available"
                )

                pub_data = {
                    'title': filled_pub['bib'].get('title', 'No title'),
                    'year': filled_pub['bib'].get('pub_year', 'Year Unknown'),
                    'citation': filled_pub['bib'].get('citation', 'Citation not available'),
                    'abstract': abstract,
                    'url': filled_pub.get('pub_url', '#'),
                    'authors': filled_pub['bib'].get('author', [])
                }

                # Debugging print
                print(f"\n✅ Processed: {pub_data['title']}")
                print(f"📌 Abstract: {abstract[:100]}..." if len(abstract) > 100 else f"📌 Abstract: {abstract}")

                stats['recent_publications'].append(pub_data)

            except Exception as pub_error:
                print(f"⚠️ Error processing publication {i+1}: {pub.get('bib', {}).get('title', 'Unknown Title')}")
                print(str(pub_error))

        # Save stats to a JSON file
        os.makedirs('assets/data', exist_ok=True)
        json_path = os.path.join(os.getcwd(), 'assets/data/scholar_stats.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print("\n✅ Successfully updated scholar stats and publications!")

    except Exception as e:
        print(f"❌ Error updating scholar stats: {str(e)}")
        raise e

if __name__ == "__main__":
    update_scholar_stats()
