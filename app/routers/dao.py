# app/routers/dao.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services import dao_service

router = APIRouter(prefix="/dao", tags=["DAO"])

# ----------------- MODELS -----------------
class ProposalCreate(BaseModel):
    description: str
    duration: int


class ProposalVote(BaseModel):
    proposal_id: int
    support: bool  # True = like, False = dislike


class ProposalAction(BaseModel):
    proposal_id: int


class UserAddress(BaseModel):
    user_address: str


# ----------------- ROUTES -----------------

@router.post("/create")
async def create_proposal(data: ProposalCreate):
    receipt = dao_service.create_proposal(data.description, data.duration)
    return {"success": True, "receipt": receipt}


@router.post("/vote")
async def vote(data: ProposalVote):
    receipt = dao_service.vote(data.proposal_id, data.support)
    return {"success": True, "receipt": receipt}


@router.post("/execute")
async def execute(data: ProposalAction):
    receipt = dao_service.execute_proposal(data.proposal_id)
    return {"success": True, "receipt": receipt}


@router.get("/{proposal_id}")
async def get_proposal(proposal_id: int):
    proposal = dao_service.get_proposal(proposal_id)
    return {"success": True, "proposal": proposal}


@router.get("/user/{user_address}")
async def get_user_proposals(user_address: str):
    try:
        proposals = dao_service.get_user_proposals(user_address)
        return {"success": True, "proposals": proposals}
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": "Internal server error"}


@router.get("/live/{user_address}")
async def get_live_proposals(user_address: str):
    try:
        proposals = dao_service.get_live_proposals_excluding(user_address)
        return {"success": True, "proposals": proposals}
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": "Internal server error"}


@router.get("/vote/{proposal_id}/{user_address}")
async def get_user_vote(proposal_id: int, user_address: str):
    try:
        vote_type = dao_service.get_user_vote(proposal_id, user_address)
        return {"success": True, "voteType": vote_type}  # 0=no vote, 1=like, 2=dislike
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": "Internal server error"}
