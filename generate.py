import argparse
import json
import sys
from pathlib import Path

from pipeline.scraper.shopify import scrape


def main():
    parser = argparse.ArgumentParser(
        description="Generate UGC video ads from a Shopify product URL"
    )
    parser.add_argument("--url", required=True, help="Shopify product URL")
    parser.add_argument(
        "--output", default="output", help="Output directory (default: output/)"
    )
    parser.add_argument(
        "--skip-reviews", action="store_true",
        help="Skip Playwright review scraping (useful if browser deps not installed)"
    )
    args = parser.parse_args()

    output_base = Path(args.output)

    try:
        result = scrape(args.url, output_base, skip_reviews=args.skip_reviews)
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Stage 1 complete ---")
    print(f"Product:  {result['product_name']}")
    print(f"Price:    {result['price']}")
    print(f"Images:   {result['image_count']}")
    print(f"Reviews:  {result['review_count']}")
    print(f"Bullets:  {len(result['bullet_points'])}")
    print(f"Run dir:  {result['run_dir']}")
    print(f"JSON:     {result['run_dir']}/product.json")

    if not result["has_reviews"]:
        print(
            "\n⚠  No reviews found. Script quality will be weaker without real customer language."
            "\n   Consider providing 2–3 testimonials manually."
        )


if __name__ == "__main__":
    main()
