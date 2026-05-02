import json
import os
import time
from pathlib import Path

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from mutagen.mp3 import MP3

# ── Config ────────────────────────────────────────────────────────────────────
# Set ELEVENLABS_VOICE_ID in your environment, or replace the fallback string.
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "YOUR_VOICE_ID_HERE")
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    use_speaker_boost=True,
)


def generate_voiceovers(run_dir: Path) -> list[dict]:
    if VOICE_ID == "YOUR_VOICE_ID_HERE":
        raise ValueError(
            "No voice ID set. Export ELEVENLABS_VOICE_ID=<id> or edit VOICE_ID in "
            "pipeline/voiceover/generator.py."
        )

    prompts_path = run_dir / "video_prompts" / "video_prompts.json"
    if not prompts_path.exists():
        raise FileNotFoundError(
            f"video_prompts.json not found at {prompts_path}. Run Stage 3 first."
        )

    with open(prompts_path) as f:
        video_prompts = json.load(f)

    audio_dir = run_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    client = ElevenLabs()  # reads ELEVENLABS_API_KEY from env
    results = []

    for i, vp in enumerate(video_prompts):
        script_type_name = vp["script_type_name"]
        print(f"[voiceover] generating '{script_type_name}' ({i + 1}/{len(video_prompts)})...")

        script = vp["script"]
        voiceover_notes = vp.get("voiceover_notes", "")

        # Prepend delivery notes as a silent context hint via a system-style prefix
        # ElevenLabs ignores non-speech text but the notes inform our own QA
        audio_bytes = _call_elevenlabs(client, script)

        slug = vp["script_type_id"]
        mp3_path = audio_dir / f"audio_{i + 1:02d}_{slug}.mp3"
        mp3_path.write_bytes(audio_bytes)

        duration = _get_duration(mp3_path)

        result = {
            "script_type_id": vp["script_type_id"],
            "script_type_name": script_type_name,
            "audio_path": str(mp3_path),
            "duration_seconds": duration,
            "voice_id": VOICE_ID,
            "model_id": MODEL_ID,
            "voiceover_notes": voiceover_notes,
        }

        print(f"  {duration:.1f}s → {mp3_path.name}")
        results.append(result)

    summary_path = audio_dir / "audio.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def _call_elevenlabs(client: ElevenLabs, text: str) -> bytes:
    for attempt in range(5):
        try:
            audio_generator = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=f"[fast paced]{text}",
                model_id=MODEL_ID,
                output_format=OUTPUT_FORMAT,
                voice_settings=VOICE_SETTINGS,
            )
            return b"".join(audio_generator)
        except Exception as e:
            if attempt == 4:
                raise
            err = str(e)
            if "429" in err or "rate" in err.lower() or "too many" in err.lower():
                time.sleep(2 ** attempt)
            else:
                raise


def _get_duration(mp3_path: Path) -> float:
    audio = MP3(str(mp3_path))
    return round(audio.info.length, 2)
