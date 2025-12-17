import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

IN_CSV = "gfmag_trans_1000_urls.csv"
OUT_CSV = "SCRAPED_gfmag_trans_1000_urls.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

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
    """
    Try a few common patterns for WordPress/GFMag:
    - <time class="entry-date" datetime="...">
    - <time datetime="...">
    - date text near .posted-on or .meta
    Returns a string (ISO if possible) or "".
    """
    # 1) <time class="entry-date" datetime="...">
    time_el = soup.select_one("time.entry-date[datetime]")
    if time_el and time_el.has_attr("datetime"):
        return time_el["datetime"]

    # 2) any <time datetime="...">
    time_el = soup.find("time", attrs={"datetime": True})
    if time_el and time_el.has_attr("datetime"):
        return time_el["datetime"]

    # 3) fallback: plain text date in time element
    time_el = soup.find("time")
    if time_el and time_el.get_text(strip=True):
        return time_el.get_text(strip=True)

    # 4) last resort: look for a date in a meta block
    meta = soup.select_one(".post-meta, .entry-meta")
    if meta:
        txt = meta.get_text(" ", strip=True)
        return txt

    return ""

def scrape():
    df = pd.read_csv(IN_CSV)
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
        time.sleep(1.5)

    df["Text"] = texts
    df["Date"] = dates
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved scraped articles to {OUT_CSV}")

if __name__ == "__main__":
    scrape()
