import feedparser
import pandas as pd

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import time

BASE = "https://gfmag.com"
CATEGORY_PATH = "/category/banking"  # [web:1]
OUT_CSV = "gfmag_banking_1000_urls.csv"
MAX_ARTICLES = 1000
MAX_PAGES = 100  # safety cap

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def collect_category_urls():
    seen = set()
    rows = []

    for page in range(1, MAX_PAGES + 1):
        if page == 1:
            url = urljoin(BASE, CATEGORY_PATH)
        else:
            url = urljoin(BASE, f"{CATEGORY_PATH}/page/{page}/")

        print(f"Fetching archive page {page}: {url}")
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 404:
            print("  404 – no more pages.")
            break
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # Typical WordPress pattern: post titles in <h2> or <h3> with <a>
        article_links = []
        for h in soup.find_all(["h2", "h3"]):
            a = h.find("a", href=True)
            if not a:
                continue
            href = a["href"]
            if href.startswith("http"):
                full = href
            else:
                full = urljoin(BASE, href)
            article_links.append(full)

        if not article_links:
            print("  No article links found on this page; stopping.")
            break

        for full in article_links:
            if full not in seen:
                seen.add(full)
                rows.append({"Url": full})

        print(f"  collected {len(article_links)} links (total unique: {len(seen)})")

        if len(seen) >= MAX_ARTICLES:
            break

        time.sleep(1.0)  # polite delay

    df = pd.DataFrame(rows)
    df["Mark"] = 0
    df["Text"] = ""
    df["Date"] = ""
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} unique article URLs to {OUT_CSV}")

if __name__ == "__main__":
    collect_category_urls()
