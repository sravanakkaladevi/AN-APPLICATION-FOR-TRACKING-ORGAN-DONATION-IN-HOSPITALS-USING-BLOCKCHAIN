# Organ Donation Tracker (Blockchain + Django)

A decentralized application (DApp) for tracking organ donation workflows, ensuring transparency and security using Ethereum Blockchain (Ganache) and Django.

## 🏗️ Project Architecture
The system follows a clean architecture:
**User → Hospital Portal → Django Backend → Web3.py → Ethereum Smart Contract → Ganache**

## 📂 Project Structure

```text
organ_donation/
├── backend/              # Django backend and Blockchain logic
│   ├── contracts/        # Solidity smart contracts (OrganDonation.sol)
│   ├── core/             # Main Django app (Logic, Models, Views)
│   │   ├── blockchain/   # Web3.py interaction service (service.py)
│   │   └── ...           # Models, Views, Templates
│   ├── scripts/          # Seeding scripts (seed_mca_hospitals.py)
│   ├── db.sqlite3        # SQLite database (Zero setup required)
│   ├── manage.py         # Django management script
│   └── requirements.txt  # Python dependencies
├── frontend/             # HTML templates and UI assets
└── README.md             # Documentation
```

## 🚀 Features

- **Decentralized Ledger**: Immutable record-keeping for organ matches and donation history.
- **5 Hospital Nodes**: Pre-configured nodes for Apollo, Yashoda, CARE, KIMS, and AIG.
- **Wallet Integration**: Every hospital has a unique Ethereum wallet address from Ganache.
- **Transaction Tracking**: Real-time status, wallet address display, and transaction hash logging.
- **Role-Based Access**: Specialized portals for Donors, Hospitals, and Admins.

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **Ganache**: Download and install [Truffle Ganache](https://trufflesuite.com/ganache/).
- **Node.js** (for Truffle if compiling contracts manually).

### 2. Start Blockchain (Ganache)
1. Open Ganache and click **Quickstart**.
2. Ensure the RPC Server is running at `http://127.0.0.1:7545`.
3. Network ID should be `5777`.

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Database Initialization
```bash
cd backend
python manage.py makemigrations core
python manage.py migrate
```

### 5. Seed Hospital Data (Mapped to Ganache Wallets)
This script creates exactly 5 hospital admins and maps them to the first 5 accounts in your Ganache instance.
```bash
python scripts/seed_mca_hospitals.py
```
*Note: Default password for all hospital admins is `Hospital123`.*

### 6. Run the Application
```bash
python manage.py runserver
```

## 🏥 Hospital Admin Accounts
| Hospital | Username | Wallet (Ganache) |
| :--- | :--- | :--- |
| **Apollo Hospital** | `apollo_admin` | Account #1 |
| **Yashoda Hospital** | `yashoda_admin` | Account #2 |
| **CARE Hospital** | `care_admin` | Account #3 |
| **KIMS Hospital** | `kims_admin` | Account #4 |
| **AIG Hospital** | `aig_admin` | Account #5 |

## ⚙️ Configuration
- **Database**: Uses SQLite (`db.sqlite3`) for simple, zero-config local development.
- **Blockchain**: Configured in `backend/organ_donation_project/settings.py`.
- **Contract Address**: Automatically read from the latest Truffle artifacts.

## 🎓 Academic Info
This project is developed as part of an MCA (Master of Computer Applications) curriculum to demonstrate the integration of Blockchain technology in Healthcare Management.
