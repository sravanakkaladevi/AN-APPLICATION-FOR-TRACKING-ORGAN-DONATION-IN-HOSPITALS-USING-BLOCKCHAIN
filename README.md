# Organ Donation Tracker (Blockchain + Django)

A decentralized application (DApp) for tracking organ donation workflows, ensuring transparency and security using Ethereum Blockchain (Ganache) and Django.

## 🏗️ Project Architecture
The system follows a clean architecture:
**User → Hospital Portal → Django Backend → Web3.py → Ethereum Smart Contract → Ganache**

## 📂 Project Structure

```text
organ_donation/
├── backend/              # Django backend
│   ├── core/             # Main Django app (Logic, Models, Views)
│   │   ├── blockchain/   # Web3.py interaction service (service.py)
│   │   └── ...           # Models, Views, Templates
│   ├── scripts/          # Seeding scripts (seed_mca_hospitals.py)
│   ├── db.sqlite3        # SQLite database
│   ├── manage.py         # Django management script
│   └── requirements.txt  # Python dependencies
├── blockchain/           # Blockchain module (Modular refactor)
│   ├── contracts/        # Solidity smart contracts (OrganDonation.sol)
│   ├── scripts/          # Compilation and deployment scripts
│   └── tests/            # Automated test suite (test_blockchain.py)
├── frontend/             # HTML templates and UI assets
├── setup_all.py          # Automated setup script (Recommended)
├── start_project.bat     # Quick start batch file
└── README.md             # Documentation
```

## 🚀 Features

- **Decentralized Ledger**: Immutable record-keeping for organ matches and donation history.
- **5 Hospital Nodes**: Pre-configured nodes for Apollo, Yashoda, CARE, KIMS, and AIG.
- **Wallet Integration**: Every hospital has a unique Ethereum wallet address from Ganache.
- **Transaction Tracking**: Real-time status, wallet address display, and transaction hash logging.
- **Role-Based Access**: Specialized portals for Donors, Hospitals, and Admins.
- **Automated Testing**: Integrated test suite for blockchain validation.

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **Ganache**: Download and install [Truffle Ganache](https://trufflesuite.com/ganache/).

### 2. Start Blockchain (Ganache)
1. Open Ganache and click **Quickstart**.
2. Ensure the RPC Server is running at `http://127.0.0.1:7545`.
3. Network ID should be `5777`.

### 3. Automated Setup (Recommended)
The project now includes an automated setup script that installs dependencies, runs migrations, seeds data, compiles, and deploys the contract in one go.
```bash
python setup_all.py
```

### 4. Manual Setup (Alternative)
If you prefer manual steps:
1. **Install Dependencies**: `pip install -r backend/requirements.txt`
2. **Database Migrations**: `python backend/manage.py migrate`
3. **Seed Data**: `python backend/scripts/seed_mca_hospitals.py`
4. **Compile/Deploy**: Run the scripts in `blockchain/scripts/`

### 5. Run the Application
```bash
python backend/manage.py runserver
```

## 🔐 Login Credentials

> [!NOTE]
> For security reasons, login credentials are not included in the public repository.
> 
> **How to access:**
> 1. Check the local `CREDENTIALS.md` file (if available).
> 2. If you are a student or evaluator, please contact the project maintainer for the hospital and admin credentials.
> 3. Alternatively, you can create your own superuser using:

```bash
python backend/manage.py createsuperuser
```

## ⚙️ Configuration
- **Database**: Uses SQLite (`db.sqlite3`) for simple, zero-config local development.
- **Blockchain**: Configured in `backend/organ_donation_project/settings.py`.
- **Contract Address**: Automatically updated in `backend/core/blockchain/` after deployment.

## 🎓 Academic Info
This project is developed as part of an MCA (Master of Computer Applications) curriculum to demonstrate the integration of Blockchain technology in Healthcare Management.
