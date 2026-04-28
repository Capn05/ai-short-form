import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GOOGLE_CLIENT_ID: str = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET: str = os.environ["GOOGLE_CLIENT_SECRET"]
    JWT_SECRET: str = os.environ["JWT_SECRET"]
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    BACKEND_URL: str = os.environ["BACKEND_URL"]
    FRONTEND_URL: str = os.environ["FRONTEND_URL"]

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_SCOPE: str = "openid email profile"

    @property
    def google_redirect_uri(self) -> str:
        return f"{self.BACKEND_URL}/auth/google/callback"


settings = Settings()
