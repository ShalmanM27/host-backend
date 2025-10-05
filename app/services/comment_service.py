# app/services/comment_service.py
from app.services.web3_utils import get_contract, build_signed_tx, send_signed_transaction
from app import config

COMMENT_ADDRESS = config.COMMENT_ADDRESS
comment_contract = get_contract(COMMENT_ADDRESS, "Comment")

def create_comment(post_id: int, content: str, media_hash: str = ""):
    try:
        fn = comment_contract.functions.createComment(post_id, content, media_hash)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise Exception(f"Error creating comment: {str(e)}")

def update_comment(comment_id: int, content: str, media_hash: str = ""):
    try:
        fn = comment_contract.functions.updateComment(comment_id, content, media_hash)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise Exception(f"Error updating comment: {str(e)}")

def delete_comment(comment_id: int):
    try:
        fn = comment_contract.functions.deleteComment(comment_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return {"txHash": receipt.transactionHash.hex(), "status": receipt.status}
    except Exception as e:
        raise Exception(f"Error deleting comment: {str(e)}")

def get_comments(post_id: int):
    try:
        res = comment_contract.functions.getComments(post_id).call()
        comments = []
        for c in res:
            comments.append({
                "id": c[0],
                "postId": c[1],
                "author": c[2],
                "content": c[3],
                "mediaHash": c[4],
                "timestamp": c[5],
                "exists": c[6]
            })
        return comments
    except Exception as e:
        raise Exception(f"Error fetching comments: {str(e)}")
