# Organ Donation Tracking System using Blockchain

MCA final year academic project:

**An Application for Tracking Organ Donation in Hospitals using Blockchain**

This project is a Django-based organ donation management system with a local Ethereum blockchain layer for audit tracking. Normal application data stays in the database, while important workflow events are recorded on Ganache through a Solidity smart contract and Web3.py.

## Current Stack

| Layer | Technology |
| --- | --- |
| Backend | Django, Python |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Database | Django ORM; current local settings use SQLite for development |
| Blockchain | Ganache, Solidity, Truffle, Web3.py |
| Smart contract | `blockchain/contracts/OrganDonation.sol` |

## What the System Tracks

- Donor registration and hospital approval
- Organ availability and blockchain verification
- Recipient/patient organ requests
- Admin organ matching
- Transplant completion
- Blockchain transaction hashes and audit logs
- Status history for viva/demo explanation

## Important Design Rule

The project uses a hybrid storage model.

- Database stores normal hospital, donor, recipient, and transplant data.
- Blockchain stores only audit-level records such as transaction hashes, donor verification events, organ matching events, transplant events, and immutable timestamps.
- Full medical data is not stored on-chain.

## Main Workflow

1. Donor registers or pledges an organ.
2. Hospital reviews donor and organ suitability.
3. Admin sends approved organ details to blockchain.
4. Admin clicks **Match Organ** and selects a compatible recipient.
5. Django calls `match_organ_on_chain()`.
6. Smart contract executes `matchOrganWithRecipient()`.
7. Ganache mines a new block.
8. Database updates the organ status to `Matched`.
9. Admin or hospital completes the transplant.
10. Django calls `transplant_organ_on_chain()`.
11. Smart contract executes `completeTransplantWithRecipient()`.
12. Ganache mines another block.
13. Database updates status to `Transplanted`.

## Project Structure

```text
organ_donation/
|-- backend/
|   |-- core/
|   |   |-- blockchain/
|   |   |   `-- service.py
|   |   |-- management/commands/
|   |   |-- migrations/
|   |   |-- models.py
|   |   |-- forms.py
|   |   |-- views.py
|   |   |-- urls.py
|   |   `-- tests.py
|   |-- organ_donation_project/
|   |   `-- settings.py
|   |-- scripts/
|   `-- requirements.txt
|
|-- blockchain/
|   |-- contracts/
|   |   `-- OrganDonation.sol
|   |-- migrations/
|   |   `-- 1_deploy_organ_donation.js
|   |-- scripts/
|   |   |-- compile_contract.py
|   |   `-- deploy_contract.py
|   |-- truffle-config.js
|   `-- README_BLOCKCHAIN.md
|
|-- frontend/
|   |-- static/
|   `-- templates/core/
|       |-- admin_dashboard.html
|       |-- hospital_dashboard.html
|       |-- donor_dashboard.html
|       |-- home.html
|       |-- login.html
|       |-- register_donor.html
|       `-- register_hospital.html
|
|-- architecture/
|-- database/
|-- documentation/
|-- scripts/
|-- manage.py
|-- requirements.txt
|-- start_project.bat
|-- .gitignore
`-- README.md
```

## Key Files

| File | Purpose |
| --- | --- |
| `backend/core/models.py` | User roles, donor, hospital, organ, recipient, transplant, blockchain logs |
| `backend/core/views.py` | Dashboard workflows and admin/hospital/donor actions |
| `backend/core/blockchain/service.py` | Web3.py connection, contract loading, register/match/transplant transactions |
| `backend/core/urls.py` | Django route mappings |
| `frontend/templates/core/admin_dashboard.html` | Admin dashboard, organ matching modal, transplant actions |
| `blockchain/contracts/OrganDonation.sol` | Solidity smart contract |
| `blockchain/scripts/deploy_contract.py` | Deploys the contract to Ganache and syncs artifacts |

## Setup

### 1. Create and activate virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start Ganache

Open Ganache Desktop and make sure:

```text
RPC Server: http://127.0.0.1:7545
Network ID: 5777
```

### 4. Run migrations

```powershell
python manage.py migrate
```

### 5. Deploy smart contract

```powershell
python blockchain\scripts\deploy_contract.py
```

The deployment creates or updates:

```text
blockchain/build/contracts/OrganDonation.json
blockchain/compiled/abi.json
blockchain/compiled/contract_address.txt
```

### 6. Run server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Useful Verification Commands

Run Django system checks:

```powershell
python manage.py check
```

Run application tests:

```powershell
python manage.py test core
```

Check Ganache/Web3 flow manually from the UI:

1. Open Admin Dashboard.
2. Send eligible organ to blockchain.
3. Click **Match Organ**.
4. Select a compatible recipient.
5. Confirm that Ganache mines one new block.
6. Confirm the UI changes to `Matched`.
7. Click **Complete Transplant**.
8. Confirm Ganache mines one more block.
9. Confirm the UI changes to `Transplanted`.

## Environment Variables

These settings are read by Django when available:

| Variable | Default |
| --- | --- |
| `DJANGO_SECRET_KEY` | Local development fallback in settings |
| `GANACHE_RPC_URL` | `http://127.0.0.1:7545` |
| `GANACHE_CHAIN_ID` | `5777` |
| `ORGAN_DONATION_CONTRACT_ADDRESS` | Empty; loaded from artifact if not set |
| `ORGAN_DONATION_FROM_ADDRESS` | Empty; falls back to first Ganache account |
| `ORGAN_DONATION_ARTIFACT_PATH` | `blockchain/build/contracts/OrganDonation.json` |

Do not commit real secrets, private keys, or local credential files.

## Current Blockchain Functions

The Django Web3 service uses these main contract operations:

- `registerDonation(...)`
- `registerRecipient(...)`
- `matchOrganWithRecipient(...)`
- `completeTransplantWithRecipient(...)`

The project intentionally does not use coins, NFTs, mining logic, or token systems.

## Viva Explanation

Why blockchain is used:

Blockchain is used only for audit verification. For example, when an organ is matched or transplanted, Ganache creates a transaction hash. That hash is saved in the database and can be checked later to prove that the event was recorded and not silently changed.

Why database is still used:

Hospital and medical data changes often and can be private. Storing all medical details directly on-chain would be slow, expensive, and unnecessary for this academic demo.

Simple example:

If CARE Hospital donates a kidney and the admin matches it to a recipient at another hospital, Django updates the normal database record and Web3.py sends a transaction to Ganache. The resulting transaction hash becomes the verification proof for that match.

## AI Agent Context & Documentation

This project contains comprehensive testing records and AI context configurations:
- `documentation/TEST_CASES.md`: Contains 25 positive test cases covering Unit, Integration, Functional, System, and UAT testing phases.
- `documentation/architecture_graph.html`: A visual architecture flow generated via Mermaid.js.
- `.agents/`: Contains custom context files, rules (`AGENTS.md`), and workflows designed to give AI coding assistants (like Google Antigravity or GitHub Copilot) instant contextual awareness of the project architecture and UI constraints.
- Graphify integration: The workspace uses `graphify` for full semantic codebase mapping. The generated graph output is excluded from git in `.agents/graphify-out/`.

## Notes for Git

Generated blockchain build files, local credentials, scratch scripts, and test result output should stay out of commits unless they are intentionally needed for a report.

Before pushing:

```powershell
git status --short
python manage.py check
python manage.py test core
```
