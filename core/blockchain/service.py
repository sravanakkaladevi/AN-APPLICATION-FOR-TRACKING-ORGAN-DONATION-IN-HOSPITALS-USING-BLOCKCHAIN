import json
import os
from web3 import Web3
from django.conf import settings

# This directory structure expects abi.json and contract_address.txt to be deposited here by deploy_contract.py
current_dir = os.path.dirname(os.path.abspath(__file__))

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

def get_contract():
    try:
        with open(os.path.join(current_dir, 'abi.json'), 'r') as f:
            abi = json.load(f)
        with open(os.path.join(current_dir, 'contract_address.txt'), 'r') as f:
            address = f.read().strip()
        
        return w3.eth.contract(address=address, abi=abi)
    except Exception as e:
        print(f"Error loading contract: {e}. Was it deployed?")
        return None

def register_organ_on_chain(donor_hash, organ_type, blood_group, hospital_address=None):
    contract = get_contract()
    if not contract or not w3.is_connected():
        raise Exception("Blockchain not connected or contract not found.")
    
    sender_account = hospital_address if hospital_address else w3.eth.accounts[0]

    # Build transaction
    tx_hash = contract.functions.addOrgan(
        donor_hash,
        organ_type,
        blood_group
    ).transact({'from': sender_account})
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # We can parse the events to get the generated organ ID
    events = contract.events.OrganAdded().process_receipt(receipt)
    if events:
        return events[0]['args']['id']
    return None

def match_organ_on_chain(organ_id, recipient_hospital_address, matching_admin_address=None):
    contract = get_contract()
    sender_account = matching_admin_address if matching_admin_address else w3.eth.accounts[0]
    
    tx_hash = contract.functions.matchOrgan(
        organ_id,
        recipient_hospital_address
    ).transact({'from': sender_account})
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.status == 1

def transplant_organ_on_chain(organ_id, hospital_address=None):
    contract = get_contract()
    sender_account = hospital_address if hospital_address else w3.eth.accounts[0]
    
    tx_hash = contract.functions.completeTransplant(organ_id).transact({'from': sender_account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.status == 1
