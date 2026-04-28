from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.database import init_db
from api.routes.auth import router as auth_router
from api.routes.jobs import router as jobs_router

app = FastAPI(title="AI Short Form API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    checks = {"status": "ok", "db": "ok", "s3": "ok"}
    try:
        from api.database import SessionLocal
        with SessionLocal() as db:
            db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        checks["db"] = str(e)
        checks["status"] = "degraded"
    try:
        from api.s3 import _client
        from api.config import settings
        _client().head_bucket(Bucket=settings.AWS_S3_BUCKET)
    except Exception as e:
        checks["s3"] = str(e)
        checks["status"] = "degraded"
    return checks


app.include_router(auth_router)
app.include_router(jobs_router)
