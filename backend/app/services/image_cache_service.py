"""
On-demand product image fetcher with in-memory cache.
Used as fallback when CSV doesn't have image_url populated yet.
"""
import logging
import threading

import requests

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}
_lock = threading.Lock()

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0"}
FALLBACK = "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"


def get_product_image(product_url: str) -> str:
    """Return cached image URL, fetching from product page if not cached."""
    if not product_url:
        return FALLBACK

    with _lock:
        if product_url in _cache:
            return _cache[product_url]

    try:
        from bs4 import BeautifulSoup
        r = requests.get(product_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                img_url = og["content"]
                with _lock:
                    _cache[product_url] = img_url
                return img_url
    except Exception as e:
        logger.debug("Image fetch failed for %s: %s", product_url, e)

    with _lock:
        _cache[product_url] = FALLBACK
    return FALLBACK
