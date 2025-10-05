# app/routers/streak.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services import streak_service

router = APIRouter(prefix="/streak", tags=["Streak"])


# ----------------- MODELS -----------------
class UserAddress(BaseModel):
    user_address: str


# ----------------- ROUTES -----------------
@router.post("/complete")
async def complete_task(data: UserAddress):
    try:
        receipt = streak_service.complete_task(data.user_address)
        return {"success": True, "receipt": receipt}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/current/{user_address}")
async def get_current_streak(user_address: str):
    try:
        streak = streak_service.get_current_streak(user_address)
        return {"success": True, "streak": streak}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/history/{user_address}")
async def get_last_7_days_status(user_address: str):
    try:
        history = streak_service.get_last_7_days_status(user_address)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}
