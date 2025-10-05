from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileUpdateRequest(BaseModel):
    username: str
    avatarURI: str = ""
    bio: str = ""


@router.get("/")
async def get_profile(address: str = Query(...)):
    """
    Get the profile for a given address.
    """
    try:
        profile = profile_service.get_profile_by_address(address)
        return {"success": True, "data": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
async def update_profile(address: str = Query(...), body: ProfileUpdateRequest = None):
    """
    Update the profile for a given address.
    """
    try:
        # In production, you'd have the client sign the transaction.
        res = profile_service.set_profile(body.username, body.avatarURI, body.bio)
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))