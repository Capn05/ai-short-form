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

GENERIC_SELECTORS = [
    "[class*='review-item']",
    "[class*='review-card']",
    "[class*='review-tile']",
    "[class*='review-entry']",
    "[class*='testimonial-item']",
    "[class*='testimonial-card']",
]


def scrape_reviews(url: str) -> list[dict]:
    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Scroll to trigger lazy-loaded review widgets
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

        except PlaywrightTimeout:
            print(f"  [reviews] page load timed out")
        except Exception as e:
            print(f"  [reviews] failed: {e}")
        finally:
            browser.close()

    return reviews[:10]


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
