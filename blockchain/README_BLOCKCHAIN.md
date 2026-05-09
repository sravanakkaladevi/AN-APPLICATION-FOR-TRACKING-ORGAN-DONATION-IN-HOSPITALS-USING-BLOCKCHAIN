# ⛓️ Blockchain Integration Module

This module provides a secure and immutable ledger for the **Organ Donation Tracking System** using Ethereum (Ganache).

## 📂 Folder Structure
```text
blockchain/
├── contracts/          # Solidity smart contracts (OrganDonation.sol)
├── scripts/            # Deployment and management scripts
├── tests/              # Automated test cases
└── compiled/           # Compiled ABI and contract address
```

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.13**
- **Ganache**: [Download Ganache](https://trufflesuite.com/ganache/)
- **Dependencies**:
  ```bash
  pip install web3 py-solc-x
  ```

### 2. Start Local Blockchain
1. Open **Ganache**.
2. Click **Quickstart**.
3. Ensure the RPC Server is: `http://127.0.0.1:7545`.

### 3. Deploy Smart Contract
Run the deployment script to compile and push the contract to Ganache:
```bash
cd blockchain/scripts
python deploy_contract.py
```
*This will create `abi.json` and `contract_address.txt` in the `compiled/` folder.*

### 4. Run Automated Tests
Verify that everything is working correctly:
```bash
cd blockchain/tests
python test_blockchain.py
```

---

## 🔄 Transaction Flow
The system follows a clean flow from the User Interface to the Blockchain:

1. **Django Form**: User enters donor details on the website.
2. **Web3.py**: The Django view calls `blockchain_service.py` using the Web3 library.
3. **Ganache**: Web3 sends a signed transaction to the local blockchain provider.
4. **Smart Contract**: The `registerDonor` function in `OrganDonation.sol` executes.
5. **Transaction Hash**: A unique hash is returned and stored in the **MySQL/SQLite Database**.
6. **Immutable Record**: The data is now permanently saved on the blockchain ledger.

---

## 📡 API Endpoints
The following endpoints are available for blockchain interaction:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/blockchain/register-donor/` | `POST` | Registers a new donor (name, organ, hospital). |
| `/api/blockchain/get-donor/?id=1` | `GET` | Retrieves donor details by ID. |
| `/api/blockchain/verify/?hash=0x...` | `GET` | Verifies a transaction hash status. |

---

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
| :--- | :--- | :--- |
| **ConnectionError** | Ganache is not running. | Open Ganache and ensure it is on port 7545. |
| **FileNotFoundError** | Contract not deployed. | Run `python blockchain/scripts/deploy_contract.py` first. |
| **Invalid Transaction** | Gas limit or account error. | Ensure the first account in Ganache has enough ETH. |
| **Solc Not Found** | Solidity compiler missing. | The deploy script installs it automatically, but ensure internet is connected. |

---
*Developed as part of the MCA Final Project Demo.*
