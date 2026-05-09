import json
import os
from web3 import Web3
from web3.exceptions import Web3Exception

# Configuration
GANACHE_URL = "http://127.0.0.1:7545"

"""
SOFTWARE ARCHITECTURE NOTE:
---------------------------
We separate the 'backend' logic from 'blockchain' artifacts to maintain a clean MVC-like structure.
- 'backend/': Contains the Django application logic and service layers.
- 'blockchain/': Contains smart contracts, compiled ABI files, and deployment scripts.
- 'blockchain/compiled/': ABI files are stored separately to keep the repository clean and 
  allow easy versioning of contract updates without touching backend code.
"""

# Path to compiled artifacts (relative to this file)
# BASE_DIR points to the project root (organ_donation/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILED_PATH = os.path.join(BASE_DIR, "blockchain", "compiled")

def connect_blockchain():
    """Connects to the local Ganache blockchain."""
    try:
        w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        if w3.is_connected():
            return w3
        else:
            raise ConnectionError("Could not connect to Ganache. Ensure it is running at http://127.0.0.1:7545")
    except Exception as e:
        print(f"Error connecting to blockchain: {e}")
        return None

def get_contract_instance(w3):
    """Loads the contract ABI and address and returns a contract instance."""
    try:
        abi_path = os.path.join(COMPILED_PATH, "abi.json")
        address_path = os.path.join(COMPILED_PATH, "contract_address.txt")

        if not os.path.exists(abi_path) or not os.path.exists(address_path):
            raise FileNotFoundError("Contract ABI or Address not found. Please run deploy_contract.py first.")

        with open(abi_path, "r") as f:
            abi = json.load(f)
        with open(address_path, "r") as f:
            address = f.read().strip()

        return w3.eth.contract(address=address, abi=abi)
    except Exception as e:
        print(f"Error loading contract: {e}")
        return None

def register_donor(name, organ_type, hospital_id):
    """Registers a donor on the blockchain."""
    w3 = connect_blockchain()
    if not w3:
        return {"error": "Ganache not running"}

    try:
        contract = get_contract_instance(w3)
        if not contract:
            return {"error": "Contract not deployed"}

        # Use the first account for transaction
        account = w3.eth.accounts[0]
        
        # Build and send transaction
        tx_hash = contract.functions.registerDonor(name, organ_type, hospital_id).transact({'from': account})
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": True,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }
    except Web3Exception as e:
        return {"error": f"Blockchain transaction failure: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

def get_donor(donor_id):
    """Retrieves donor details from the blockchain."""
    w3 = connect_blockchain()
    if not w3:
        return {"error": "Ganache not running"}

    try:
        contract = get_contract_instance(w3)
        donor_data = contract.functions.getDonor(int(donor_id)).call()
        
        return {
            "id": donor_data[0],
            "name": donor_data[1],
            "organ_type": donor_data[2],
            "hospital_id": donor_data[3],
            "is_approved": donor_data[4],
            "timestamp": donor_data[5]
        }
    except Exception as e:
        return {"error": f"Failed to retrieve donor: {str(e)}"}

def verify_transaction(tx_hash):
    """Verifies a transaction by its hash."""
    w3 = connect_blockchain()
    if not w3:
        return {"error": "Ganache not running"}

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return {
            "status": "Success" if receipt.status == 1 else "Failed",
            "block_number": receipt.blockNumber,
            "from": receipt['from'],
            "to": receipt['to']
        }
    except Exception as e:
        return {"error": f"Transaction not found or invalid: {str(e)}"}
