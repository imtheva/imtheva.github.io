#!/usr/bin/env python3
"""
_scripts/build_cv_pdf.py
Prints the current CV page (/cv/) to assets/pdf/Thayananthan_CV.pdf,
which is the file the CV page's download icon links to.

Usage (with the local server running in another Terminal tab:
       bundle exec jekyll serve):
    python3 _scripts/build_cv_pdf.py
    python3 _scripts/build_cv_pdf.py --url https://imtheva.github.io/cv/
"""
import argparse
import sys
from pathlib import Path

OUT = Path("assets/pdf/Thayananthan_CV.pdf")

# Hide site chrome so the PDF contains only the CV content
PRINT_CSS = """
  header, nav, footer, .navbar, #toc-sidebar, .toc-sidebar, nav#toc-sidebar,
  .back-to-top, #back-to-top, .social, .cv-download, a[title*="PDF"],
  .post-header .btn, .fa-file-pdf { display: none !important; }
  body { padding-top: 0 !important; background: #fff !important; }
  .container, .col-sm-9, .col-sm-10, .col-md-9 { max-width: 100% !important; flex: 0 0 100% !important; }
  a { color: inherit !important; text-decoration: none !important; }
  .card, section, .timeline-item { break-inside: avoid; }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:4000/cv/")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Run: python3 -m pip install --user playwright && python3 -m playwright install chromium")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 1400})
        try:
            resp = page.goto(args.url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            browser.close()
            sys.exit(f"❌ Could not open {args.url} — is `bundle exec jekyll serve` running?\n   {e}")
        if not resp or resp.status >= 400:
            browser.close()
            sys.exit(f"❌ {args.url} returned HTTP {resp.status if resp else '?'}")

        # Force light theme and expand any collapsed sections
        page.evaluate("""() => {
            document.documentElement.setAttribute('data-theme', 'light');
            document.querySelectorAll('.collapse').forEach(e => e.classList.add('show'));
            document.querySelectorAll('details').forEach(d => d.open = true);
        }""")
        page.add_style_tag(content=PRINT_CSS)
        page.emulate_media(media="print")
        page.wait_for_timeout(800)

        page.pdf(
            path=str(out),
            format="Letter",
            print_background=True,
            margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                "<div style='font-size:8px;width:100%;text-align:center;color:#666'>"
                "Thevathayarajh Thayananthan — CV · page <span class='pageNumber'></span>"
                " of <span class='totalPages'></span></div>"
            ),
        )
        browser.close()

    print(f"✅ Saved {out} ({out.stat().st_size // 1024} KB)")
    print("   Commit it:  git add assets/pdf/Thayananthan_CV.pdf && git commit -m 'Update CV PDF' && git push")


if __name__ == "__main__":
    main()
