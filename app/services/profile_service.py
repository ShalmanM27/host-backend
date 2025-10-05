# backend/app/services/profile_service.py

from app.services.web3_utils import get_contract, w3, build_signed_tx, send_signed_transaction
from app import config

PROFILE_ADDRESS = config.PROFILE_ADDRESS
profile_contract = get_contract(PROFILE_ADDRESS, "Profile")


def get_profile_by_address(address: str):
    """
    Read-only call to Profile.getProfile(address).
    """
    try:
        checksum_addr = w3.to_checksum_address(address)
        res = profile_contract.functions.getProfile(checksum_addr).call()
        return {
            "owner": res[0],
            "username": res[1],
            "avatarURI": res[2],
            "bio": res[3],
            "updatedAt": res[4],
            "exists": res[5]
        }
    except Exception as e:
        # Bubble up informative error
        raise Exception(f"Error fetching profile: {str(e)}")


def get_username_owner(username: str):
    """
    Read-only call to check who owns a username.
    """
    try:
        owner = profile_contract.functions.getUsernameOwner(username).call()
        return {"owner": owner}
    except Exception as e:
        raise Exception(f"Error checking username owner: {str(e)}")


def set_profile(username: str, avatarURI: str, bio: str):
    """
    Build, sign and send a transaction to call Profile.setProfile(username, avatarURI, bio).
    NOTE: This uses the server's private key (config.PRIVATE_KEY) to sign.
    In production you should have clients sign transactions themselves.
    Returns the transaction receipt.
    """
    try:
        fn = profile_contract.functions.setProfile(username, avatarURI, bio)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {
            "txHash": receipt.transactionHash.hex(),
            "status": receipt.status,
            "blockNumber": receipt.blockNumber,
        }
    except Exception as e:
        raise Exception(f"Error setting profile on-chain: {str(e)}")
