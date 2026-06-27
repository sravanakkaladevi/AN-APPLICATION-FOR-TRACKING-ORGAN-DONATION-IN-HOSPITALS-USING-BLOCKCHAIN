import json
import os
import logging
from datetime import datetime, timezone

from django.conf import settings
from web3 import Web3

logger = logging.getLogger(__name__)

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
    accounts = w3.eth.accounts
    if not accounts:
        raise ValueError("No Ganache accounts available. Start Ganache first.")

    if preferred_address:
        checksummed = Web3.to_checksum_address(preferred_address)
        if checksummed in accounts:
            logger.info("Using preferred sender account: %s", checksummed)
            return checksummed
        else:
            logger.warning(
                "Preferred address %s is not in Ganache accounts. Falling back to default/first account.",
                checksummed,
            )

    configured_sender = settings.ORGAN_DONATION_FROM_ADDRESS.strip() if hasattr(settings, 'ORGAN_DONATION_FROM_ADDRESS') else ''
    if configured_sender:
        checksummed_sender = Web3.to_checksum_address(configured_sender)
        if checksummed_sender in accounts:
            logger.info("Using configured sender account: %s", checksummed_sender)
            return checksummed_sender
        else:
            logger.warning(
                "Configured address %s is not in Ganache accounts. Falling back to first account.",
                checksummed_sender,
            )

    logger.info("Using fallback first Ganache account: %s", accounts[0])
    return accounts[0]


def get_contract():
    artifact = _load_contract_artifact()
    return w3.eth.contract(address=_get_contract_address(artifact), abi=artifact['abi'])


# Verify connection on module load
logger.info("Initializing Web3 provider at %s", settings.GANACHE_RPC_URL)
try:
    if w3.is_connected():
        logger.info("Connected to Ganache: True")
        logger.info("Ganache Block Number: %s", w3.eth.block_number)
        artifact_init = _load_contract_artifact()
        logger.info("Contract ABI Loaded: True")
        logger.info("Contract Deployed Address: %s", _get_contract_address(artifact_init))
    else:
        logger.warning("Connected to Ganache: False (RPC at %s)", settings.GANACHE_RPC_URL)
except Exception as e:
    logger.error("Error during Web3 initialization check: %s", e)


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
    logger.info("blockchain_service.register_organ_on_chain called.")
    connected = w3.is_connected()
    logger.info("Connected to Ganache: %s", connected)
    if not connected:
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    try:
        contract = get_contract()
        logger.info("Contract Loaded: True")
    except Exception as e:
        logger.error("Contract Loaded: False. Error: %s", e)
        raise

    sender_account = _get_sender_account(sender_address)
    tx_func = contract.functions.registerDonation(
        str(donor_id),
        donor_name,
        organ_type,
        hospital_name,
        doctor_name,
    )
    logger.info("Transaction Submitted")
    tx_hash = tx_func.transact({'from': sender_account})
    logger.info("Transaction Hash: %s", tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    logger.info("Block Number: %s", receipt.blockNumber)
    logger.info("Receipt Status: %s", receipt.status)

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


def match_organ_on_chain(organ_id, recipient_hospital_name, recipient_blockchain_id=None, matching_admin_address=None):
    logger.info("=== ENTERED match_organ_on_chain ===")

    logger.info("blockchain_service.match_organ_on_chain called.")
    connected = w3.is_connected()
    logger.info("Connected to Ganache: %s", connected)
    if not connected:
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    try:
        contract = get_contract()
        logger.info("Contract Loaded: True")
    except Exception as e:
        logger.error("Contract Loaded: False. Error: %s", e)
        raise

    sender_account = _get_sender_account(matching_admin_address)
    logger.info("Sender Account: %s", sender_account)

    if recipient_blockchain_id:
        try:
            blockchain_id_str = str(recipient_blockchain_id).strip()
            if '-' in blockchain_id_str:
                rec_id_int = int(blockchain_id_str.split('-')[-1]) - 1000
            else:
                rec_id_int = int(blockchain_id_str)
            if rec_id_int < 0:
                rec_id_int = 0
        except Exception:
            rec_id_int = 0

        import re
        cleaned_organ_id = re.sub(r'\D', '', str(organ_id))
        organ_id_int = int(cleaned_organ_id) if cleaned_organ_id else 0
        tx_func = contract.functions.matchOrganWithRecipient(
            organ_id_int,
            recipient_hospital_name,
            rec_id_int,
        )
    else:
        import re
        cleaned_organ_id = re.sub(r'\D', '', str(organ_id))
        organ_id_int = int(cleaned_organ_id) if cleaned_organ_id else 0
        tx_func = contract.functions.matchOrgan(
            organ_id_int,
            recipient_hospital_name,
        )

    logger.info("=== BEFORE TRANSACT ===")
    tx_hash = tx_func.transact({'from': sender_account})
    logger.info("=== AFTER TRANSACT ===")

    logger.info("Transaction Hash: %s", tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    logger.info("=== RECEIPT RECEIVED ===")

    logger.info("Block Number: %s", receipt.blockNumber)
    logger.info("Receipt Status: %s", receipt.status)

    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while matching organ.")

    return {
        'transaction_hash': tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
        'block_number': receipt.blockNumber,
        'status': receipt.status,
    }

def transplant_organ_on_chain(organ_id, recipient_blockchain_id=None, hospital_address=None):
    logger.info("blockchain_service.transplant_organ_on_chain called.")
    connected = w3.is_connected()
    logger.info("Connected to Ganache: %s", connected)
    if not connected:
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    try:
        contract = get_contract()
        logger.info("Contract Loaded: True")
    except Exception as e:
        logger.error("Contract Loaded: False. Error: %s", e)
        raise

    sender_account = _get_sender_account(hospital_address)
    
    if recipient_blockchain_id:
        try:
            blockchain_id_str = str(recipient_blockchain_id).strip()
            if '-' in blockchain_id_str:
                rec_id_int = int(blockchain_id_str.split('-')[-1]) - 1000
            else:
                rec_id_int = int(blockchain_id_str)
            if rec_id_int < 0:
                rec_id_int = 0
        except Exception:
            rec_id_int = 0
        import re
        cleaned_organ_id = re.sub(r'\D', '', str(organ_id))
        organ_id_int = int(cleaned_organ_id) if cleaned_organ_id else 0
        tx_func = contract.functions.completeTransplantWithRecipient(
            organ_id_int,
            rec_id_int
        )
    else:
        import re
        cleaned_organ_id = re.sub(r'\D', '', str(organ_id))
        organ_id_int = int(cleaned_organ_id) if cleaned_organ_id else 0
        tx_func = contract.functions.completeTransplant(organ_id_int)
    
    logger.info("Transaction Submitted")
    tx_hash = tx_func.transact({'from': sender_account})
    logger.info("Transaction Hash: %s", tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    logger.info("Block Number: %s", receipt.blockNumber)
    logger.info("Receipt Status: %s", receipt.status)

    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while completing transplant.")

    return {
        'transaction_hash': tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash,
        'block_number': receipt.blockNumber,
        'status': receipt.status
    }


def register_recipient_on_chain(
    recipient_id,
    full_name,
    blood_group,
    organ_needed,
    hospital_name,
    sender_address=None,
):
    logger.info("blockchain_service.register_recipient_on_chain called.")
    connected = w3.is_connected()
    logger.info("Connected to Ganache: %s", connected)
    if not connected:
        raise ConnectionError(f"Blockchain not connected at {settings.GANACHE_RPC_URL}.")

    try:
        contract = get_contract()
        logger.info("Contract Loaded: True")
    except Exception as e:
        logger.error("Contract Loaded: False. Error: %s", e)
        raise

    sender_account = _get_sender_account(sender_address)
    tx_func = contract.functions.registerRecipient(
        str(recipient_id),
        full_name,
        blood_group,
        organ_needed,
        hospital_name,
    )
    logger.info("Transaction Submitted")
    tx_hash = tx_func.transact({'from': sender_account})
    logger.info("Transaction Hash: %s", tx_hash.hex() if isinstance(tx_hash, bytes) else tx_hash)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    logger.info("Block Number: %s", receipt.blockNumber)
    logger.info("Receipt Status: %s", receipt.status)

    if receipt.status != 1:
        raise RuntimeError("Ganache transaction failed while registering recipient.")

    events = contract.events.RecipientRegistered().process_receipt(receipt)
    if not events:
        raise RuntimeError("RecipientRegistered event was not emitted by the contract.")

    event_args = events[0]['args']
    transaction_hash = receipt.transactionHash.hex()
    if not transaction_hash.startswith('0x'):
        transaction_hash = f"0x{transaction_hash}"

    return {
        'blockchain_id': f"BC-{1000 + event_args['id']}",
        'transaction_hash': transaction_hash,
        'block_number': receipt.blockNumber,
        'timestamp': datetime.fromtimestamp(event_args['timestamp'], tz=timezone.utc),
    }



