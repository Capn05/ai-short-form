import base64
import json
import subprocess
import tempfile
import time
from pathlib import Path

import replicate
import requests
from openai import OpenAI

MODEL = "bytedance/seedance-2.0"
RESOLUTION = "480p"
ASPECT_RATIO = "9:16"
MAX_RETRIES = 4

# Seedance only accepts these discrete duration values (seconds)
VALID_DURATIONS = [4, 5, 6, 8, 10, 12, 15]


def generate_videos(run_dir: Path) -> list[dict]:
    prompts_path = run_dir / "video_prompts" / "video_prompts.json"
    if not prompts_path.exists():
        raise FileNotFoundError(
            f"video_prompts.json not found at {prompts_path}. Run Stage 3 first."
        )

    audio_path = run_dir / "audio" / "audio.json"
    if not audio_path.exists():
        raise FileNotFoundError(
            f"audio.json not found at {audio_path}. Run Stage 4 first."
        )

    with open(prompts_path) as f:
        video_prompts = json.load(f)

    with open(audio_path) as f:
        audio_data = json.load(f)

    # Build a lookup from script_type_id → audio duration
    audio_durations = {a["script_type_id"]: a["duration_seconds"] for a in audio_data}

    video_dir = run_dir / "video"
    clips_dir = video_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for i, vp in enumerate(video_prompts):
        slug = vp["script_type_id"]
        name = vp["script_type_name"]
        audio_duration = audio_durations.get(slug, vp["total_duration_seconds"])
        chunks = vp["chunks"]
        chunk_durations = _distribute_durations(audio_duration, len(chunks))

        ref_path = vp.get("reference_image")
        if ref_path and Path(ref_path).exists():
            ref_images = _clean_reference_images([ref_path], run_dir)
        else:
            ref_images = _find_reference_images(run_dir)

        total_video = sum(chunk_durations)
        print(
            f"[video] generating '{name}' ({i + 1}/{len(video_prompts)}) "
            f"— audio {audio_duration:.1f}s → {len(chunks)} chunks {chunk_durations} = {total_video}s"
        )

        variant_dir = clips_dir / f"video_{i + 1:02d}_{slug}"
        variant_dir.mkdir(exist_ok=True)

        clip_paths = []
        prev_clip: Path | None = None
        for chunk, duration in zip(chunks, chunk_durations):
            chunk_num = chunk["chunk_number"]
            print(f"  chunk {chunk_num}/{len(chunks)} ({duration}s)...")

            clip_path = variant_dir / f"chunk_{chunk_num:02d}.mp4"
            _generate_chunk(chunk, clip_path, duration, ref_images, prev_clip)
            clip_paths.append(clip_path)
            prev_clip = clip_path
            print(f"    → {clip_path.name}")

        stitched_path = video_dir / f"video_{i + 1:02d}_{slug}.mp4"
        print(f"  stitching {len(clip_paths)} clips...")
        _stitch_clips(clip_paths, stitched_path)
        print(f"  → {stitched_path.name}")

        result = {
            "script_type_id": slug,
            "script_type_name": name,
            "video_path": str(stitched_path),
            "clip_paths": [str(p) for p in clip_paths],
            "chunk_durations": chunk_durations,
            "total_video_seconds": total_video,
            "audio_seconds": audio_duration,
        }
        results.append(result)

    summary_path = video_dir / "video.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def _distribute_durations(audio_duration: float, n_chunks: int) -> list[int]:
    per_chunk = audio_duration / n_chunks
    return [_nearest_duration(per_chunk) for _ in range(n_chunks)]


def _nearest_duration(target: float) -> int:
    for d in VALID_DURATIONS:
        if d >= target:
            return d
    return VALID_DURATIONS[-1]


def _generate_chunk(
    chunk: dict,
    output_path: Path,
    duration: int,
    ref_images: list[str],
    ref_video: Path | None = None,
) -> None:
    prompt = chunk["prompt"]
    valid_refs = [p for p in ref_images if Path(p).exists()]
    has_video = ref_video and ref_video.exists()

    if valid_refs and has_video:
        refs_str = ", ".join(f"[Image{i + 1}]" for i in range(len(valid_refs)))
        prompt = f"{prompt} Maintain visual consistency with {refs_str} and the reference video."
    elif valid_refs:
        refs_str = ", ".join(f"[Image{i + 1}]" for i in range(len(valid_refs)))
        prompt = f"{prompt} Maintain visual consistency with {refs_str}."
    elif has_video:
        prompt = f"{prompt} Maintain visual consistency with the reference video."

    for attempt in range(MAX_RETRIES + 1):
        try:
            inp = {
                "prompt": prompt,
                "duration": duration,
                "resolution": RESOLUTION,
                "aspect_ratio": ASPECT_RATIO,
                "generate_audio": False,
            }

            if valid_refs:
                inp["reference_images"] = [open(p, "rb") for p in valid_refs]

            if has_video:
                inp["reference_videos"] = [open(ref_video, "rb")]

            output = replicate.run(MODEL, input=inp)

            url = output if isinstance(output, str) else output.url
            _download(url, output_path)
            return

        except Exception as e:
            if attempt < MAX_RETRIES:
                is_pa = "code: PA" in str(e) or "interrupted" in str(e).lower()
                wait = 60 if is_pa else 15 * (attempt + 1)
                print(f"    attempt {attempt + 1} failed ({e}). retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Chunk generation failed after {MAX_RETRIES + 1} attempts: {e}"
                )


def _clean_reference_images(image_paths: list[str], run_dir: Path) -> list[str]:
    cleaned_dir = run_dir / "images_cleaned"
    cleaned_dir.mkdir(exist_ok=True)

    client = OpenAI()
    results = []

    for path_str in image_paths:
        path = Path(path_str)
        cleaned_path = cleaned_dir / path.name

        if cleaned_path.exists():
            results.append(str(cleaned_path))
            continue

        try:
            print(f"  [video] cleaning reference image {path.name}...")
            from PIL import Image as PILImage
            import io
            img = PILImage.open(path).convert("RGBA")
            img.thumbnail((1024, 1024), PILImage.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            buf.name = "image.png"
            response = client.images.edit(
                model="gpt-image-2",
                image=buf,
                prompt=(
                    "Remove all small text, fine print, ingredient lists, directions, and subtext "
                    "from this product label or packaging. Keep the main brand name and large product "
                    "name text intact. Do not alter the product shape, colors, or overall appearance."
                ),
                size="1024x1024",
            )
            img_bytes = base64.b64decode(response.data[0].b64_json)
            cleaned_path.write_bytes(img_bytes)
            results.append(str(cleaned_path))
            print(f"    → {cleaned_path.name}")
        except Exception as e:
            print(f"  [video] image cleaning failed for {path.name}: {e} — using original")
            results.append(path_str)

    return results


def _find_reference_images(run_dir: Path, n: int = 3) -> list[str]:
    images_dir = run_dir / "images"
    paths = []
    for p in sorted(images_dir.iterdir()):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            paths.append(str(p))
        if len(paths) == n:
            break
    return paths


def _download(url: str, output_path: Path) -> None:
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)


def _stitch_clips(clip_paths: list[Path], output_path: Path) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for clip in clip_paths:
            f.write(f"file '{clip.resolve()}'\n")
        filelist = Path(f.name)

    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(filelist),
                "-c", "copy",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg stitching failed:\n{result.stderr[-500:]}")
    finally:
        filelist.unlink(missing_ok=True)
