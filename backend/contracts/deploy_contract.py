from web3 import Web3
import json

# For local development with Ganache, the default RPC server is usually HTTP://127.0.0.1:7545
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if w3.is_connected():
    print("Connected to Ethereum network (Ganache)")
else:
    print("Cannot connect to Ethereum network. Please ensure Ganache is running on port 7545.")
    exit(1)

# Default ganache account
w3.eth.default_account = w3.eth.accounts[0]

with open("abi.json", "r") as file:
    abi = json.load(file)

with open("bytecode.txt", "r") as file:
    bytecode = file.read()

# Deploy contract
OrganDonation = w3.eth.contract(abi=abi, bytecode=bytecode)
print("Deploying Contract...")

tx_hash = OrganDonation.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"Contract Deployed At: {contract_address}")

# Save the address and ABI where Django can read it
django_blockchain_dir = "../core/blockchain"
import os
os.makedirs(django_blockchain_dir, exist_ok=True)

with open(f"{django_blockchain_dir}/contract_address.txt", "w") as f:
    f.write(contract_address)

with open(f"{django_blockchain_dir}/abi.json", "w") as f:
    json.dump(abi, f)

print(f"Contract address and ABI saved to {django_blockchain_dir}")
