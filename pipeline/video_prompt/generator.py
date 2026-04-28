import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

import anthropic

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MEDIA_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

TARGET_VIDEO_DURATION = 28  # seconds — sweet spot per TikTok/Meta data (21–34s range)
MAX_CHUNK_DURATION = 9.5    # seconds — stay safely under Seedance's 10s limit
TARGET_CHUNKS = 3           # 3 × ~9s = ~27s

JSON_SCHEMA = """{
  "hook_type": "<string: the hook type chosen for chunk 1 shot 1>",
  "hook_reasoning": "<string: one sentence explaining why this hook type matches the script's opening line>",
  "voiceover_notes": "<string: tone, energy, pacing>",
  "total_duration_seconds": <number, target 26-30>,
  "chunks": [
    {
      "chunk_number": <integer, 1-based>,
      "total_duration_seconds": <number, max 9.5>,
      "prompt": "<string: Seedance 2 multi-shot prompt — describe the full sequence of cuts within this chunk, e.g. 'Shot 1 (3s): ... | CUT | Shot 2 (3s): ... | CUT | Shot 3 (3s): ...'>"
    }
  ]
}"""


def generate_video_prompts(product: dict, run_dir: Path, voice_persona: str | None = None) -> list[dict]:
    scripts_path = run_dir / "scripts" / "scripts.json"
    if not scripts_path.exists():
        raise FileNotFoundError(
            f"scripts.json not found at {scripts_path}. Run Stage 2 first."
        )

    with open(scripts_path) as f:
        scripts = json.load(f)

    prompts_dir = run_dir / "video_prompts"
    prompts_dir.mkdir(exist_ok=True)

    client = anthropic.Anthropic()

    # Call 1: pick reference image from all product images
    all_image_blocks = _load_images(product.get("images", []), limit=8)
    ref_image_block, ref_image_path = _select_reference_image(client, all_image_blocks, product.get("images", []))

    # Call 2: extract product mechanics from video frames (if video exists)
    video_frames = _load_product_video(product.get("video"))
    mechanics = _describe_mechanics(client, video_frames, product) if video_frames else None

    system_prompt = _build_system_prompt(voice_persona)
    results = []

    for i, script in enumerate(scripts):
        print(
            f"[video_prompts] generating chunk prompts for '{script['script_type_name']}' ({i + 1}/{len(scripts)})..."
        )

        raw = _generate_prompts(client, system_prompt, product, script, ref_image_block, mechanics, voice_persona)

        output = {
            "script_type_id": script["script_type_id"],
            "script_type_name": script["script_type_name"],
            "script": script["script"],
            "hook_type": raw.get("hook_type"),
            "hook_reasoning": raw.get("hook_reasoning"),
            "voiceover_notes": raw["voiceover_notes"],
            "total_duration_seconds": raw["total_duration_seconds"],
            "reference_image": ref_image_path,
            "product_mechanics": mechanics,
            "chunks": raw["chunks"],
        }

        slug = script["script_type_id"]
        out_path = prompts_dir / f"prompt_{i + 1:02d}_{slug}.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)

        total = raw["total_duration_seconds"]
        n_chunks = len(raw["chunks"])
        hook = raw.get("hook_type", "unknown")
        print(f"  {n_chunks} chunks, ~{total}s total, hook: {hook} → {out_path.name}")
        results.append(output)

    summary_path = prompts_dir / "video_prompts.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def _select_reference_image(
    client: anthropic.Anthropic,
    image_blocks: list[dict],
    image_paths: list[str],
) -> tuple[dict | None, str | None]:
    if not image_blocks:
        return None, None

    if len(image_blocks) == 1:
        return image_blocks[0], image_paths[0]

    print(f"  [video_prompts] selecting best reference image from {len(image_blocks)}...")

    content = [
        {
            "type": "text",
            "text": (
                "These are product images. Return ONLY a JSON object with the 0-based index of the single best "
                "reference image — the clearest shot of the product alone, ideally against a plain background, "
                "not a lifestyle or in-use photo. Format: {\"index\": N}"
            ),
        }
    ]
    content.extend(image_blocks)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=32,
        messages=[{"role": "user", "content": content}],
    )

    try:
        text = next(b.text for b in response.content if b.type == "text")
        idx = json.loads(text)["index"]
        idx = max(0, min(idx, len(image_blocks) - 1))
        print(f"  [video_prompts] selected image index {idx}")
        return image_blocks[idx], image_paths[idx]
    except Exception as e:
        print(f"  [video_prompts] image selection failed ({e}), using index 0")
        return image_blocks[0], image_paths[0]


def _describe_mechanics(client: anthropic.Anthropic, video_frames: list[dict], product: dict | None = None) -> str | None:
    if not video_frames:
        return None

    print(f"  [video_prompts] extracting product mechanics from video frames...")

    context = ""
    if product:
        context = f"Product: {product.get('product_name', '')}\n\nDescription:\n{product.get('description', '').strip()[:600]}\n\n"

    content = [
        {
            "type": "text",
            "text": (
                f"{context}These are frames from a product demo video. In 2–3 sentences, describe exactly how this "
                "product is physically used — what the user's hands do step by step, what opens, closes, pours, or "
                "dispenses. Focus only on physical mechanics, not features or benefits. Be literal and specific."
            ),
        }
    ]
    content.extend(video_frames)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": content}],
    )

    try:
        mechanics = next(b.text for b in response.content if b.type == "text").strip()
        print(f"  [video_prompts] mechanics: {mechanics[:100]}...")
        return mechanics
    except Exception as e:
        print(f"  [video_prompts] mechanics extraction failed ({e})")
        return None


def _generate_prompts(
    client: anthropic.Anthropic,
    system_prompt: list[dict],
    product: dict,
    script: dict,
    ref_image_block: dict | None,
    mechanics: str | None,
    voice_persona: str | None,
) -> dict:
    reviews = product.get("reviews", [])
    review_block = ""
    if reviews:
        lines = []
        for r in reviews:
            prefix = f"{r['author']}, {r['rating']}/5 — " if r.get("author") and r.get("rating") else ""
            lines.append(f'"{prefix}{r["text"]}"')
        review_block = "\n\nCustomer reviews:\n" + "\n".join(lines)

    voiceover_duration = _estimate_duration(script["script"])

    persona_line = f"\nVoice persona: {voice_persona} — any person visible in shots should match this. Do not describe their clothing or appearance in the prompt — just ensure the demographic matches." if voice_persona else ""
    mechanics_line = f"\nHow the product physically works: {mechanics}" if mechanics else ""

    text = f"""Product: {product['product_name']}
Price: {product['price']}

Description:
{product.get('description', '').strip()}{review_block}

Script type: {script['script_type_name']}
Voiceover script:
{script['script']}

Voiceover duration: ~{voiceover_duration}s
Target video: {TARGET_VIDEO_DURATION}s total, {TARGET_CHUNKS} chunks of up to {MAX_CHUNK_DURATION}s each{persona_line}{mechanics_line}

Generate {TARGET_CHUNKS} Seedance 2 chunk prompts that cover the full video. Each chunk prompt must describe a sequence of 2–4 cuts using " | CUT | " as the separator between shots. Every shot must specify: subject, action, camera angle, movement, lighting, and setting.

The product reference image is attached — use it for colors, textures, and product details.

Respond with ONLY a JSON object matching this exact schema:
{JSON_SCHEMA}"""

    content = [{"type": "text", "text": text}]
    if ref_image_block:
        content.append(ref_image_block)

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )

    for block in response.content:
        if block.type == "text":
            return _parse_json_response(block.text)

    raise RuntimeError("Claude returned no text block.")


def _clean_json(s: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", s)


def _parse_json_response(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(_clean_json(match.group(1)))

    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(_clean_json(text[start : i + 1]))

    raise RuntimeError(f"Could not extract JSON from response:\n{text[:500]}")


def _build_system_prompt(voice_persona: str | None = None) -> list[dict]:
    system_text = f"""You are writing video prompts that will generate footage meant to look exactly like a real dog owner filmed it on their phone and posted it to TikTok. The viewer must not be able to tell it is an ad. Every prompt you write should produce footage that looks indistinguishable from organic UGC — slightly imperfect, casually filmed, real home environment. If a shot could appear in a professionally produced commercial, rewrite it.

Your job: take a voiceover script and product details, then output a complete set of Seedance 2 chunk prompts. Each chunk is one Seedance 2 generation call (max {MAX_CHUNK_DURATION}s). Seedance supports multiple cuts within a single generation — use " | CUT | " to signal cut points within a chunk prompt.

TARGET: {TARGET_VIDEO_DURATION}s total video, {TARGET_CHUNKS} chunks of up to {MAX_CHUNK_DURATION}s each.

FORMAT RULES:
- POV/b-roll only. No presenter to camera. Hands, side profile, and dog are all fine — direct address never.
- Every shot must specify: subject, action, camera angle, movement, lighting, and setting.
- Consistent lighting and setting across all chunks for seamless stitching.
- Movement: "handheld shake" — not "slight handheld shake". Never smooth gimbal, cinematic push, camera pan, zoom, or any push toward or away from the subject. Seedance will add a zoom by default if movement is not asserted strongly — counter this by describing active subject motion instead (dog walking, hand reaching, head turning).
- Banned angles: overhead, top-down, bird's-eye, and any professional cinematography framing term ("medium shot", "medium close-up", "establishing shot"). Describe angles as a person would — "looking down at", "phone held at floor level", "over the shoulder", "hand-level".
- Shot duration: 2.5–3.5 seconds each. Visual reset (cut to different angle or subject) every 2–3 seconds.
- Hard cuts only. No dissolves, no wipes.
- Never use product showcase language: no "rotating to show", "showcasing", "revealing", "neutral background", "clean background", or "slight push-in". Products must appear in real home environments, picked up casually or already mid-use — never displayed for the camera.
- The room must feel lived-in and imperfect. Describe the setting as it naturally is — worn surfaces, incidental mess, objects already present. Never append a prop list to a shot description. Background details should emerge from the scene, not be placed for the camera.

HOOK (chunk 1, shot 1):
- Action must be in frame from the very first second — no establishing shot, no product sitting still.
- First shot must have camera motion — handheld shake.
- Choose the hook type that best matches the script's opening line. Read the first sentence of the voiceover and pick the type that visually amplifies what it is saying. Justify your choice in the hook_reasoning field.

Hook types (choose one):
- PROBLEM IN PROGRESS: The bad thing is visibly happening right now. Dog gulping, scratching, refusing, pacing, anxious. Viewer pattern-matches to their own dog before a word is spoken. Use when the script opens with a problem being named or described.
- STRIKING RESULT: The after-state is shown first with no setup — dog impossibly calm, bowl still full, coat noticeably better. Creates a "how?" gap the viewer stays to close. Use when the script opens with a result or transformation.
- EXTREME CLOSE-UP: Macro shot of product texture, dog's nose at the mat, fur mid-brush, tongue mid-lick. Arrests the scroll through visual detail alone before the brain registers it as an ad. Use when the script opens with a product detail, ingredient, or specific mechanism.
- HANDS MID-ACTION: Product already in use with zero setup — brush mid-stroke, product being poured, hands already doing the thing. Purposeful motion in frame 1. Use when the script opens with an action or discovery moment.
- PATTERN INTERRUPT: Something compositionally unexpected — extreme low angle, dog filling the entire frame in an unusual way, an object in a surprising context. Fires before the "this is an ad" filter. Use when the script opens with a surprising fact or counterintuitive claim.
- BEHAVIORAL REACTION: Animal doing something so immediately recognizable it matches the viewer's own experience before context is established. Anxious panting, food inhaling, frantic scratching, head tilt. Use when the script opens with an observation about the dog's behavior.

SAFE ZONES (TikTok 9:16):
- Top 130px: covered by search bar — no key content
- Bottom 484px: covered by captions and UI buttons — no key content
- Right 140px: covered by like/share buttons — no key content
- Place all text overlays and product close-ups in the center of the frame.

LIGHTING:
- Every shot must describe lighting as slightly imperfect: uneven, slightly overexposed in one corner, or casting soft shadows. Never describe lighting as clean, perfect, or even.
- Never ring light, studio lighting, or 3-point setup.
- Kitchen: warm side window light with uneven falloff. Living room: warm lamp ambient with one darker corner. Outdoor: dappled natural light, slightly harsh.

READABLE TEXT:
- Video models can reproduce text that is clearly visible in the reference product image (brand name, product name on packaging). They cannot invent text they haven't seen — phone screens, app UI, nutritional labels, device displays will render as squiggles.
- Never write a shot requiring invented text. For phone screens: describe the hand and action only, not the screen content. For device displays: describe the indicator light or glow, not specific characters or numbers.

PHYSICAL SEQUENCES:
- Video models do not infer intermediate steps — they jump straight to outcomes, producing physically impossible results (food through closed lids, liquid defying gravity, hands through solid surfaces).
- Describe every physical interaction as a complete step-by-step sequence. Never describe an outcome without describing the action that produces it. Assume nothing is implied: opening, pressing, lifting, pouring — each must be stated explicitly.
- Never invent a physical interaction. If the exact mechanic of an action is not clearly described in the product materials, do not write a shot for it — show the product already in use, the dog reacting, or the result instead.

VOICEOVER NOTES FIELD:
- Specify: delivery style ("friend voice note, not performing"), pace (~150–165 wpm), energy (1–10), pause locations.
- Energy by category: calming/anxiety 3/10, slow feeders 5/10, deshedding 6/10, health supplements 4/10.
- CTA delivered at same pace as the rest — no sales inflection."""

    return [
        {
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _estimate_duration(script_text: str) -> float:
    words = len(script_text.split())
    return round(words / 2.5, 1)  # 150 wpm


def _detect_media_type(raw: bytes, ext: str) -> str:
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return MEDIA_TYPE_MAP.get(ext, "image/jpeg")


def _load_images(image_paths: list[str], limit: int = 8, max_size: int = 512) -> list[dict]:
    from PIL import Image
    import io

    blocks = []
    for path_str in image_paths[:limit]:
        path = Path(path_str)
        ext = path.suffix.lower()

        if ext not in SUPPORTED_IMAGE_EXTS:
            converted = _try_convert_heic(path)
            if converted is None:
                print(
                    f"  [video_prompts] skipping {path.name} "
                    f"(install pillow-heif to convert HEIC: pip install pillow-heif)"
                )
                continue
            path = converted
            ext = ".png"

        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((max_size, max_size), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            raw = buf.getvalue()
            data = base64.standard_b64encode(raw).decode("utf-8")
            blocks.append(
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": data},
                }
            )
        except Exception as e:
            print(f"  [video_prompts] warning: failed to load {path.name}: {e}")

    return blocks


def _load_product_video(video_path: str | None, fps: str = "1/3") -> list[dict]:
    if not video_path:
        return []
    path = Path(video_path)
    if not path.exists():
        return []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            frame_pattern = str(Path(tmp) / "frame_%02d.jpg")
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(path), "-vf", f"fps={fps}", "-q:v", "3", frame_pattern],
                capture_output=True,
            )
            frames = sorted(Path(tmp).glob("frame_*.jpg"))
            blocks = []
            for frame in frames:
                raw = frame.read_bytes()
                data = base64.standard_b64encode(raw).decode("utf-8")
                blocks.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}})
        print(f"  [video_prompts] extracted {len(blocks)} frames from product video")
        return blocks
    except Exception as e:
        print(f"  [video_prompts] warning: failed to extract video frames: {e}")
        return []


def _try_convert_heic(path: Path) -> Path | None:
    try:
        import pillow_heif
        from PIL import Image

        pillow_heif.register_heif_opener()
        out_path = path.with_suffix(".png")
        img = Image.open(path)
        img.save(out_path, "PNG")
        return out_path
    except ImportError:
        return None
    except Exception as e:
        print(f"  [video_prompts] HEIC conversion failed for {path.name}: {e}")
        return None
