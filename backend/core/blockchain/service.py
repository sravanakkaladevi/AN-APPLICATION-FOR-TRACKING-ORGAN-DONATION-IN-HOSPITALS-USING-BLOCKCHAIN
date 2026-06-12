import json
import os
from datetime import datetime, timezone

from django.conf import settings
from web3 import Web3


w3 = Web3(Web3.HTTPProvider(settings.GANACHE_RPC_URL))


def _load_contract_artifact():
    artifact_path = settings.ORGAN_DONATION_ARTIFACT_PATH
    if os.path.exists(artifact_path):
        with open(artifact_path, 'r', encoding='utf-8') as artifact_file:
            data = json.load(artifact_file)
            if isinstance(data, list):
                return {'abi': data, 'networks': {}}
            return data

    legacy_abi_path = os.path.join(os.path.dirname(__file__), 'abi.json')
    if os.path.exists(legacy_abi_path):
        with open(legacy_abi_path, 'r', encoding='utf-8') as abi_file:
            return {'abi': json.load(abi_file), 'networks': {}}

    raise FileNotFoundError(
        "OrganDonation contract artifact was not found. Please compile the contract first."
    )


def _get_contract_address(artifact):
    configured_address = settings.ORGAN_DONATION_CONTRACT_ADDRESS.strip()
    if configured_address:
        return Web3.to_checksum_address(configured_address)

    if hasattr(settings, 'ORGAN_DONATION_ARTIFACT_PATH') and settings.ORGAN_DONATION_ARTIFACT_PATH:
        abi_dir = os.path.dirname(settings.ORGAN_DONATION_ARTIFACT_PATH)
        address_path = os.path.join(abi_dir, 'contract_address.txt')
        if os.path.exists(address_path):
            with open(address_path, 'r', encoding='utf-8') as address_file:
                return Web3.to_checksum_address(address_file.read().strip())

    network = artifact.get('networks', {}).get(str(settings.GANACHE_CHAIN_ID), {})
    artifact_address = network.get('address')
    if artifact_address:
        return Web3.to_checksum_address(artifact_address)

    legacy_address_path = os.path.join(os.path.dirname(__file__), 'contract_address.txt')
    if os.path.exists(legacy_address_path):
        with open(legacy_address_path, 'r', encoding='utf-8') as address_file:
            return Web3.to_checksum_address(address_file.read().strip())

    raise ValueError(
        "Contract address not found. Deploy the contract or set "
        "ORGAN_DONATION_CONTRACT_ADDRESS."
    )


def _get_sender_account(preferred_address=None):
    if preferred_address:
        return Web3.to_checksum_address(preferred_address)

    configured_sender = settings.ORGAN_DONATION_FROM_ADDRESS.strip()
    if configured_sender:
        return Web3.to_checksum_address(configured_sender)

    accounts = w3.eth.accounts
    if not accounts:
        raise ValueError("No Ganache accounts available. Start Ganache first.")
    return accounts[0]


def get_contract():
    artifact = _load_contract_artifact()
    return w3.eth.contract(address=_get_contract_address(artifact), abi=artifact['abi'])


def get_blockchain_status():
    status = {
        'connected': False,
        'network': 'Ganache Local',
        'rpc_url': settings.GANACHE_RPC_URL,
        'chain_id': settings.GANACHE_CHAIN_ID,
        'block_number': 'offline',
        'gas_price_gwei': '0.00',
        'accounts': 0,
        'contract_loaded': False,
    }

    try:
        status['connected'] = w3.is_connected()
        if not status['connected']:
            return status

        status['block_number'] = w3.eth.block_number
        status['accounts'] = len(w3.eth.accounts)
        status['gas_price_gwei'] = f"{w3.from_wei(w3.eth.gas_price, 'gwei'):.2f}"
        status['contract_loaded'] = get_contract() is not None
    except Exception:
        status['contract_loaded'] = False

    return status


def register_organ_on_chain(
    donor_id,
    donor_name,
    organ_type,
    hospital_name,
    doctor_name,
    sender_address=None,
):
    if not w3.is_connected():
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    contract = get_contract()
    sender_account = _get_sender_account(sender_address)
    tx_hash = contract.functions.registerDonation(
        str(donor_id),
        donor_name,
        organ_type,
        hospital_name,
        doctor_name,
    ).transact({'from': sender_account})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while registering donation.")

    events = contract.events.DonationRegistered().process_receipt(receipt)
    if not events:
        raise RuntimeError("DonationRegistered event was not emitted by the contract.")

    event_args = events[0]['args']
    transaction_hash = receipt.transactionHash.hex()
    if not transaction_hash.startswith('0x'):
        transaction_hash = f"0x{transaction_hash}"

    return {
        'blockchain_id': event_args['id'],
        'transaction_hash': transaction_hash,
        'block_number': receipt.blockNumber,
        'timestamp': datetime.fromtimestamp(event_args['timestamp'], tz=timezone.utc),
    }


def match_organ_on_chain(organ_id, recipient_hospital_name, matching_admin_address=None):
    if not w3.is_connected():
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    contract = get_contract()
    sender_account = _get_sender_account(matching_admin_address)
    tx_hash = contract.functions.matchOrgan(
        int(organ_id),
        str(recipient_hospital_name),
    ).transact({'from': sender_account})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while matching organ.")

    return {
        'transaction_hash': tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
        'block_number': receipt.blockNumber,
        'status': receipt.status
    }


def transplant_organ_on_chain(organ_id, hospital_address=None):
    if not w3.is_connected():
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    contract = get_contract()
    sender_account = _get_sender_account(hospital_address)
    tx_hash = contract.functions.completeTransplant(int(organ_id)).transact({'from': sender_account})
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while completing transplant.")

    return {
        'transaction_hash': tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
        'block_number': receipt.blockNumber,
        'status': receipt.status
    }


# --- VERSION A COMPATIBILITY WRAPPERS (formerly in blockchain_service.py) ---

def connect_blockchain():
    """Connects to the local Ganache blockchain, caching the connection for performance."""
    if w3.is_connected():
        return w3
    return None


def get_contract_instance(w3_conn):
    """Loads the contract ABI and address and returns a contract instance."""
    try:
        return get_contract()
    except Exception:
        return None


def register_donor(name, organ_type, hospital_id):
    """Registers a donor on the blockchain (for REST API and legacy tests)."""
    if not w3.is_connected():
        return {"error": "Ganache not running"}

    try:
        contract = get_contract()
        account = w3.eth.accounts[0]
        tx_hash = contract.functions.registerDonor(name, organ_type, hospital_id).transact({'from': account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": True,
            "transaction_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }
    except Exception as e:
        return {"error": str(e)}


def get_donor(donor_id):
    """Retrieves donor details from the blockchain (for REST API and legacy tests)."""
    if not w3.is_connected():
        return {"error": "Ganache not running"}

    try:
        contract = get_contract()
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
    """Verifies a transaction by its hash (for REST API and legacy tests)."""
    if not w3.is_connected():
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
