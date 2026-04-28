import re

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# App-specific selector configs — tried in order
REVIEW_APP_CONFIGS = [
    {
        "name": "judge_me",
        "container": ".jdgm-rev",
        "body": ".jdgm-rev__body",
        "author": ".jdgm-rev__author",
        "rating_attr_selector": "[data-score]",
        "rating_attr": "data-score",
    },
    {
        "name": "yotpo",
        "container": ".yotpo-review",
        "body": ".content-review",
        "author": ".yotpo-user-name",
        "rating_attr_selector": None,
        "rating_attr": None,
    },
    {
        "name": "okendo",
        "container": ".oke-review",
        "body": ".oke-review-body-text, .oke-w-review-comment",
        "author": ".oke-w-reviewer-name",
        "rating_attr_selector": None,
        "rating_attr": None,
    },
    {
        "name": "loox",
        "container": "[class*='loox-review']",
        "body": "[class*='loox-review-text'], [class*='loox-review-body']",
        "author": "[class*='loox-author']",
        "rating_attr_selector": None,
        "rating_attr": None,
    },
    {
        "name": "stamped",
        "container": ".stamped-review",
        "body": ".stamped-review-content-body",
        "author": ".author",
        "rating_attr_selector": None,
        "rating_attr": None,
    },
    {
        "name": "shopify_native",
        "container": ".spr-review",
        "body": ".spr-review-content-body",
        "author": ".spr-review-header-byline strong",
        "rating_attr_selector": None,
        "rating_attr": None,
    },
]

DESCRIPTION_SELECTORS = [
    ".product__description",
    ".product-description",
    ".product-single__description",
    "[class*='product-description']",
    ".product__info-container .rte",
    ".product-info .rte",
    ".product__content .rte",
    "#product-description",
    "[data-product-description]",
]

GENERIC_SELECTORS = [
    "[class*='review-item']",
    "[class*='review-card']",
    "[class*='review-tile']",
    "[class*='review-entry']",
    "[class*='testimonial-item']",
    "[class*='testimonial-card']",
]


def scrape_page_content(url: str, skip_reviews: bool = False) -> dict:
    """Returns rendered description text, reviews, and hero video URL in a single browser session."""
    description = ""
    reviews = []
    video_url = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            description = _extract_description(page)
            video_url = _extract_video_url(page)

            if not skip_reviews:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
                page.wait_for_timeout(1500)

                detected_app = None
                for config in REVIEW_APP_CONFIGS:
                    containers = page.query_selector_all(config["container"])
                    if containers:
                        detected_app = config["name"]
                        reviews = _extract_with_config(page, config)
                        if reviews:
                            break

                if not reviews:
                    reviews = _extract_generic(page)

                if detected_app:
                    print(f"  [reviews] app detected: {detected_app}, found {len(reviews)}")
                elif reviews:
                    print(f"  [reviews] generic fallback, found {len(reviews)}")
                else:
                    print(f"  [reviews] none found")
            else:
                print(f"  [reviews] skipped (--skip-reviews)")

        except PlaywrightTimeout:
            print(f"  [scraper] page load timed out")
        except Exception as e:
            print(f"  [scraper] page scrape failed: {e}")
        finally:
            browser.close()

    return {"description": description, "reviews": reviews[:10], "video_url": video_url}


def _extract_with_config(page, config: dict) -> list[dict]:
    reviews = []
    containers = page.query_selector_all(config["container"])

    for container in containers[:10]:
        try:
            text = ""
            author = ""
            rating = None

            body_el = container.query_selector(config["body"])
            if body_el:
                text = body_el.inner_text().strip()

            author_el = container.query_selector(config["author"])
            if author_el:
                author = author_el.inner_text().strip()

            if config.get("rating_attr_selector") and config.get("rating_attr"):
                rating_el = container.query_selector(config["rating_attr_selector"])
                if rating_el:
                    try:
                        rating = int(float(rating_el.get_attribute(config["rating_attr"])))
                    except (TypeError, ValueError):
                        rating = None

            if text and len(text) > 15:
                reviews.append({"text": text, "author": author, "rating": rating})

        except Exception:
            continue

    return reviews


def _extract_video_url(page) -> str | None:
    srcs = page.eval_on_selector_all(
        "video", "els => els.map(e => e.currentSrc).filter(s => s && s.endsWith('.mp4') || s.includes('.mp4?'))"
    )
    if not srcs:
        return None
    counts = {}
    for s in srcs:
        counts[s] = counts.get(s, 0) + 1
    url = max(counts, key=counts.__getitem__)
    print(f"  [scraper] product video found ({counts[url]}x): {url[:80]}...")
    return url


def _extract_description(page) -> str:
    for selector in DESCRIPTION_SELECTORS:
        try:
            el = page.query_selector(selector)
            if el:
                text = _clean_text(el.inner_text())
                if len(text) > 100:
                    return text
        except Exception:
            continue
    return ""


def _clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _extract_generic(page) -> list[dict]:
    reviews = []

    for selector in GENERIC_SELECTORS:
        try:
            containers = page.query_selector_all(selector)
            if not containers:
                continue

            for container in containers[:10]:
                try:
                    text = container.inner_text().strip()
                    if 30 < len(text) < 2000:
                        reviews.append({"text": text, "author": "", "rating": None})
                except Exception:
                    continue

            if reviews:
                break
        except Exception:
            continue

    return reviews
