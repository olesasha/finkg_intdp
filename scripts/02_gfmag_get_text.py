import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

DELAY_SEC = 1.5

def extract_article_text(soup: BeautifulSoup) -> str:
    for selector in [
        "div.entry-content",
        "article .entry-content",
        "article",
        "main",
    ]:
        el = soup.select_one(selector)
        if el and el.get_text(strip=True):
            text = "\n".join(
                t.strip() for t in el.stripped_strings
                if len(t.strip()) > 2
            )
            if len(text) > 500:
                return text
    return ""


def extract_article_date(soup: BeautifulSoup) -> str:
    # 1) <time class="entry-date" datetime="...">
    time_el = soup.select_one("time.entry-date[datetime]")
    if time_el and time_el.has_attr("datetime"):
        return time_el["datetime"]

    # 2) any <time datetime="...">
    time_el = soup.find("time", attrs={"datetime": True})
    if time_el and time_el.has_attr("datetime"):
        return time_el["datetime"]

    # 3) fallback: plain text <time>
    time_el = soup.find("time")
    if time_el and time_el.get_text(strip=True):
        return time_el.get_text(strip=True)

    # 4) last resort: meta block
    meta = soup.select_one(".post-meta, .entry-meta")
    if meta:
        return meta.get_text(" ", strip=True)

    return ""


def scrape(in_csv: str, out_csv: str):
    df = pd.read_csv(in_csv)

    texts = []
    dates = []

    for i, row in df.iterrows():
        url = row["Url"]
        print(f"[{i}] Fetching {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            text = extract_article_text(soup)
            date_str = extract_article_date(soup)

        except Exception as e:
            print("  Error:", e)
            text = ""
            date_str = ""

        texts.append(text)
        dates.append(date_str)
        time.sleep(DELAY_SEC)

    df["Text"] = texts
    df["Date"] = dates
    df.to_csv(out_csv, index=False)
    print(f"\nSaved scraped articles to {out_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape article text and dates from GFMag article URLs"
    )
    parser.add_argument(
        "--in-csv",
        required=True,
        help="Input CSV containing a column named 'Url'"
    )
    parser.add_argument(
        "--out-csv",
        required=True,
        help="Output CSV with scraped Text and Date columns"
    )

    args = parser.parse_args()
    scrape(args.in_csv, args.out_csv)

if __name__ == "__main__":
    main()
