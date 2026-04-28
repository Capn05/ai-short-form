import json
import subprocess
from pathlib import Path

import anthropic
from openai import OpenAI

# Caption settings — tuned for 480p 9:16 (496×864)
WORDS_PER_CAPTION = 1
CAPTION_FONT = "Arial"
CAPTION_FONT_SIZE = 35
CAPTION_MARGIN_V = 130   # px from bottom — used only for bottom-aligned styles
CAPTION_OUTLINE = 5      # px black outline


def compose(run_dir: Path) -> list[dict]:
    audio_path = run_dir / "audio" / "audio.json"
    video_path = run_dir / "video" / "video.json"

    for p in [audio_path, video_path]:
        if not p.exists():
            raise FileNotFoundError(f"{p} not found. Run prior stages first.")

    with open(audio_path) as f:
        audio_data = json.load(f)
    with open(video_path) as f:
        video_data = json.load(f)

    audio_by_id = {a["script_type_id"]: a for a in audio_data}

    final_dir = run_dir / "final"
    final_dir.mkdir(exist_ok=True)

    client = OpenAI()
    results = []

    for i, video in enumerate(video_data):
        slug = video["script_type_id"]
        name = video["script_type_name"]
        print(f"[compose] '{name}' ({i + 1}/{len(video_data)})...")

        audio = audio_by_id[slug]

        mp3_path = Path(audio["audio_path"])
        duration = audio["duration_seconds"]
        silent_mp4 = Path(video["video_path"])

        # Step 1 — transcribe for word timestamps
        print(f"  transcribing...")
        words = _transcribe(client, mp3_path)
        print(f"  {len(words)} words")

        # Step 1b — mark emotionally impactful words for pop effect
        _mark_pop_words(words)

        # Step 2 — write ASS subtitle file
        ass_path = final_dir / f"captions_{i + 1:02d}_{slug}.ass"
        _write_ass(words, ass_path)

        # Step 3 — FFmpeg: trim + burn subs + mix audio
        output_path = final_dir / f"final_{i + 1:02d}_{slug}.mp4"
        print(f"  composing...")
        _ffmpeg_compose(silent_mp4, mp3_path, ass_path, duration, output_path)
        print(f"  → {output_path.name} ({duration:.1f}s)")

        results.append({
            "script_type_id": slug,
            "script_type_name": name,
            "final_path": str(output_path),
            "duration_seconds": duration,
        })

    summary_path = final_dir / "final.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def _transcribe(client: OpenAI, mp3_path: Path) -> list[dict]:
    with open(mp3_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    return [{"word": w.word, "start": w.start, "end": w.end} for w in response.words]


def _write_ass(words: list[dict], ass_path: Path) -> None:
    captions = _group_words(words, WORDS_PER_CAPTION)

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 496",
        "PlayResY: 864",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
        "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,{CAPTION_FONT},{CAPTION_FONT_SIZE},"
        f"&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        f"1,0,0,0,100,100,0,0,1,{CAPTION_OUTLINE},1,5,20,20,{CAPTION_MARGIN_V},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for cap in captions:
        text = _ass_escape(cap["text"])
        if cap.get("pop"):
            text = r"{\fs44}" + text
        lines.append(
            f"Dialogue: 0,{_ass_time(cap['start'])},{_ass_time(cap['end'])},"
            f"Caption,,0,0,0,,{text}"
        )

    ass_path.write_text("\n".join(lines), encoding="utf-8")


def _mark_pop_words(words: list[dict]) -> None:
    if not words:
        return
    try:
        ac = anthropic.Anthropic()
        transcript = " ".join(f"{i}:{w['word']}" for i, w in enumerate(words))
        response = ac.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Transcript (index:word):\n{transcript}\n\n"
                    "Identify the ~15% of words with the most emotional impact or urgency for a short-form video ad caption. "
                    "Return only a comma-separated list of indices. No other text."
                ),
            }],
        )
        raw = next((b.text.strip() for b in response.content if b.type == "text"), "")
        pop_indices = {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}
        for idx in pop_indices:
            if idx < len(words):
                words[idx]["pop"] = True
    except Exception as e:
        print(f"  [compose] pop word detection failed: {e}")


def _group_words(words: list[dict], n: int, min_duration: float = 0.15) -> list[dict]:
    groups = []
    for i in range(0, len(words), n):
        group = words[i : i + n]
        text = " ".join(w["word"].strip() for w in group).upper()
        start = group[0]["start"]
        end = group[-1]["end"]
        next_start = words[i + n]["start"] if i + n < len(words) else None
        if end - start < min_duration:
            end = min(start + min_duration, next_start - 0.01) if next_start else start + min_duration
        pop = any(w.get("pop") for w in group)
        groups.append({"start": start, "end": end, "text": text, "pop": pop})
    return groups


def _ffmpeg_compose(
    video: Path, audio: Path, ass: Path, duration: float, output: Path
) -> None:
    ass_filter = f"ass={_escape_filter_path(str(ass))}"

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video),
            "-i", str(audio),
            "-map", "0:v",
            "-map", "1:a",
            "-vf", ass_filter,
            "-t", str(duration),
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", "192k",
            str(output),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg composition failed:\n{result.stderr[-800:]}")


def _ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    cs = int(round((s % 1) * 100))
    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("{", "{{").replace("}", "}}")


def _escape_filter_path(path: str) -> str:
    return path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
