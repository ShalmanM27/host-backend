from fastapi import APIRouter
from pydantic import BaseModel
from app.services import comment_service

router = APIRouter(prefix="/comment", tags=["Comment"])

class CommentCreate(BaseModel):
    post_id: int
    content: str
    media_hash: str = ""

class CommentUpdate(BaseModel):
    comment_id: int
    content: str
    media_hash: str = ""

class CommentAction(BaseModel):
    comment_id: int

@router.post("/create")
async def create_comment(data: CommentCreate):
    receipt = comment_service.create_comment(data.post_id, data.content, data.media_hash)
    return {"success": True, "receipt": receipt}

@router.post("/update")
async def update_comment(data: CommentUpdate):
    receipt = comment_service.update_comment(data.comment_id, data.content, data.media_hash)
    return {"success": True, "receipt": receipt}

@router.post("/delete")
async def delete_comment(data: CommentAction):
    receipt = comment_service.delete_comment(data.comment_id)
    return {"success": True, "receipt": receipt}

@router.get("/{post_id}")
async def get_comments(post_id: int):
    comments = comment_service.get_comments(post_id)
    return {"success": True, "comments": comments}
