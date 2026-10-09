"""Check that every page shares the same header, footer, call bar and contact band.

The site has no build step, so these parts are copied into each page by hand.
Run from the repository root before opening a pull request:

    python3 _tools/check_pages.py

It prints any page whose shared parts differ from the home page, and exits 1 if
any do. The only expected difference is which menu link is marked as the
current page. A page that isn't in the menu (Sample documents) marks nothing.
"""
import re, sys, pathlib

PAGES = ["index.html", "services/index.html", "your-information/index.html",
         "cmmc-status/index.html", "questions/index.html", "sample-documents/index.html"]
PARTS = {
    "header": (r'<header class="site-header">', r"</header>"),
    "contact band": (r'<section class="contact" id="contact"', r"</section>"),
    "footer": (r'<footer class="site-footer">', r"</footer>"),
    "call bar": (r'<aside class="callbar"', r"</aside>"),
}

def part(html, start, end):
    a = html.find(start)
    if a < 0:
        return None
    b = html.find(end, a) + len(end)
    return re.sub(r' aria-current="page"', "", html[a:b])

root = pathlib.Path(".")
base = (root / PAGES[0]).read_text(encoding="utf-8")
bad = 0
for page in PAGES:
    html = (root / page).read_text(encoding="utf-8")
    if 'style="' in html:
        print(f"{page}: has a style attribute (the CSP blocks these)"); bad += 1
    for name, (start, end) in PARTS.items():
        if part(html, start, end) != part(base, start, end):
            print(f"{page}: {name} differs from index.html"); bad += 1
    current = re.findall(r'href="([^"]+)" aria-current="page"', html)
    want = "/" + page.replace("index.html", "")
    in_menu = f'href="{want}"' in (part(html, *PARTS["header"]) or "")
    expected = {want} if (want != "/" and in_menu) else set()
    if want != "/" and set(current) != expected:
        print(f"{page}: menu marks {current or 'nothing'} as current, expected {sorted(expected) or 'nothing'}"); bad += 1
print("OK: shared parts match on all pages" if not bad else f"{bad} problem(s)")
sys.exit(1 if bad else 0)
