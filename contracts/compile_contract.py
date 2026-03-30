from solcx import compile_standard, install_solc
import json
import os

# Install solc version
print("Installing solc...")
install_solc("0.8.19")

with open("OrganDonation.sol", "r") as file:
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
    solc_version="0.8.19",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["OrganDonation.sol"]["OrganDonation"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["OrganDonation.sol"]["OrganDonation"]["abi"]

with open("abi.json", "w") as file:
    json.dump(abi, file)

with open("bytecode.txt", "w") as file:
    file.write(bytecode)

print("Compilation successful, abi and bytecode saved.")
