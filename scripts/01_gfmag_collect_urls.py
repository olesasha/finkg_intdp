import argparse
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

MAX_PAGES = 100  #safety break
BASE_URL = "https://gfmag.com"

def collect_category_urls(
    category_path,
    out_csv,
    max_articles,
    sleep_time=1,
):
    seen = set()
    rows = []

    for page in range(1, MAX_PAGES + 1):
        if page == 1:
            url = urljoin(BASE_URL, category_path)
        else:
            url = urljoin(BASE_URL, f"{category_path}/page/{page}/")

        print(f"Fetching archive page {page}: {url}")

        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 404:
            print("404 – no more pages.")
            break
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        article_links = []
        for h in soup.find_all(["h2", "h3"]):
            a = h.find("a", href=True)
            if not a:
                continue

            href = a["href"]
            full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
            article_links.append(full_url)

        if not article_links:
            print("No article links found on this page; stopping.")
            break

        for full_url in article_links:
            if full_url not in seen:
                seen.add(full_url)
                rows.append({"Url": full_url})

        print(
            f"  collected {len(article_links)} links "
            f"(total unique: {len(seen)})"
        )

        if len(seen) >= max_articles:
            break

        time.sleep(sleep_time)

    df = pd.DataFrame(rows)
    df["Mark"] = 0
    df["Text"] = ""
    df["Date"] = ""
    df.to_csv(out_csv, index=False)

    print(f"\nSaved {len(df)} unique article URLs to {out_csv}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape GFMag category archive pages for article URLs"
    )
    parser.add_argument(
        "--category-path",  "--category_path", #rename python-friendly
        default="/category/banking",
        help="Category path to scrape",
    )
    parser.add_argument(
        "--out-csv","--out_csv",
        default="gfmag_urls.csv",
        help="Output CSV file",
    )
    parser.add_argument(
        "--max-articles","--max_articles",
        type=int,
        default=1000,
        help="Maximum number of articles to collect"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    collect_category_urls(
        category_path=args.category_path,
        out_csv=args.out_csv,
        max_articles=args.max_articles
    )

#python 01_gfmag_collect_urls.py \
#  --category-path /category/banking \
#  --out-csv gfmag_banking_1000_urls.csv \
#  --max-articles 1000 