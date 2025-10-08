import os
import json
import logging
import requests
from app.services.db import db  # ✅ MongoDB Atlas connection
from app import config

logger = logging.getLogger(__name__)

# ----------------- MongoDB -----------------
modules_col = db["modules_content"]  # Stores AI-generated content and quizzes

# ----------------- Web3 Contract -----------------
LEARNING_ADDRESS = getattr(config, "LEARNING_ADDRESS", None)
learning_contract = None

# ----------------- AI Setup -----------------
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# =====================================================
# AI CONTENT & QUIZ GENERATION
# =====================================================
def generate_ai_content_simple(topic_id: int, module_title: str) -> str:
    """Generate short, easy-to-read learning content."""
    topic_name = f"Topic {topic_id}" if topic_id else "General"
    prompt = f"""
    Generate easy, beginner-friendly educational content for a module titled '{module_title}' under topic '{topic_name}'.

    Guidelines:
    - Use short sentences, simple words, and headings.
    - Add examples and bullet points where helpful.
    - Keep tone positive and clear.
    """

    if not OPENROUTER_KEY:
        logger.warning("OPENROUTER_API_KEY not found. Returning placeholder content.")
        return f"Learning content for {module_title} (placeholder - AI disabled)."

    payload = {
        "model": "x-ai/grok-4-fast",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        if isinstance(text, list):
            text = "".join([c.get("text", "") for c in text])
        return text
    except Exception as e:
        logger.exception("AI content generation failed: %s", e)
        return f"Learning content for {module_title} (AI error)."

def generate_quiz_ai(topic_id: int, module_id: int, question_count: int = 5):
    """Generate multiple choice questions from module content."""
    module_entry = modules_col.find_one({"topic_id": topic_id, "module_id": module_id})
    content_text = module_entry["content"] if module_entry else "No content available."
    print(content_text)
    prompt = f"""
    Create {question_count} multiple-choice questions from this text.
    Return valid JSON with:
    - q: question string
    - options: 4 choices
    - answerIndex: 0-based index of correct option

    Content:
    {content_text}
    """

    if not OPENROUTER_KEY:
        return [{"q": f"Question {i+1}", "options": ["A", "B", "C", "D"], "answerIndex": 0} for i in range(question_count)]

    payload = {
        "model": "x-ai/grok-4-fast",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]

        if isinstance(text, list):
            text = "".join([c.get("text", "") for c in text])

        quiz_list = json.loads(text)
        valid_quiz = []
        for q in quiz_list:
            if "q" in q and "options" in q and "answerIndex" in q:
                valid_quiz.append({
                    "q": q["q"],
                    "options": q["options"][:4],
                    "answerIndex": int(q["answerIndex"]),
                })
        return valid_quiz or [{"q": f"Question {i+1}", "options": ["A", "B", "C", "D"], "answerIndex": 0} for i in range(question_count)]

    except Exception as e:
        logger.exception("AI quiz generation failed: %s", e)
        return [{"q": f"Question {i+1}", "options": ["A", "B", "C", "D"], "answerIndex": 0} for i in range(question_count)]

async def get_module_content(topic_id: int, module_id: int):
    """
    Retrieve module content (title, markdown, etc.) from MongoDB for the given topic and module.
    """
    collection = db["modules_content"]  # use your actual collection name
    doc = collection.find_one({"topic_id": topic_id, "module_id": module_id})

    if not doc:
        return None

    # Return structured data
    return {
        "module_title": doc.get("module_title"),
        "content": doc.get("content"),
        "questionCount": doc.get("questionCount"),
        "passScore": doc.get("passScore"),
    }
