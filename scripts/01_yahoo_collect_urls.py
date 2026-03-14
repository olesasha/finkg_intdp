import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm 

# Load tickers
tickers_df = pd.read_csv("tickerssp500.csv")
tickers = list(tickers_df["Symbol"].str.lower())

rss_base = "https://feeds.finance.yahoo.com/rss/2.0/headline"
headers = {"User-Agent": "Mozilla/5.0"}

all_links = set()

# Wrap tickers in tqdm to get a progress bar
for ticker in tqdm(tickers, desc="Fetching RSS feeds"):
    url = f"{rss_base}?s={ticker}&region=US&lang=en-US"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, "xml")
        for item in soup.find_all("item"):
            all_links.add(item.link.text)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

# Save results
df = pd.DataFrame(list(all_links), columns=["link"])
df.to_csv("yahoo_links.csv", index=False)
