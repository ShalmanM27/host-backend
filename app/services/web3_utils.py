# app/services/web3_utils.py
import json
from web3 import Web3
from eth_account import Account
from pathlib import Path
from app import config

# Setup web3 provider
w3 = Web3(Web3.HTTPProvider(config.HELA_RPC))
if not w3.is_connected():
    # Fail fast with a clear message
    raise RuntimeError("Unable to connect to HeLa RPC at " + str(config.HELA_RPC))

# Server account (used to sign transactions from backend)
ACCOUNT = Account.from_key(config.PRIVATE_KEY)
CHAIN_ID = w3.eth.chain_id

def load_abi(name: str):
    p = Path(__file__).resolve().parents[1] / "abis" / f"{name}.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_contract(address: str, abi_name: str):
    abi = load_abi(abi_name)
    return w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

def build_signed_tx(contract_function, tx_params=None, value=0):
    """
    Build and sign a transaction for the given contract function using the server ACCOUNT.
    Returns the signed transaction object.
    """
    if tx_params is None:
        tx_params = {}
    # default tx fields
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    tx_defaults = {
        "chainId": CHAIN_ID,
        "gas": tx_params.get("gas", 600000),
        "gasPrice": tx_params.get("gasPrice", w3.eth.gas_price),
        "nonce": tx_params.get("nonce", nonce),
        "value": int(value)
    }
    built = contract_function.build_transaction(tx_defaults)
    signed = Account.sign_transaction(built, config.PRIVATE_KEY)
    return signed

def send_signed_transaction(signed_tx):
    """
    Send signed raw transaction and wait for receipt (with a timeout).
    Returns the transaction receipt.
    """
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    # wait for receipt (polling)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    return receipt
