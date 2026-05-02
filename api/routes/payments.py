import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from api.auth import current_user
from api.config import settings
from api.database import get_db, User, Purchase

router = APIRouter(prefix="/payments", tags=["payments"])

PACKS = [
    {"id": "pack_1",  "generations": 1,  "price_cents": 600,  "label": "1 video",   "per_video": "$6.00"},
    {"id": "pack_5",  "generations": 5,  "price_cents": 2500, "label": "5 videos",  "per_video": "$5.00 each"},
    {"id": "pack_10", "generations": 10, "price_cents": 4000, "label": "10 videos", "per_video": "$4.00 each"},
]


@router.get("/packs")
def get_packs():
    return PACKS


@router.post("/checkout/{pack_id}")
def create_checkout(pack_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pack = next((p for p in PACKS if p["id"] == pack_id), None)
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": pack["price_cents"],
                "product_data": {
                    "name": f"AI Short Form — {pack['label']}",
                    "description": f"{pack['generations']} video generation{'s' if pack['generations'] > 1 else ''}",
                },
            },
            "quantity": 1,
        }],
        metadata={
            "user_id": str(user.id),
            "generations": str(pack["generations"]),
        },
        success_url=f"{settings.FRONTEND_URL}/dashboard?payment=success",
        cancel_url=f"{settings.FRONTEND_URL}/dashboard",
    )
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("payment_status") != "paid":
            return {"status": "ignored"}

        stripe_session_id = session["id"]

        # Idempotency — ignore if already processed
        if db.query(Purchase).filter(Purchase.stripe_session_id == stripe_session_id).first():
            return {"status": "already_processed"}

        user_id = int(session["metadata"]["user_id"])
        generations = int(session["metadata"]["generations"])

        db.query(User).filter(User.id == user_id).update({"credits": User.credits + generations})
        db.add(Purchase(
            user_id=user_id,
            stripe_session_id=stripe_session_id,
            stripe_payment_intent_id=session.get("payment_intent"),
            generations=generations,
            amount_cents=session["amount_total"],
        ))
        db.commit()

    return {"status": "ok"}
