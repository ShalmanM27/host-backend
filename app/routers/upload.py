from fastapi import APIRouter, HTTPException
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()  # loads PINATA_JWT from .env

router = APIRouter(prefix="/pinata", tags=["Pinata"])

PINATA_JWT = os.getenv("PINATA_JWT")
PINATA_SIGN_URL = "https://uploads.pinata.cloud/v3/files/sign"

@router.get("/signed-url")
def get_signed_url():
    """
    Returns a presigned URL to upload a file directly from frontend.
    """
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }

    payload = {
        "expires": 60,  # seconds
        "name": "client_file",  # optional file name
        "mimeTypes": ["image/*"],  # optional
        "maxFileSize": 5000000,  # optional
        "date": int(time.time())  # REQUIRED: current timestamp
    }

    try:
        response = requests.post(PINATA_SIGN_URL, json=payload, headers=headers)
        print("Pinata status code:", response.status_code)
        print("Pinata response text:", response.text)
        response.raise_for_status()
        data = response.json()
        return {"url": data.get("data")}
    except requests.HTTPError as e:
        print("HTTPError:", e)
        if e.response is not None:
            print("Response status code:", e.response.status_code)
            print("Response body:", e.response.text)
        raise HTTPException(
            status_code=e.response.status_code if e.response else 500,
            detail=f"Pinata HTTPError: {e}"
        )
    except Exception as e:
        print("Exception:", e)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
