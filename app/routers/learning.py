# backend/app/routers/learning.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.learning_service import generate_quiz_ai, get_module_content

router = APIRouter(prefix="/learning", tags=["Learning"])

class GenerateQuizReq(BaseModel):
    topic_id: int
    module_id: int
    question_count: Optional[int] = 5

@router.post("/generate-quiz")
async def generate_quiz(payload: GenerateQuizReq):
    """
    Generate a multiple-choice quiz for a module using AI.
    Reads content from MongoDB (stored by admin-side pipeline).
    """
    try:
        quiz = generate_quiz_ai(
            payload.topic_id,
            payload.module_id,
            payload.question_count
        )
        return {"success": True, "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic_id}/module/{module_id}")
async def fetch_module_content(topic_id: int, module_id: int):
    """
    Fetch specific module content based on topic_id and module_id
    """
    content = await get_module_content(topic_id, module_id)
    if not content:
        raise HTTPException(status_code=404, detail="Module not found")
    return content
