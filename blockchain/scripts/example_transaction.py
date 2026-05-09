import sys
import os

# Add root directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from backend import blockchain_service
except ImportError:
    # Fallback: add backend directory directly to path
    backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend")
    sys.path.append(backend_path)
    import blockchain_service

def run_demo():
    print("--- Blockchain Transaction Demo ---")
    
    # 1. Register Donor
    print("\nStep 1: Registering Donor 'Sravan' for 'Kidney' donation...")
    reg_result = blockchain_service.register_donor("Sravan", "Kidney", "Apollo-Hyderabad")
    
    if "error" in reg_result:
        print(f"Error: {reg_result['error']}")
        return

    tx_hash = reg_result['transaction_hash']
    print(f"Success! Transaction Hash: {tx_hash}")
    
    # 2. Verify Transaction
    print("\nStep 2: Verifying transaction on blockchain...")
    verify_result = blockchain_service.verify_transaction(tx_hash)
    print(f"Status: {verify_result['status']} in Block: {verify_result['block_number']}")
    
    # 3. Retrieve Data
    print("\nStep 3: Retrieving donor data from smart contract...")
    # Get the latest ID (we'll assume it's the one we just added)
    w3 = blockchain_service.connect_blockchain()
    contract = blockchain_service.get_contract_instance(w3)
    latest_id = contract.functions.donorCount().call()
    
    donor_data = blockchain_service.get_donor(latest_id)
    print(f"Data Found: ID={donor_data['id']}, Name={donor_data['name']}, Organ={donor_data['organ_type']}")
    
    print("\n--- Demo Completed Successfully! ---")

if __name__ == "__main__":
    run_demo()
