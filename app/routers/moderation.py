# backend/app/routers/moderation.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services import moderation_service

router = APIRouter(prefix="/moderation", tags=["Moderation"])


class FlagContent(BaseModel):
    content_id: int


class ResolveFlag(BaseModel):
    content_id: int
    remove: bool


@router.post("/flag")
async def flag_content(data: FlagContent):
    receipt = moderation_service.flag_content(data.content_id)
    return {"success": True, "receipt": receipt}


@router.post("/resolve")
async def resolve_flag(data: ResolveFlag):
    receipt = moderation_service.resolve_flag(data.content_id, data.remove)
    return {"success": True, "receipt": receipt}


@router.get("/{content_id}")
async def get_flags(content_id: int):
    flags = moderation_service.get_flags(content_id)
    return {"success": True, "flags": flags}
