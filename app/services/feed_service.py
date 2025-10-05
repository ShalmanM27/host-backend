from app.services.web3_utils import get_contract, send_signed_transaction, build_signed_tx
from app import config
from web3 import Web3

FEED_ADDRESS = config.FEED_ADDRESS
feed_contract = get_contract(FEED_ADDRESS, "Feed")


# Create Post
def create_post(content: str, media_hash: str = ""):
    try:
        fn = feed_contract.functions.createPost(content, media_hash)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error creating post: {str(e)}")


# Update Post
def update_post(post_id: int, content: str, media_hash: str = ""):
    try:
        fn = feed_contract.functions.updatePost(post_id, content, media_hash)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error updating post: {str(e)}")


# Delete Post
def delete_post(post_id: int):
    try:
        fn = feed_contract.functions.deletePost(post_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error deleting post: {str(e)}")


# Like Post
def like_post(post_id: int):
    try:
        fn = feed_contract.functions.likePost(post_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error liking post: {str(e)}")


# Remove Like
def remove_like(post_id: int):
    try:
        fn = feed_contract.functions.removeLike(post_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error removing like: {str(e)}")


# Dislike Post
def dislike_post(post_id: int):
    try:
        fn = feed_contract.functions.dislikePost(post_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error disliking post: {str(e)}")


# Remove Dislike
def remove_dislike(post_id: int):
    try:
        fn = feed_contract.functions.removeDislike(post_id)
        signed = build_signed_tx(fn)
        receipt = send_signed_transaction(signed)
        return dict(txHash=receipt.transactionHash.hex(), status=receipt.status)
    except Exception as e:
        raise Exception(f"Error removing dislike: {str(e)}")


# Get a single post
def get_post(post_id: int, user_address: str = None):
    try:
        res = feed_contract.functions.getPost(post_id).call()
        post = {
            "id": res[0],
            "owner": res[1],  # changed from "author" to "owner"
            "content": res[2],
            "mediaHash": res[3],
            "created_at": res[4],  # changed from "timestamp" to "created_at"
            "likeCount": res[5],
            "dislikeCount": res[6],
            "exists": res[7]
        }

        if user_address:
            user_address = Web3.to_checksum_address(user_address)
            liked = feed_contract.functions.likedBy(post_id, user_address).call()
            disliked = feed_contract.functions.dislikedBy(post_id, user_address).call()
            post["likedByUser"] = liked
            post["dislikedByUser"] = disliked
        else:
            post["likedByUser"] = False
            post["dislikedByUser"] = False

        return post
    except Exception as e:
        raise Exception(f"Error fetching post {post_id}: {str(e)}")


# Get latest N posts
def get_latest_posts(count: int = 10, user_address: str = None):
    try:
        res = feed_contract.functions.getLatestPosts(count).call()
        posts = []

        if user_address:
            user_address = Web3.to_checksum_address(user_address)

        post_ids = res[0]
        authors = res[1]
        contents = res[2]
        mediaHashes = res[3]
        timestamps = res[4]
        likeCounts = res[5]
        dislikeCounts = res[6]

        liked_status = []
        disliked_status = []
        if user_address:
            for pid in post_ids:
                liked_status.append(feed_contract.functions.likedBy(pid, user_address).call())
                disliked_status.append(feed_contract.functions.dislikedBy(pid, user_address).call())

        for i in range(len(post_ids)):
            post = {
                "id": post_ids[i],
                "owner": authors[i],  # changed from "author" to "owner"
                "content": contents[i],
                "mediaHash": mediaHashes[i],
                "created_at": timestamps[i],  # changed from "timestamp" to "created_at"
                "likeCount": likeCounts[i],
                "dislikeCount": dislikeCounts[i],
                "likedByUser": liked_status[i] if user_address else False,
                "dislikedByUser": disliked_status[i] if user_address else False
            }
            posts.append(post)

        return posts
    except Exception as e:
        raise Exception(f"Error fetching latest posts: {str(e)}")
        raise Exception(f"Error fetching latest posts: {str(e)}")
