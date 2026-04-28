import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from pipeline.scraper.shopify import scrape
from pipeline.scripts.generator import generate_scripts
from pipeline.video_prompt.generator import generate_video_prompts
from pipeline.voiceover.generator import generate_voiceovers, VOICE_ID
from pipeline.video.generator import generate_videos
from pipeline.composition.generator import compose


def _get_voice_persona() -> str | None:
    if VOICE_ID == "YOUR_VOICE_ID_HERE":
        return None
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs()
        voice = client.voices.get(VOICE_ID)
        labels = voice.labels or {}
        parts = [p for p in [labels.get("gender"), labels.get("age"), labels.get("accent")] if p]
        return ", ".join(parts) if parts else None
    except Exception as e:
        print(f"  [stage 3] warning: could not fetch voice persona ({e})")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate UGC video ads from a Shopify product URL"
    )
    parser.add_argument("--url", help="Shopify product URL (required for Stage 1)")
    parser.add_argument(
        "--run-id",
        help="Existing run ID — skips Stage 1 and runs from Stage 2 onward",
    )
    parser.add_argument(
        "--output", default="output", help="Output directory (default: output/)"
    )
    parser.add_argument(
        "--skip-reviews",
        action="store_true",
        help="Skip Playwright review scraping",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        default=None,
        help="Run only a specific stage (default: run all stages)",
    )
    parser.add_argument(
        "--n-scripts",
        type=int,
        default=1,
        help="Number of script variants to generate (default: 1)",
    )
    args = parser.parse_args()

    output_base = Path(args.output)

    if args.run_id and args.url:
        print("Error: provide either --url or --run-id, not both.", file=sys.stderr)
        sys.exit(1)
    if not args.run_id and not args.url:
        print("Error: --url is required unless --run-id is provided.", file=sys.stderr)
        sys.exit(1)

    # ── Stage 1 ──────────────────────────────────────────────────────────────
    if args.run_id:
        run_dir = output_base / "runs" / args.run_id
        product_path = run_dir / "product.json"
        if not product_path.exists():
            print(f"Error: {product_path} not found.", file=sys.stderr)
            sys.exit(1)
        with open(product_path) as f:
            product = json.load(f)
        print(f"[stage 1] skipped — using existing run {args.run_id}")
    else:
        if args.stage in (None, 1):
            try:
                product = scrape(args.url, output_base, skip_reviews=args.skip_reviews)
            except ValueError as e:
                print(f"\nError: {e}", file=sys.stderr)
                sys.exit(1)

            print(f"\n--- Stage 1 complete ---")
            print(f"Product:  {product['product_name']}")
            print(f"Price:    {product['price']}")
            print(f"Images:   {product['image_count']}")
            print(f"Reviews:  {product['review_count']}")
            print(f"Run dir:  {product['run_dir']}")

            if not product["has_reviews"]:
                print(
                    "\n⚠  No reviews found. Script quality will be weaker without real customer language."
                    "\n   Consider providing 2–3 testimonials manually."
                )

            if args.stage == 1:
                return
        else:
            print("Error: --url required to run Stage 1.", file=sys.stderr)
            sys.exit(1)

    run_dir = Path(product["run_dir"])

    # ── Stage 2 ──────────────────────────────────────────────────────────────
    if args.stage in (None, 2, 3):
        voice_persona = _get_voice_persona()
        if voice_persona:
            print(f"  voice persona: {voice_persona}")

    if args.stage in (None, 2):
        print(f"\n[stage 2] generating {args.n_scripts} scripts...")
        scripts = generate_scripts(product, run_dir, n=args.n_scripts, voice_persona=voice_persona)

        print(f"\n--- Stage 2 complete ---")
        for s in scripts:
            print(f"\n[{s['script_type_name']}]")
            print(s["script"])

        if args.stage == 2:
            return

    # ── Stage 3 ──────────────────────────────────────────────────────────────
    if args.stage in (None, 3):
        print(f"\n[stage 3] generating video prompts...")
        try:
            video_prompts = generate_video_prompts(product, run_dir, voice_persona=voice_persona)
        except FileNotFoundError as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"\n--- Stage 3 complete ---")
        for vp in video_prompts:
            print(f"\n[{vp['script_type_name']}] — {len(vp['chunks'])} chunks, ~{vp['total_duration_seconds']}s")
            print(f"Voiceover notes: {vp['voiceover_notes']}")
            for chunk in vp["chunks"]:
                ref = f" [ref: {Path(chunk['reference_image']).name}]" if chunk.get("reference_image") else ""
                overlay = f" + overlay: '{chunk['text_overlay']['text']}'" if chunk.get("text_overlay") else ""
                print(f"  Chunk {chunk['chunk_number']} ({chunk['total_duration_seconds']}s){ref}{overlay}")
                print(f"    {chunk['prompt'][:140]}{'...' if len(chunk['prompt']) > 140 else ''}")

        print(f"\nRun dir:       {run_dir}")
        print(f"Video prompts: {run_dir}/video_prompts/")

        if args.stage == 3:
            return

    # ── Stage 4 ──────────────────────────────────────────────────────────────
    if args.stage in (None, 4):
        print(f"\n[stage 4] generating voiceovers...")
        try:
            voiceovers = generate_voiceovers(run_dir)
        except (FileNotFoundError, ValueError) as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"\n--- Stage 4 complete ---")
        for v in voiceovers:
            print(f"  [{v['script_type_name']}] {v['duration_seconds']}s → {Path(v['audio_path']).name}")
        print(f"\nAudio: {run_dir}/audio/")

        if args.stage == 4:
            return

    # ── Stage 5 ──────────────────────────────────────────────────────────────
    if args.stage in (None, 5):
        print(f"\n[stage 5] generating videos...")
        try:
            videos = generate_videos(run_dir)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"\n--- Stage 5 complete ---")
        for v in videos:
            print(f"  [{v['script_type_name']}] {len(v['clip_paths'])} chunks → {Path(v['video_path']).name}")
        print(f"\nVideo: {run_dir}/video/")

        if args.stage == 5:
            return

    # ── Stage 6 ──────────────────────────────────────────────────────────────
    if args.stage in (None, 6):
        print(f"\n[stage 6] composing final videos...")
        try:
            finals = compose(run_dir)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"\n--- Stage 6 complete ---")
        for f in finals:
            print(f"  [{f['script_type_name']}] {f['duration_seconds']:.1f}s → {Path(f['final_path']).name}")
        print(f"\nFinal: {run_dir}/final/")


if __name__ == "__main__":
    main()
