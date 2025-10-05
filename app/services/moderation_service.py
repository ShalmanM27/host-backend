# backend/app/services/moderation_service.py

from app.services.web3_utils import get_contract, build_signed_tx, send_signed_transaction
from app import config

MODERATION_ADDRESS = config.MODERATION_ADDRESS

# Load the Moderation contract
moderation_contract = get_contract(MODERATION_ADDRESS, "Moderation")


def flag_content(content_id: int):
    """
    Calls Moderation.flagContent(contentId)
    """
    try:
        fn = moderation_contract.functions.flagContent(content_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {
            "txHash": receipt.transactionHash.hex(),
            "status": receipt.status
        }
    except Exception as e:
        raise Exception(f"Error flagging content: {str(e)}")


def resolve_flag(content_id: int, remove: bool):
    """
    Calls Moderation.resolveFlag(contentId, remove)
    """
    try:
        fn = moderation_contract.functions.resolveFlag(content_id, remove)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {
            "txHash": receipt.transactionHash.hex(),
            "status": receipt.status
        }
    except Exception as e:
        raise Exception(f"Error resolving flag: {str(e)}")


def get_flags(content_id: int):
    """
    Calls Moderation.getFlags(contentId) → returns array of (contentId, flagger, resolved)
    """
    try:
        flags = moderation_contract.functions.getFlags(content_id).call()
        result = []
        for f in flags:
            result.append({
                "contentId": f[0],
                "flagger": f[1],
                "resolved": f[2],
            })
        return result
    except Exception as e:
        raise Exception(f"Error retrieving flags: {str(e)}")
