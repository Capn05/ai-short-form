import re
import json
import uuid
import requests
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from pipeline.scraper.reviews import scrape_reviews


def scrape(url: str, output_base: Path, skip_reviews: bool = False) -> dict:
    run_id = uuid.uuid4().hex[:8]
    run_dir = output_base / "runs" / run_id
    images_dir = run_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"[scraper] run_id={run_id}")
    print(f"[scraper] fetching product JSON...")

    base_url, handle = _parse_url(url)
    product_data = _fetch_product_json(base_url, handle)

    if not product_data:
        raise ValueError(
            f"Could not fetch product data from {url}. "
            "Confirm this is a valid Shopify product URL."
        )

    product = product_data.get("product", {})

    name = product.get("title", "")
    price = _extract_price(product)
    description_html = product.get("body_html", "") or ""
    description_text = _html_to_text(description_html)
    bullet_points = _extract_bullet_points(description_html)
    image_urls = [img["src"] for img in product.get("images", []) if img.get("src")]

    print(f"[scraper] product: {name}")
    print(f"[scraper] downloading {len(image_urls)} images...")
    local_images = _download_images(image_urls, images_dir)

    print(f"[scraper] scraping reviews...")
    reviews = scrape_reviews(url) if not skip_reviews else []
    if skip_reviews:
        print(f"[scraper] reviews skipped (--skip-reviews)")

    result = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "url": url,
        "product_name": name,
        "price": price,
        "description": description_text,
        "bullet_points": bullet_points,
        "reviews": reviews,
        "has_reviews": len(reviews) > 0,
        "review_count": len(reviews),
        "images": local_images,
        "image_count": len(local_images),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }

    output_path = run_dir / "product.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[scraper] wrote {output_path}")
    return result


def _parse_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rstrip("/")
    parts = path.split("/")

    try:
        products_idx = parts.index("products")
        handle = parts[products_idx + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Could not extract product handle from URL: {url}")

    return base_url, handle


def _fetch_product_json(base_url: str, handle: str) -> dict | None:
    json_url = f"{base_url}/products/{handle}.json"
    try:
        resp = requests.get(
            json_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if resp.status_code == 200:
            return resp.json()
        print(f"[scraper] JSON endpoint returned {resp.status_code}")
        return None
    except Exception as e:
        print(f"[scraper] JSON endpoint failed: {e}")
        return None


def _extract_price(product: dict) -> str:
    variants = product.get("variants", [])
    if variants:
        price = variants[0].get("price", "")
        if price:
            return f"${price}"
    return ""


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _extract_bullet_points(html: str) -> list[str]:
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")

    items = [li.get_text(strip=True) for li in soup.find_all("li") if len(li.get_text(strip=True)) > 5]

    if not items:
        text = soup.get_text(separator=" ", strip=True)
        sentences = re.split(r"[.!?]+", text)
        items = [s.strip() for s in sentences if len(s.strip()) > 20][:6]

    return items


def _download_images(image_urls: list[str], images_dir: Path) -> list[str]:
    local_paths = []
    for i, url in enumerate(image_urls):
        try:
            clean_url = url.split("?")[0]
            ext = Path(clean_url).suffix or ".jpg"
            filepath = images_dir / f"img_{i:02d}{ext}"
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                filepath.write_bytes(resp.content)
                local_paths.append(str(filepath))
        except Exception as e:
            print(f"[scraper] warning: failed to download image {i}: {e}")
    return local_paths
