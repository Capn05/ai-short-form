import base64
import json
import subprocess
import uuid
import requests
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from openai import OpenAI

from pipeline.scraper.reviews import scrape_page_content


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
    description_fallback = _html_to_text(description_html)
    image_urls = [img["src"] for img in product.get("images", []) if img.get("src")]

    print(f"[scraper] product: {name}")
    print(f"[scraper] downloading {len(image_urls)} images...")
    local_images = _download_images(image_urls, images_dir)

    print(f"[scraper] loading rendered page...")
    page_content = scrape_page_content(url, skip_reviews=skip_reviews)
    description_text = page_content["description"] or description_fallback
    reviews = page_content["reviews"]

    local_video = _download_video(page_content.get("video_url"), run_dir)

    if len(description_text) < 800:
        print(f"[scraper] thin description ({len(description_text)} chars) — extracting features from images...")
        image_features = _extract_image_features(name, description_text, local_images)
        if image_features:
            description_text = description_text + "\n\n" + image_features
            print(f"  [scraper] appended image-extracted features to description")
    else:
        print(f"[scraper] description sufficient ({len(description_text)} chars) — skipping image extraction")

    result = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "url": url,
        "product_name": name,
        "price": price,
        "description": description_text,
        "reviews": reviews,
        "has_reviews": len(reviews) > 0,
        "review_count": len(reviews),
        "images": local_images,
        "image_count": len(local_images),
        "video": local_video,
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


def _download_video(video_url: str | None, run_dir: Path, duration: int = 15) -> str | None:
    if not video_url:
        return None
    try:
        print(f"[scraper] downloading product video (first {duration}s)...")
        raw_path = run_dir / "product_video_raw.mp4"
        trimmed_path = run_dir / "product_video.mp4"

        resp = requests.get(video_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        raw_path.write_bytes(resp.content)

        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_path), "-t", str(duration), "-c", "copy", str(trimmed_path)],
            capture_output=True,
        )
        raw_path.unlink(missing_ok=True)

        if result.returncode != 0 or not trimmed_path.exists():
            print(f"  [scraper] video trim failed, skipping")
            return None

        print(f"  [scraper] saved → {trimmed_path.name}")
        return str(trimmed_path)
    except Exception as e:
        print(f"  [scraper] video download failed: {e}")
        return None


def _extract_image_features(product_name: str, description: str, image_paths: list[str]) -> str:
    if not image_paths:
        return ""
    try:
        content = [
            {
                "type": "text",
                "text": (
                    f"Product: {product_name}\n\n"
                    f"Existing text description: {description[:400]}\n\n"
                    "The images below are product photos. Some may be infographics or diagrams with text callouts "
                    "explaining features, specs, or how the product works. Extract any useful product information "
                    "visible in the images that is NOT already covered in the text description above — things like "
                    "how the product is used, key features, materials, capacity, safety info, or physical mechanics. "
                    "Return only the extracted information as plain sentences. If nothing new is visible beyond the "
                    "text description, return an empty string."
                ),
            }
        ]

        SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
        loaded = 0
        for path_str in image_paths[:8]:
            path = Path(path_str)
            ext = path.suffix.lower()
            if ext not in SUPPORTED:
                continue
            try:
                raw = path.read_bytes()
                if raw[:3] == b"\xff\xd8\xff":
                    media_type = "image/jpeg"
                elif raw[:8] == b"\x89PNG\r\n\x1a\n":
                    media_type = "image/png"
                else:
                    media_type = MEDIA_TYPES.get(ext, "image/jpeg")
                data = base64.standard_b64encode(raw).decode("utf-8")
                content.append({"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{data}"}})
                loaded += 1
            except Exception:
                continue

        if not loaded:
            return ""

        client = OpenAI(max_retries=5)
        response = client.chat.completions.create(
            model="gpt-5.4",
            max_completion_tokens=400,
            messages=[{"role": "user", "content": content}],
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        print(f"  [scraper] image feature extraction failed: {e}")
        return ""


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
