# backend/app/routers/learning.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import learning_service
from typing import Optional

router = APIRouter(prefix="/learning", tags=["Learning"])

# ----------------- Models -----------------
class TopicCreate(BaseModel):
    title: str
    description: str

class TopicUpdate(BaseModel):
    topic_id: int
    title: str
    description: str

class ModuleCreate(BaseModel):
    topic_id: int
    module_id: Optional[int] = None
    title: str
    content_hash: str = ""
    question_count: int = 5
    pass_score: int = 60

class ModuleUpdate(BaseModel):
    topic_id: int
    module_id: int
    title: str
    content_hash: str = ""
    question_count: int = 5
    pass_score: int = 60

class CompleteModuleReq(BaseModel):
    user_address: str
    topic_id: int
    module_id: int
    score: int
    question_count: Optional[int] = None

# ----------------- Topics -----------------
@router.get("/topics")
async def get_topics():
    try:
        topics = learning_service.get_topics()
        return {"success": True, "topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/create")
async def create_topic(payload: TopicCreate):
    try:
        receipt = learning_service.create_topic(payload.title, payload.description)
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/update")
async def update_topic(payload: TopicUpdate):
    try:
        receipt = learning_service.update_topic(payload.topic_id, payload.title, payload.description)
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/delete")
async def delete_topic(payload: dict):
    topic_id = payload.get("topic_id")
    if topic_id is None:
        raise HTTPException(status_code=400, detail="topic_id required")
    try:
        receipt = learning_service.delete_topic(topic_id)
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- Modules -----------------
@router.get("/module/{topic_id}/{module_id}")
async def get_module(topic_id: int, module_id: int):
    try:
        module = learning_service.get_module_by_id(topic_id, module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        return {"success": True, "module": module}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/{topic_id}")
async def get_modules(topic_id: int):
    try:
        modules = learning_service.get_modules_by_topic(topic_id)
        return {"success": True, "modules": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/add")
async def add_module(payload: ModuleCreate):
    try:
        receipt = learning_service.add_module(
            payload.topic_id,
            payload.title,
            payload.content_hash,
            payload.question_count,
            payload.pass_score
        )
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/update")
async def update_module(payload: ModuleUpdate):
    try:
        receipt = learning_service.update_module(
            payload.topic_id,
            payload.module_id,
            payload.title,
            payload.content_hash,
            payload.question_count,
            payload.pass_score
        )
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/delete")
async def delete_module(payload: dict):
    topic_id = payload.get("topic_id")
    module_id = payload.get("module_id")
    if topic_id is None or module_id is None:
        raise HTTPException(status_code=400, detail="topic_id and module_id required")
    try:
        receipt = learning_service.delete_module(topic_id, module_id)
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- Completion & Progress -----------------
@router.post("/complete")
async def complete_module(payload: CompleteModuleReq):
    """
    Mark a module as completed for a user and generate AI quiz.
    """
    try:
        receipt = learning_service.complete_module(
            payload.user_address,
            payload.topic_id,
            payload.module_id,
            payload.score,
            payload.question_count
        )
        return {"success": True, "receipt": receipt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/progress/{user_address}/{topic_id}")
async def get_progress(user_address: str, topic_id: int):
    try:
        progress = learning_service.get_user_progress(user_address, topic_id)
        return {"success": True, "progress": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- AI Content Generation -----------------
@router.post("/generate")
async def generate_module_content(payload: ModuleCreate):
    try:
        content = learning_service.generate_ai_content_simple(payload.topic_id, payload.title)
        return {"success": True, "generated": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
