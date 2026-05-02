import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.config import settings
from api.database import get_db, User
from api.auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
def google_login():
    params = (
        f"client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope={settings.GOOGLE_SCOPE.replace(' ', '+')}"
        f"&access_type=offline"
    )
    return RedirectResponse(f"{settings.GOOGLE_AUTH_URL}?{params}")


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_resp = await client.post(
            settings.GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google code")
        token_data = token_resp.json()

        # Get user info
        userinfo_resp = await client.get(
            settings.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google user info")
        info = userinfo_resp.json()

    # Upsert user
    user = db.query(User).filter(User.google_id == info["id"]).first()
    if not user:
        user = User(
            google_id=info["id"],
            email=info["email"],
            name=info["name"],
            picture=info.get("picture"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_token(user.id)
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?token={token}")


@router.get("/me")
def me(db: Session = Depends(get_db), user: User = Depends(__import__("api.auth", fromlist=["current_user"]).current_user)):
    return {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture, "credits": user.credits}
