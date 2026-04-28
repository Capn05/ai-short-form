import boto3
from pathlib import Path
from api.config import settings


def _client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def upload_run_files(run_dir: Path, run_id: str) -> list[str]:
    """Upload all .mp4 files from run_dir/final/ to S3. Returns list of S3 keys."""
    client = _client()
    final_dir = run_dir / "final"
    keys = []
    for f in sorted(final_dir.iterdir()):
        if f.suffix == ".mp4":
            key = f"runs/{run_id}/{f.name}"
            client.upload_file(str(f), settings.AWS_S3_BUCKET, key)
            keys.append(key)
    return keys


def list_run_files(run_id: str) -> list[str]:
    """List .mp4 filenames for a run."""
    client = _client()
    prefix = f"runs/{run_id}/"
    resp = client.list_objects_v2(Bucket=settings.AWS_S3_BUCKET, Prefix=prefix)
    return [obj["Key"].split("/")[-1] for obj in resp.get("Contents", []) if obj["Key"].endswith(".mp4")]


def presigned_url(run_id: str, filename: str, expires: int = 3600) -> str:
    """Generate a presigned download URL."""
    client = _client()
    key = f"runs/{run_id}/{filename}"
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
