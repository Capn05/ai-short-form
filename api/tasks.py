import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from api.celery_app import celery
from api.config import settings
from api.database import SessionLocal, Job


def _set_progress(redis_client, job_id: str, stage: int, message: str, percent: int):
    redis_client.setex(
        f"job:{job_id}:progress",
        7200,
        json.dumps({"stage": stage, "message": message, "percent": percent}),
    )


def _update_job(job_id: str, **kwargs):
    with SessionLocal() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            for k, v in kwargs.items():
                setattr(job, k, v)
            job.updated_at = datetime.utcnow()
            db.commit()


def _get_voice_persona():
    from pipeline.voiceover.generator import VOICE_ID
    if VOICE_ID == "YOUR_VOICE_ID_HERE":
        return None
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs()
        voice = client.voices.get(VOICE_ID)
        labels = voice.labels or {}
        parts = [p for p in [labels.get("gender"), labels.get("age"), labels.get("accent")] if p]
        return ", ".join(parts) if parts else None
    except Exception:
        return None


@celery.task(bind=True, name="run_pipeline")
def run_pipeline(self, job_id: str, product_url: str):
    import redis as redis_lib
    r = redis_lib.from_url(settings.REDIS_URL)

    try:
        _update_job(job_id, status="running")
        _set_progress(r, job_id, 1, "Reading your product...", 5)

        from pipeline.scraper.shopify import scrape
        product = scrape(product_url, Path("output"), skip_reviews=False)
        run_dir = Path(product["run_dir"])
        run_id = run_dir.name
        _update_job(job_id, run_id=run_id)

        _set_progress(r, job_id, 2, "Writing your ad script...", 20)
        voice_persona = _get_voice_persona()
        from pipeline.scripts.generator import generate_scripts
        generate_scripts(product, run_dir, n=1, voice_persona=voice_persona)

        _set_progress(r, job_id, 3, "Planning your shots...", 35)
        from pipeline.video_prompt.generator import generate_video_prompts
        generate_video_prompts(product, run_dir, voice_persona=voice_persona)

        _set_progress(r, job_id, 4, "Recording voiceover...", 50)
        from pipeline.voiceover.generator import generate_voiceovers
        generate_voiceovers(run_dir)

        _set_progress(r, job_id, 5, "Filming your ad...", 65)
        from pipeline.video.generator import generate_videos
        generate_videos(run_dir)

        _set_progress(r, job_id, 6, "Putting it all together...", 85)
        from pipeline.composition.generator import compose
        compose(run_dir)

        _set_progress(r, job_id, 6, "Uploading...", 95)
        from api.s3 import upload_run_files
        upload_run_files(run_dir, run_id)

        shutil.rmtree(run_dir, ignore_errors=True)

        _update_job(job_id, status="done")
        _set_progress(r, job_id, 6, "Done!", 100)

    except Exception as e:
        _update_job(job_id, status="failed", error=str(e))
        _set_progress(r, job_id, 0, f"Failed: {e}", 0)
        raise
