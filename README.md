# 🫀 OrganChain — Blockchain-Based Organ Donation Tracking System

> **MCA Final Year Project** | Django + Ethereum (Ganache) + Web3.py  
> A production-style decentralized application (DApp) for transparent, immutable organ donation lifecycle tracking across hospitals.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Role Modules](#role-modules)
- [Setup Instructions](#setup-instructions)
- [Login Credentials](#login-credentials)
- [Blockchain Integration](#blockchain-integration)
- [Configuration](#configuration)
- [Knowledge Graph & MCP](#knowledge-graph--mcp)
- [Academic Info](#academic-info)

---

## Overview

OrganChain is a full-stack web application that tracks the complete lifecycle of organ donation — from donor registration and organ availability, through hospital matching and transplantation, to final blockchain verification. Every organ registration and transplant event is logged as an immutable transaction on a local Ethereum blockchain (Ganache), ensuring auditability and transparency.

**Tech Stack:**
| Layer | Technology |
|---|---|
| Backend | Django 4.x (Python) |
| Blockchain | Solidity Smart Contract + Web3.py |
| Local Chain | Ganache (Truffle Suite) |
| Database | SQLite (development) |
| Frontend | Bootstrap 5 + Vanilla JS + Custom CSS |
| Auth | Django role-based auth (Admin / Hospital / Donor) |

---

## Features

- **🔗 Immutable Ledger** — Every organ registration and transplant is stored on-chain via a Solidity smart contract
- **🏥 Multi-Hospital Network** — Hospitals register, match, and transfer organs across the network
- **👤 Donor Portal** — Donors pledge organs, track status, and view blockchain verification records
- **🛠️ Admin Control Center** — Full oversight: users, hospitals, recipients, feedback analytics, audit trail
- **🤝 Donor-Recipient Matching** — Hospital-driven organ matching with blockchain confirmation
- **📊 Feedback & Sentiment Analysis** — Rule-based NLP sentiment scoring on user feedback
- **📜 Death Certificate Management** — Admin-issued medical certificates tied to donor records
- **🔐 Role-Based Access** — Clean separation between Admin, Hospital, and Donor portals

---

## Project Structure

```text
organ_donation/
│
├── 📁 backend/                    # Django application root
│   ├── core/                      # Main Django app
│   │   ├── blockchain/            # Web3.py service (register, match, transplant)
│   │   │   └── service.py
│   │   ├── migrations/            # Django DB migrations
│   │   ├── models.py              # User, DonorProfile, HospitalProfile, Recipient, Transplant...
│   │   ├── views.py               # All view logic (Admin / Hospital / Donor dashboards)
│   │   ├── forms.py               # All Django forms (Registration, Recipient, Pledge...)
│   │   ├── urls.py                # URL routing
│   │   └── api_views.py           # Blockchain REST API endpoints
│   ├── organ_donation_project/    # Django project settings
│   │   └── settings.py
│   ├── scripts/                   # DB seeding scripts
│   │   └── seed_mca_hospitals.py
│   ├── db.sqlite3                 # SQLite database (auto-generated)
│   └── requirements.txt           # Python dependencies
│
├── 📁 blockchain/                 # Ethereum blockchain module
│   ├── contracts/                 # Solidity smart contracts
│   │   └── OrganDonation.sol
│   ├── scripts/                   # Compile & deploy scripts
│   │   ├── compile_contract.py
│   │   └── deploy_contract.py
│   └── tests/                     # Automated blockchain test suite
│       ├── test_blockchain.py
│       ├── TEST_CASES.csv
│       └── test_results.txt
│
├── 📁 frontend/                   # UI layer
│   ├── templates/core/            # Django HTML templates
│   │   ├── base.html              # Global layout, navbar, theme
│   │   ├── login.html             # Cinematic login page
│   │   ├── home.html              # Public landing page
│   │   ├── admin_dashboard.html   # Admin module (full SPA)
│   │   ├── hospital_dashboard.html # Hospital module
│   │   ├── donor_dashboard.html   # Donor/User module
│   │   ├── register_donor.html    # Donor registration
│   │   ├── register_hospital.html # Hospital registration
│   │   └── register_organ.html    # Organ registration form
│   └── static/core/               # CSS, JS, images
│       └── images/
│
├── 📁 architecture/               # System design diagrams
│   ├── architecture.png
│   ├── data_flow.png
│   ├── uml_diagram.png
│   └── architecture_graph.md
│
├── 📁 database/                   # DB exports / schema references
│
├── 📁 documentation/              # Project documentation
│
├── 📁 scripts/                    # Utility & maintenance scripts
│   ├── setup_all.py               # Automated setup (migrations + seed + deploy)
│   ├── update_donor_dash.py       # Donor dashboard template patcher
│   ├── update_hosp_dash.py        # Hospital dashboard template patcher
│   ├── update_hosp_dash2.py       # Hospital dashboard v2 patcher
│   └── update_nav.py              # Navigation template patcher
│
├── manage.py                      # Django CLI entry point
├── start_project.bat              # Windows quick-start (Ganache + Django)
├── .gitignore
└── README.md                      # This file
```

---

## System Architecture

```
Donor/Hospital/Admin Browser
          │
          ▼
   Django Web Server (manage.py runserver)
          │
    ┌─────┴──────┐
    │  Views.py  │  ←── Role-based routing (Admin / Hospital / Donor)
    └─────┬──────┘
          │
    ┌─────┴──────────────┐
    │  blockchain/       │  ←── Web3.py service.py
    │  service.py        │
    └─────┬──────────────┘
          │
    Ganache (Local Ethereum Node)
    http://127.0.0.1:7545
          │
    OrganDonation.sol (Smart Contract)
          │
    Immutable Transaction Ledger
```

---

## Role Modules

### 🔴 Admin Portal
| Section | Description |
|---|---|
| Dashboard | Live stats: donors, recipients, hospitals, organs, blockchain tx |
| User Management | Approve, edit, deactivate users |
| Hospital Management | Add, edit, delete hospital accounts |
| Donor Management | View all registered donors |
| Recipient & Patient Monitor | Track all recipients across hospitals |
| Transplant Tracking | Monitor all donor→recipient transplant events |
| Blockchain Logs | Immutable transaction ledger (tx hash, organ, donor, hospital) |
| Feedback & Sentiment | Feedback with NLP sentiment analysis (positive/neutral/negative) |
| Death Certificate | Issue medical death certificates tied to donor records |
| Audit Trail | System activity log |

### 🟢 Hospital Portal
| Section | Description |
|---|---|
| Dashboard | Hospital-specific stats (6 KPI cards) |
| Donor Management | View all system donors, register organs |
| Registered Donors | Organs registered by this hospital |
| Available Donors / Organs | Match available organs from other hospitals |
| Recipient / Patient Management | Add and track patients awaiting transplants |
| Transplant Tracking | Update status of received organs (Matched → Transplanted) |
| Blockchain Records | Hospital's on-chain transaction history |
| Search | Search organs by type and location |
| Settings | Update hospital profile, logo, wallet address |

### 🔵 Donor Portal
| Section | Description |
|---|---|
| Dashboard | Overview of donor's registered organs |
| Donate Organ / Pledge | Pledge specific organs before hospital verification |
| My Organ Donation Status | Track status of all pledged/registered organs |
| Blockchain Verification | Personal on-chain transaction history |
| Feedback | Submit feedback with star rating |
| My Profile | Edit personal info and profile picture |

---

## Setup Instructions

### Prerequisites
- **Python 3.10+**
- **Ganache Desktop** — [Download here](https://trufflesuite.com/ganache/)
- **Git**

---

### Step 1 — Clone & Create Virtual Environment
```bash
git clone <repo-url>
cd organ_donation
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2 — Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3 — Start Ganache
1. Open **Ganache Desktop** → Click **Quickstart Ethereum**
2. Confirm RPC Server: `http://127.0.0.1:7545`
3. Network ID: `5777`

### Step 4 — Automated Setup (Recommended)
```bash
python scripts/setup_all.py
```
This runs migrations, seeds hospital data, compiles and deploys the smart contract automatically.

### Step 5 — OR Manual Setup
```bash
# Migrations
python manage.py migrate

# Seed hospital data
python backend/scripts/seed_mca_hospitals.py

# Compile contract
python blockchain/scripts/compile_contract.py

# Deploy contract
python blockchain/scripts/deploy_contract.py
```

### Step 6 — Run the Server
```bash
python manage.py runserver
```
Open → [http://127.0.0.1:8000](http://127.0.0.1:8000)

### ⚡ Quick Start (Windows Only)
```bat
start_project.bat
```

---

## Login Credentials

> [!NOTE]
> Default credentials are set during seeding. For security, sensitive credentials are not committed to the repository.

**Create a superuser (Admin):**
```bash
python manage.py createsuperuser
```

**Hospital & Donor accounts** are created through:
- Registration pages: `/register/donor/` and `/register/hospital/`
- Or via the Admin portal after logging in as superuser

---

## Blockchain Integration

The system uses a **Solidity smart contract** (`OrganDonation.sol`) deployed on **Ganache** (local Ethereum testnet).

### On-Chain Events
| Event | Trigger |
|---|---|
| `registerOrgan()` | Hospital registers a donor's organ |
| `matchOrgan()` | Hospital matches an organ to a recipient hospital |
| `transplantOrgan()` | Hospital marks transplant as complete |

### Transaction Record
Every blockchain event stores a `BlockchainTransaction` record in MySQL with:
- `tx_hash` — Ethereum transaction hash
- `organ_type` — Organ involved
- `donor` → linked to DonorProfile
- `hospital` → linked to HospitalProfile
- `timestamp` — Auto-recorded

### Running Blockchain Tests
```bash
python blockchain/tests/test_blockchain.py
```
Results saved to `blockchain/tests/test_results.txt`.

---

## Configuration

| Setting | Location | Default |
|---|---|---|
| Database | `backend/organ_donation_project/settings.py` | SQLite |
| Ganache RPC | `backend/core/blockchain/service.py` | `http://127.0.0.1:7545` |
| Contract Address | Auto-updated after deployment | — |
| Media Uploads | `MEDIA_ROOT` in settings.py | `frontend/media/` |
| Static Files | `STATIC_ROOT` in settings.py | `frontend/static/` |

---

## Knowledge Graph & MCP

The codebase features an integrated AST-based **Knowledge Graph** via `graphify` and `code-review-graph`. This allows any MCP-compliant AI Coding Assistant (like Claude Code, Cursor, Windsurf) to navigate the workspace with **500x lower token consumption** and 100% structural accuracy.

### Exploring the Visual Graph
An interactive D3 visual map of the codebase is compiled and available offline:
*   [graph.html](file:///c:/Users/srava/.gemini/antigravity/scratch/organ_donation/documentation/graphfy/graph.html) — Open directly in your web browser to explore classes, files, smart contracts, and their dependencies interactively.
*   [GRAPH_REPORT.md](file:///c:/Users/srava/.gemini/antigravity/scratch/organ_donation/documentation/graphfy/GRAPH_REPORT.md) — Comprehensive structural and community dependency analysis report.

### Setting Up the MCP Servers
Local machine-specific config mappings are ignored via Git but configured at your project root in `.mcp.json`.

---

## Academic Info

| Field | Detail |
|---|---|
| Project Title | Organ Donation Tracking using Blockchain |
| Author | **Akkaladevi Sravan Kumar** |
| Course | MCA (Master of Computer Applications) |
| Technologies | Django, Solidity, Web3.py, Ganache, Bootstrap 5 |
| Key Concepts | Blockchain immutability, Smart contracts, Role-based access, Sentiment analysis |
| Evaluation | Suitable for MCA viva and project demo |

---

*Built with ❤️ by **Akkaladevi.Sravan kumar** for transparent, trustworthy healthcare.*
