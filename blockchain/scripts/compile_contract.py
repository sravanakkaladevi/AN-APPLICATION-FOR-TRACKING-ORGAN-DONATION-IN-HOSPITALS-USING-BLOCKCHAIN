from solcx import compile_standard, install_solc
import json
import os

# Configuration
SOLC_VERSION = "0.8.19"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT_PATH = os.path.join(BASE_DIR, "contracts", "OrganDonation.sol")
COMPILED_DIR = os.path.join(BASE_DIR, "compiled")

os.makedirs(COMPILED_DIR, exist_ok=True)

print(f"Installing solc {SOLC_VERSION}...")
install_solc(SOLC_VERSION)

print(f"Reading contract from {CONTRACT_PATH}...")
with open(CONTRACT_PATH, "r") as file:
    organ_donation_file = file.read()

print("Compiling contract...")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"OrganDonation.sol": {"content": organ_donation_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version=SOLC_VERSION,
)

# get bytecode and abi
contract_data = compiled_sol["contracts"]["OrganDonation.sol"]["OrganDonation"]
bytecode = contract_data["evm"]["bytecode"]["object"]
abi = contract_data["abi"]

# Save artifacts
with open(os.path.join(COMPILED_DIR, "abi.json"), "w") as file:
    json.dump(abi, file)

with open(os.path.join(COMPILED_DIR, "bytecode.txt"), "w") as file:
    file.write(bytecode)

with open(os.path.join(COMPILED_DIR, "compiled_code.json"), "w") as file:
    json.dump(compiled_sol, file)

print(f"Compilation successful. Artifacts saved to {COMPILED_DIR}")
