"""
Scrape product images from Bing Image Search.
Updates image_url column in the CSV.

Usage:
    python3 ml/scrape_images.py
"""
import re
import time
import pandas as pd
import requests

CSV_PATH = "backend/data/skincare_products_clean.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

CATEGORY_IMAGES = {
    "acne/pimples":  "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&fit=crop",
    "dark circles":  "https://images.unsplash.com/photo-1617897903246-719242758050?w=400&fit=crop",
    "dandruff":      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&fit=crop",
    "dark spots":    "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&fit=crop",
    "blackheads":    "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&fit=crop",
    "default":       "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&fit=crop",
}


def fetch_image(product_name: str, brand: str) -> str | None:
    query = f"{brand} {product_name} product"
    try:
        r = requests.get(
            "https://www.bing.com/images/search",
            params={"q": query, "form": "HDRSC2"},
            headers=HEADERS,
            timeout=8,
        )
        urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', r.text)
        # Filter out SVGs and tiny images
        for url in urls:
            if not url.endswith(".svg") and "logo" not in url.lower():
                return url
    except Exception as e:
        print(f"  Error: {e}")
    return None


def main():
    df = pd.read_csv(CSV_PATH)
    if "image_url" not in df.columns:
        df["image_url"] = None
    df["image_url"] = df["image_url"].astype(object)

    total = len(df)
    updated = 0

    for i, row in df.iterrows():
        name    = str(row["product_name"])
        brand   = str(row["brand"])
        concern = str(row.get("concern", "default")).strip().lower()

        existing = row.get("image_url")
        if existing and str(existing).strip() not in ("", "nan", "NaN"):
            print(f"[{i+1}/{total}] Skip: {name}")
            continue

        print(f"[{i+1}/{total}] {name} ...", end=" ", flush=True)

        url = fetch_image(name, brand) or CATEGORY_IMAGES.get(concern, CATEGORY_IMAGES["default"])
        df.at[i, "image_url"] = url
        updated += 1
        print(f"✓ {url[:80]}")
        time.sleep(0.5)

    df.to_csv(CSV_PATH, index=False)
    print(f"\nDone. {updated}/{total} updated → {CSV_PATH}")


if __name__ == "__main__":
    main()
