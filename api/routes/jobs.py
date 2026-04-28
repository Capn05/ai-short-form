import json
import uuid
from pathlib import Path
from datetime import datetime

import redis as redis_lib
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.config import settings
from api.database import get_db, Job
from api.auth import current_user
from api.database import User

router = APIRouter(prefix="/jobs", tags=["jobs"])
_redis = redis_lib.from_url(settings.REDIS_URL)


class SubmitRequest(BaseModel):
    product_url: str


@router.post("")
def submit_job(body: SubmitRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    from api.tasks import run_pipeline

    job_id = str(uuid.uuid4())
    job = Job(id=job_id, user_id=user.id, product_url=body.product_url)
    db.add(job)
    db.commit()

    run_pipeline.delay(job_id, body.product_url)
    return {"job_id": job_id}


@router.get("")
def list_jobs(db: Session = Depends(get_db), user: User = Depends(current_user)):
    jobs = (
        db.query(Job)
        .filter(Job.user_id == user.id)
        .order_by(Job.created_at.desc())
        .limit(20)
        .all()
    )
    return [_job_dict(j) for j in jobs]


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    raw = _redis.get(f"job:{job_id}:progress")
    progress = json.loads(raw) if raw else None

    return {**_job_dict(job), "progress": progress}


@router.get("/{job_id}/files")
def list_files(job_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job or job.status != "done" or not job.run_id:
        raise HTTPException(status_code=404, detail="Job not ready")

    final_dir = Path("output/runs") / job.run_id / "final"
    if not final_dir.exists():
        raise HTTPException(status_code=404, detail="Output files not found")

    files = [f.name for f in sorted(final_dir.iterdir()) if f.suffix == ".mp4"]
    return {"files": files}


@router.get("/{job_id}/download/{filename}")
def download_file(
    job_id: str,
    filename: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job or job.status != "done" or not job.run_id:
        raise HTTPException(status_code=404, detail="Job not ready")

    # Prevent path traversal
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = Path("output/runs") / job.run_id / "final" / filename
    if not path.exists() or path.suffix != ".mp4":
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="video/mp4", filename=filename)


def _job_dict(job: Job) -> dict:
    return {
        "id": job.id,
        "status": job.status,
        "product_url": job.product_url,
        "run_id": job.run_id,
        "error": job.error,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }
