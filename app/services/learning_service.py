# backend/app/services/learning_service.py

from app.services.web3_utils import get_contract, build_signed_tx, send_signed_transaction
from app import config
import logging
import requests
import os
import json
from web3 import Web3  # ✅ For checksum addresses
from app.services.db import db  # ✅ Import MongoDB Atlas connection from db.py

logger = logging.getLogger(__name__)

# ----------------- MongoDB Setup -----------------
modules_col = db["modules_content"]  # stores module content and quizzes

# ----------------- Web3 Contract -----------------
LEARNING_ADDRESS = getattr(config, "LEARNING_ADDRESS", None)
learning_contract = None
try:
    if LEARNING_ADDRESS:
        learning_contract = get_contract(LEARNING_ADDRESS, "Learning")
    else:
        logger.warning("LEARNING_ADDRESS not set; learning_contract will be None.")
except Exception as e:
    logger.exception("Failed to get learning contract: %s", e)
    learning_contract = None

# ----------------- AI Setup -----------------
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ----------------- AI Content Generation -----------------
def generate_ai_content_simple(topic_id: int, module_title: str):
    topic_name = f"Topic {topic_id}" if topic_id else "General"
    
    prompt = f"""
    Generate simple, easy-to-read, and fun learning content for a module titled '{module_title}' 
    under topic '{topic_name}'. 

    Requirements:
    - Write short sentences and break content into small paragraphs.
    - Use headings and subheadings where appropriate.
    - Include numbered or bulleted lists for steps, tips, or examples.
    - Use simple words; avoid jargon or complex explanations.
    - Add relatable examples to illustrate concepts.
    - Keep the tone friendly and encouraging, like explaining to a beginner.
    - Make it scannable so the user can quickly grasp key points.
    """

    if not OPENROUTER_KEY:
        logger.warning("OPENROUTER_KEY not set, returning placeholder content.")
        return f"Learning module: {module_title}. (AI disabled, placeholder content.)"

    payload = {
        "model": "x-ai/grok-4-fast",
        "messages": [{"role": "user", "content": [{"type":"text","text": prompt}]}]
    }
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        if isinstance(text, list):
            text = "".join([c.get("text","") for c in text])
        return text
    except Exception as e:
        logger.exception("AI content generation failed: %s", e)
        return f"Learning module: {module_title}. (AI failed, placeholder content.)"

def generate_quiz_ai(topic_id: int, module_id: int, question_count: int = 5):
    """
    Generate a multiple-choice quiz from the module content using AI.
    Returns a list of objects: [{q:..., options:[...], answerIndex:...}, ...]
    """
    module_entry = modules_col.find_one({"module_id": module_id, "topic_id": topic_id})
    content_text = module_entry["content"] if module_entry else "No content available"

    prompt = f"""
    Generate {question_count} multiple choice questions from this content.
    Return the result strictly as valid JSON: a list of objects with
    "q" (question string), "options" (array of 4 options), "answerIndex" (0-based index of correct option).

    Content:
    {content_text}

    Example format:
    [
      {{"q":"Sample question?","options":["A","B","C","D"],"answerIndex":1}} ,
      ...
    ]
    """

    if not OPENROUTER_KEY:
        # Fallback placeholder quiz
        return [{"q": f"Question {i+1}", "options": ["A","B","C","D"], "answerIndex":0} for i in range(question_count)]

    payload = {
        "model": "x-ai/grok-4-fast",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    }
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]

        if isinstance(text, list):
            # If returned as a list of text chunks, join
            text = "".join([c.get("text", "") for c in text])

        # Attempt to parse JSON
        try:
            quiz_list = json.loads(text)
            if isinstance(quiz_list, list):
                # Ensure each question has required fields
                valid_quiz = []
                for q in quiz_list:
                    if "q" in q and "options" in q and "answerIndex" in q:
                        valid_quiz.append({
                            "q": q["q"],
                            "options": q["options"][:4],  # ensure max 4 options
                            "answerIndex": int(q["answerIndex"])
                        })
                if valid_quiz:
                    return valid_quiz
        except Exception:
            pass

        # Fallback placeholder if parsing fails
        return [{"q": f"Question {i+1}", "options": ["A","B","C","D"], "answerIndex":0} for i in range(question_count)]

    except Exception as e:
        logger.exception("AI quiz generation failed: %s", e)
        # Fallback placeholder quiz
        return [{"q": f"Question {i+1}", "options": ["A","B","C","D"], "answerIndex":0} for i in range(question_count)]

# ----------------- Topics -----------------
def get_topics():
    if learning_contract is None:
        return []
    try:
        res = learning_contract.functions.getAllTopics().call()
        ids, titles, descriptions, totalModules, existsArr = res
        topics = []
        for i in range(len(ids)):
            if not existsArr[i]:
                continue
            topics.append({
                "id": int(ids[i]),
                "title": titles[i],
                "description": descriptions[i],
                "totalModules": int(totalModules[i])
            })
        return topics
    except Exception as e:
        logger.exception("Error fetching topics: %s", e)
        return []

def create_topic(title: str, description: str):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    fn = learning_contract.functions.createTopic(title, description)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)
    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status)}

def update_topic(topic_id: int, title: str, description: str):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    fn = learning_contract.functions.updateTopic(topic_id, title, description)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)
    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status)}

def delete_topic(topic_id: int):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    fn = learning_contract.functions.deleteTopic(topic_id)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)
    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status)}

# ----------------- Modules -----------------
def get_modules_by_topic(topic_id: int):
    if learning_contract is None:
        return []
    try:
        res = learning_contract.functions.getModulesByTopic(topic_id).call()
        ids, titles, contentHashes, questionCounts, passScores, existsArr = res
        modules = []
        for i in range(len(ids)):
            if not existsArr[i]:
                continue
            content_entry = modules_col.find_one({"module_id": int(ids[i]), "topic_id": topic_id})
            content_text = content_entry["content"] if content_entry else ""
            modules.append({
                "id": int(ids[i]),
                "topic_id": topic_id,
                "module_id": int(ids[i]),
                "module_title": titles[i],
                "content": content_text,
                "questionCount": int(questionCounts[i]),
                "passScore": int(passScores[i])
            })
        return modules
    except Exception as e:
        logger.exception("Error fetching modules: %s", e)
        return []

def get_module_by_id(topic_id: int, module_id: int):
    module_entry = modules_col.find_one({"module_id": module_id, "topic_id": topic_id})
    if not module_entry:
        return None
    return {
        "id": module_entry.get("module_id"),
        "topic_id": module_entry.get("topic_id"),
        "module_id": module_entry.get("module_id"),
        "module_title": module_entry.get("module_title"),
        "content": module_entry.get("content", ""),
        "questionCount": module_entry.get("questionCount", 5),
        "passScore": module_entry.get("passScore", 60)
    }

def add_module(topic_id: int, title: str, content_hash: str, question_count: int, pass_score: int):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")

    content_text = generate_ai_content_simple(topic_id, title)
    module_doc = {
        "topic_id": topic_id,
        "module_id": None,
        "module_title": title,
        "content": content_text,
        "questionCount": question_count,
        "passScore": pass_score
    }
    insert_res = modules_col.insert_one(module_doc)

    fn = learning_contract.functions.addModule(topic_id, title, content_hash, question_count, pass_score)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)

    try:
        res = learning_contract.functions.getModulesByTopic(topic_id).call()
        ids, _, _, _, _, existsArr = res
        module_id_assigned = int(ids[-1]) if ids else None
    except Exception as e:
        logger.exception("Failed to fetch module ID from contract: %s", e)
        module_id_assigned = None

    modules_col.update_one({"_id": insert_res.inserted_id}, {"$set": {"module_id": module_id_assigned}})

    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status), "module_id": module_id_assigned}

def update_module(topic_id: int, module_id: int, title: str, content_hash: str, question_count: int, pass_score: int):
    content_text = generate_ai_content_simple(topic_id, title)
    modules_col.update_one({"module_id": module_id, "topic_id": topic_id}, {"$set": {"content": content_text}}, upsert=True)

    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    fn = learning_contract.functions.updateModule(topic_id, module_id, title, content_hash, question_count, pass_score)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)
    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status)}

def delete_module(topic_id: int, module_id: int):
    modules_col.delete_one({"module_id": module_id, "topic_id": topic_id})
    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    fn = learning_contract.functions.deleteModule(topic_id, module_id)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)
    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status)}

def complete_module(user_address: str, topic_id: int, module_id: int, score: int, question_count: int = None):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")

    checksum_address = Web3.to_checksum_address(user_address)
    fn = learning_contract.functions.completeModule(topic_id, module_id, score)
    signed = build_signed_tx(fn)
    receipt = send_signed_transaction(signed)

    if question_count is None:
        content_entry = modules_col.find_one({"module_id": module_id, "topic_id": topic_id})
        question_count = content_entry.get("questionCount", 5) if content_entry else 5

    try:
        question_count = int(question_count)
    except Exception:
        question_count = 5

    quiz = generate_quiz_ai(topic_id, module_id, question_count)
    modules_col.update_one({"module_id": module_id, "topic_id": topic_id}, {"$set": {"last_quiz": quiz}}, upsert=True)

    return {"txHash": receipt.transactionHash.hex(), "status": int(receipt.status), "quiz": quiz}

def get_user_progress(user_address: str, topic_id: int):
    if learning_contract is None:
        raise Exception("Learning contract not configured.")
    try:
        checksum_address = Web3.to_checksum_address(user_address)
        res = learning_contract.functions.getUserProgress(checksum_address, topic_id).call()
        return {"completedModules": res}
    except Exception as e:
        logger.exception("Error fetching user progress: %s", e)
        raise
