import os
import sys
import json
import subprocess
from web3 import Web3

# 1. Connect to Ganache to get the dynamic chain ID
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if w3.is_connected():
    print("Connected to Ethereum network (Ganache) via Web3.py")
    chain_id = str(w3.eth.chain_id)
else:
    print("Cannot connect to Ethereum network. Please ensure Ganache is running on port 7545.")
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
blockchain_dir = os.path.join(script_dir, "..")
truffle_build_path = os.path.join(blockchain_dir, "build", "contracts", "OrganDonation.json")

# 2. Clear old network addresses from Truffle build artifact before migration to prevent stale keys
if os.path.exists(truffle_build_path):
    try:
        with open(truffle_build_path, "r", encoding="utf-8") as f:
            truffle_json = json.load(f)
        
        truffle_json["networks"] = {}
        with open(truffle_build_path, "w", encoding="utf-8") as f:
            json.dump(truffle_json, f, indent=2)
        print("Cleared old network addresses from Truffle build artifact.")
    except Exception as e:
        print(f"Warning: Could not clear old networks: {e}")

# 3. Run Truffle compilation and migration
print("Compiling and deploying smart contract via Truffle...")
try:
    # Use npx truffle migrate --reset. We use shell=True on Windows for command lookup.
    subprocess.check_call(["npx", "truffle", "migrate", "--reset"], cwd=blockchain_dir, shell=True)
    print("Truffle migration completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error running Truffle migration: {e}")
    sys.exit(1)

# 4. Load the deployed address from Truffle's build artifact
if not os.path.exists(truffle_build_path):
    print(f"Error: Truffle build artifact not found at {truffle_build_path}")
    sys.exit(1)

with open(truffle_build_path, "r", encoding="utf-8") as f:
    truffle_json = json.load(f)

# Find the newly created network entry (there should be exactly one)
networks = truffle_json.get("networks", {})
deployed_address = None
tx_hash = None

for net_id in networks:
    if "address" in networks[net_id]:
        deployed_address = networks[net_id]["address"]
        tx_hash = networks[net_id].get("transactionHash")
        break

if not deployed_address:
    print("Error: Could not find deployed contract address in Truffle networks.")
    sys.exit(1)

print(f"Discovered Truffle deployed address: {deployed_address}")

# 5. Standardize and synchronize network keys (5777, 1337, and current chain_id)
network_info = {
    "events": {},
    "links": {},
    "address": deployed_address,
    "transactionHash": tx_hash
}
truffle_json["networks"]["5777"] = network_info
truffle_json["networks"]["1337"] = network_info
truffle_json["networks"][chain_id] = network_info

with open(truffle_build_path, "w", encoding="utf-8") as f:
    json.dump(truffle_json, f, indent=2)
print(f"Truffle build artifact synchronized at {truffle_build_path}")

# 6. Save to compiled/ directory for legacy Django/Web3.py config path compatibility
compiled_dir = os.path.join(blockchain_dir, "compiled")
os.makedirs(compiled_dir, exist_ok=True)

with open(os.path.join(compiled_dir, "contract_address.txt"), "w") as f:
    f.write(deployed_address)

with open(os.path.join(compiled_dir, "abi.json"), "w") as f:
    json.dump(truffle_json["abi"], f)

print(f"Contract address and ABI saved to legacy location: {compiled_dir}")
