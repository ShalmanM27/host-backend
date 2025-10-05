# app/services/streak_service.py
from web3 import Web3
from app.services.web3_utils import get_contract, build_signed_tx, send_signed_transaction
from app import config

STREAK_ADDRESS = config.STREAK_ADDRESS
streak_contract = get_contract(STREAK_ADDRESS, "Streak")


# ----------------- COMPLETE TASK -----------------
def complete_task(user_address: str):
    """
    Marks today's task as completed for the given user.
    """
    try:
        # Convert address to checksum (optional, for consistency)
        Web3.to_checksum_address(user_address)

        fn = streak_contract.functions.completeTask()  # no extra parameters
        signed = build_signed_tx(fn)  # remove user_address argument
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise e
    
# ----------------- GET CURRENT STREAK -----------------
def get_current_streak(user_address: str):
    """
    Returns the current streak count for the given user.
    """
    try:
        user_address = Web3.to_checksum_address(user_address)
        streak = streak_contract.functions.getCurrentStreak(user_address).call()
        return streak
    except Exception as e:
        if "checksum" in str(e):
            raise ValueError("Invalid address format. Please provide a valid checksum address.")
        raise e


# ----------------- GET LAST 7 DAYS STATUS -----------------
def get_last_7_days_status(user_address: str):
    """
    Returns a boolean array representing completion status for the last 7 days.
    """
    try:
        user_address = Web3.to_checksum_address(user_address)
        status = streak_contract.functions.getLast7DaysStatus(user_address).call()
        return status
    except Exception as e:
        if "checksum" in str(e):
            raise ValueError("Invalid address format. Please provide a valid checksum address.")
        raise e
