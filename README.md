# Organ Donation Tracker

A Django and blockchain-based application for tracking organ donation workflows in hospitals.

## Project Structure

```text
organ_donation/
├── architecture/         # Project architecture diagrams and documentation
├── backend/              # Django backend and Blockchain logic
│   ├── contracts/        # Solidity smart contracts and interaction scripts
│   ├── core/             # Main Django app (Logic, Models, Views)
│   │   ├── blockchain/   # Blockchain interaction service
│   │   ├── migrations/   # Database migrations
│   │   └── ...           # Forms, Views, Models, Tests
│   ├── media/            # User-uploaded files (Profile pictures)
│   ├── organ_donation_project/ # Project settings and root URLs
│   ├── scripts/          # Utility and data seeding scripts
│   ├── manage.py         # Django management script
│   └── requirements.txt  # Python dependencies
├── database/             # Database schemas, records, and SQL exports
├── frontend/             # Frontend assets and HTML templates
│   ├── static/           # Static files (CSS, JS, Images, Vendors)
│   └── templates/        # Django HTML templates
└── manage.py             # Root Django management script
```

## Directory Deep Dive

### 🏗️ `architecture/`
Contains visual and textual documentation of the system's design.
- `architecture.png` & `data_flow.png`: High-level system and data movement diagrams.
- `uml_diagram.md`: Source code for the UML diagrams.

### ⚙️ `backend/`
The heart of the application, powered by Django.
- **`contracts/`**: Holds the `OrganDonation.sol` Ethereum smart contract. It also includes `compile_contract.py` and `deploy_contract.py` for blockchain deployment.
- **`core/`**: The main application logic.
    - `models.py`: Defines the database schema for Donors, Hospitals, and Organs.
    - `views.py`: Handles the request-response cycle and portal logic.
    - `blockchain/`: Contains `service.py` which interfaces with the Ethereum network using Web3.py.
- **`organ_donation_project/`**: Contains `settings.py` for project configuration and `urls.py` for global routing.
- **`scripts/`**: Includes scripts like `seed_hospitals.py` to pre-populate the database with demo data.

### 🗄️ `database/`
Dedicated folder for database management.
- `schema.sql`: The raw SQL structure of the MySQL database.
- `database_records.json`: A snapshot of the current database data for portability.

### 🎨 `frontend/`
Handles the User Interface and Experience.
- **`static/`**: 
    - `core/css/`: Custom styling for the application.
    - `core/js/`: Client-side logic and interactive elements.
    - `core/vendor/`: Third-party libraries like FontAwesome or Bootstrap.
- **`templates/`**:
    - `core/base.html`: The master layout template.
    - `core/donor_dashboard.html`, `core/hospital_dashboard.html`, etc.: Specific pages for different user roles.

## Features

- **Donor, Hospital, and Admin Portals**: Role-based access control and dashboards.
- **Blockchain Integration**: Immutable record-keeping for organ matches and donation history.
- **Organ Matching System**: Automated and manual matching of donors with patients.
- **Admin Dashboard**: Comprehensive analytics and hospital verification system.
- **Real-time Updates**: Status tracking of organ donation journeys.

## Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Database Setup**:
   Ensure MySQL is running and update `backend/organ_donation_project/settings.py` with your credentials.

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Start the Server**:
   ```bash
   python manage.py runserver
   ```
