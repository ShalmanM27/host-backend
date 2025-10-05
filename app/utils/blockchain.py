from web3 import Web3
from config import *

# Connect to Hela Testnet
w3 = Web3(Web3.HTTPProvider(HELA_RPC))
account = w3.eth.account.from_key(PRIVATE_KEY)

def get_contract(address, abi):
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
