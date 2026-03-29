"""
Fetch real product images from LookFantastic product pages.
Reads data/skincare_products_clean.csv, adds image_url column, saves result.

Usage: python3 ml/fetch_product_images.py

Fetches in batches with rate limiting to avoid being blocked.
Skips rows that already have an image_url.
"""
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

INPUT_CSV  = "data/skincare_products_clean.csv"
OUTPUT_CSV = "data/skincare_products_clean.csv"
HEADERS    = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0"}
DELAY      = 0.8   # seconds between requests
BATCH_SAVE = 50    # save progress every N rows


def fetch_og_image(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        og = soup.find("meta", property="og:image")
        return og["content"] if og else None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} products from {INPUT_CSV}")

    if "image_url" not in df.columns:
        df["image_url"] = None

    todo = df[df["image_url"].isna() | (df["image_url"] == "")].index
    print(f"Need to fetch images for {len(todo)} products")

    for count, i in enumerate(todo, 1):
        url = str(df.at[i, "product_url"])
        name = str(df.at[i, "product_name"])[:50]
        print(f"[{count}/{len(todo)}] {name}")

        img = fetch_og_image(url)
        df.at[i, "image_url"] = img or ""
        print(f"  -> {img or 'not found'}")

        if count % BATCH_SAVE == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"  [Saved progress at {count}]")

        time.sleep(DELAY)

    df.to_csv(OUTPUT_CSV, index=False)
    filled = df["image_url"].notna() & (df["image_url"] != "")
    print(f"\nDone. {filled.sum()}/{len(df)} products have images.")
    print(f"Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
