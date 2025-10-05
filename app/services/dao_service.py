# app/services/dao_service.py
from web3 import Web3
from app.services.web3_utils import get_contract, build_signed_tx, send_signed_transaction
from app import config

DAO_ADDRESS = config.DAO_ADDRESS
dao_contract = get_contract(DAO_ADDRESS, "DAO")


# ----------------- PROPOSAL CREATION -----------------
def create_proposal(description: str, duration: int):
    """
    Creates a new DAO proposal.
    """
    try:
        fn = dao_contract.functions.createProposal(description, duration)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise e


# ----------------- VOTING -----------------
def vote(proposal_id: int, support: bool):
    """
    Cast a vote on a proposal.
    support = True -> Yes
    support = False -> No
    """
    try:
        fn = dao_contract.functions.vote(proposal_id, support)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise e


def execute_proposal(proposal_id: int):
    """
    Executes a proposal after voting period ends.
    """
    try:
        fn = dao_contract.functions.executeProposal(proposal_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise e


# ----------------- GET SINGLE PROPOSAL -----------------
def get_proposal(proposal_id: int):
    """
    Fetches a single proposal by ID and returns a structured object.
    """
    try:
        p = dao_contract.functions.getProposal(proposal_id).call()
        return {
            "id": p[0],
            "proposer": p[1],
            "description": p[2],
            "startTime": p[3],
            "endTime": p[4],
            "yesVotes": p[5],
            "noVotes": p[6],
            "executed": p[7],
        }
    except Exception as e:
        raise e


# ----------------- GET USER PROPOSALS -----------------
def get_user_proposals(user_address: str):
    """
    Fetches all proposals created by a specific user.
    Returns a list of structured objects.
    """
    try:
        user_address = Web3.to_checksum_address(user_address)
        raw_proposals = dao_contract.functions.getUserProposals(user_address).call()

        proposals = []
        for p in raw_proposals:
            proposals.append({
                "id": p[0],
                "proposer": p[1],
                "description": p[2],
                "startTime": p[3],
                "endTime": p[4],
                "yesVotes": p[5],
                "noVotes": p[6],
                "executed": p[7],
            })
        return proposals

    except Exception as e:
        if "checksum" in str(e):
            raise ValueError("Invalid address format. Please provide a valid checksum address.")
        raise e


# ----------------- GET LIVE PROPOSALS (EXCLUDING USER) -----------------
def get_live_proposals_excluding(user_address: str):
    """
    Returns ongoing proposals excluding those created by the given user.
    """
    try:
        user_address = Web3.to_checksum_address(user_address)
        raw_proposals = dao_contract.functions.getOngoingProposalsExcluding(user_address).call()

        proposals = []
        for p in raw_proposals:
            proposals.append({
                "id": p[0],
                "proposer": p[1],
                "description": p[2],
                "startTime": p[3],
                "endTime": p[4],
                "yesVotes": p[5],
                "noVotes": p[6],
                "executed": p[7],
            })
        return proposals

    except Exception as e:
        if "checksum" in str(e):
            raise ValueError("Invalid address format. Please provide a valid checksum address.")
        raise e


# ----------------- GET USER VOTE -----------------
def get_user_vote(proposal_id: int, user_address: str):
    """
    Returns the vote of a user for a given proposal.
    0 = no vote, 1 = yes, 2 = no
    """
    try:
        user_address = Web3.to_checksum_address(user_address)
        vote_type = dao_contract.functions.getUserVote(proposal_id, user_address).call()
        return vote_type
    except Exception as e:
        if "checksum" in str(e):
            raise ValueError("Invalid address format. Please provide a valid checksum address.")
        raise e
