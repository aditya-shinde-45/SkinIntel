"""Build an image dataset for skin/hair concerns using Bing image crawl."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import random
import shutil
import time
from pathlib import Path

from icrawler.builtin import BingImageCrawler
from PIL import Image, UnidentifiedImageError


# Multiple query variants improve diversity for each class.
CONDITION_QUERIES: dict[str, list[str]] = {
    "acne_pimples": [
        "acne vulgaris face close up",
        "pimples on face skin condition",
        "facial acne dermatology photo",
        "acne skin texture real photo",
    ],
    "dark_circles": [
        "dark circles under eyes close up",
        "under eye pigmentation photo",
        "periorbital dark circles face",
        "dark under eye circles dermatology",
    ],
    "dandruff": [
        "dandruff scalp flakes close up",
        "seborrheic scalp dandruff photo",
        "hair scalp dandruff condition",
        "dandruff on scalp real image",
    ],
    "hyperpigmentation_dark_spots": [
        "facial hyperpigmentation dark spots",
        "melasma dark spots face close up",
        "uneven skin tone dark marks",
        "hyperpigmentation cheeks forehead photo",
    ],
    "blackheads_whiteheads": [
        "blackheads whiteheads on nose close up",
        "comedonal acne blackheads whiteheads",
        "whiteheads blackheads skin texture",
        "open closed comedones face photo",
    ],
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape image dataset per condition")
    parser.add_argument(
        "--output-dir",
        default="dataset/concerns",
        help="Directory where class folders will be created",
    )
    parser.add_argument(
        "--per-class",
        type=int,
        default=600,
        help="Number of images to save per class (recommended 500-800)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=224,
        help="Minimum width/height required for an image",
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=400,
        help="Maximum search results to request per query",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between image downloads",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for URL shuffling",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in value).strip("_").lower()


def validate_and_convert(image_bytes: bytes, min_size: int) -> bytes | None:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()

        if image.width < min_size or image.height < min_size:
            return None

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        elif image.mode == "RGBA":
            image = image.convert("RGB")

        out = io.BytesIO()
        image.save(out, format="JPEG", quality=92)
        return out.getvalue()
    except (UnidentifiedImageError, OSError):
        return None


def crawl_query_images(query: str, temp_dir: Path, max_per_query: int) -> None:
    temp_dir.mkdir(parents=True, exist_ok=True)
    storage = {"root_dir": str(temp_dir)}
    crawler = BingImageCrawler(
        feeder_threads=1,
        parser_threads=1,
        downloader_threads=4,
        storage=storage,
    )
    crawler.crawl(
        keyword=query,
        max_num=max_per_query,
        min_size=None,
        max_size=None,
        file_idx_offset=0,
    )


def save_metadata_row(metadata_path: Path, row: dict[str, str | int]) -> None:
    file_exists = metadata_path.exists()
    with metadata_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "class_name", "query", "source_url"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def scrape_class(
    class_name: str,
    queries: list[str],
    output_dir: Path,
    per_class: int,
    min_size: int,
    max_per_query: int,
    delay: float,
) -> None:
    class_dir = output_dir / class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = class_dir / "metadata.csv"
    raw_root = class_dir / "_raw"
    raw_root.mkdir(parents=True, exist_ok=True)

    existing_count = len(list(class_dir.glob("*.jpg")))
    if existing_count >= per_class:
        print(f"[SKIP] {class_name}: already has {existing_count} images")
        return

    print(f"\n[CLASS] {class_name}")
    saved = existing_count

    for query in queries:
        if saved >= per_class:
            break

        query_dir = raw_root / slugify(query)
        if query_dir.exists():
            shutil.rmtree(query_dir)

        print(f"[STEP] Crawling query: {query}")
        try:
            crawl_query_images(query=query, temp_dir=query_dir, max_per_query=max_per_query)
        except Exception as exc:
            print(f"[WARN] Query crawl failed: {exc}")
            continue

        raw_images = list(query_dir.glob("**/*"))
        random.shuffle(raw_images)

        for raw_file in raw_images:
            if saved >= per_class:
                break
            if not raw_file.is_file():
                continue

            try:
                content = raw_file.read_bytes()
            except OSError:
                continue

            jpeg = validate_and_convert(content, min_size=min_size)
            if jpeg is None:
                continue

            digest = hashlib.sha1(jpeg).hexdigest()[:16]
            file_name = f"{class_name}_{saved + 1:04d}_{digest}.jpg"
            file_path = class_dir / file_name
            if file_path.exists():
                continue

            file_path.write_bytes(jpeg)
            save_metadata_row(
                metadata_path,
                {
                    "file_name": file_name,
                    "class_name": class_name,
                    "query": query,
                    "source_url": str(raw_file),
                },
            )
            saved += 1

            if saved % 25 == 0:
                print(f"[INFO] {class_name}: saved {saved}/{per_class}")

            time.sleep(delay)

        shutil.rmtree(query_dir, ignore_errors=True)

    print(f"[DONE] {class_name}: saved {saved}/{per_class}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    random.seed(args.seed)

    print("Starting dataset scrape")
    print(f"Output directory: {output_dir.resolve()}")
    print(f"Target images per class: {args.per_class}")
    print(f"Running as UID {os.getuid()}")

    for class_name, queries in CONDITION_QUERIES.items():
        scrape_class(
            class_name=class_name,
            queries=queries,
            output_dir=output_dir,
            per_class=args.per_class,
            min_size=args.min_size,
            max_per_query=args.max_per_query,
            delay=args.delay,
        )

    print("\nAll classes finished.")


if __name__ == "__main__":
    main()
