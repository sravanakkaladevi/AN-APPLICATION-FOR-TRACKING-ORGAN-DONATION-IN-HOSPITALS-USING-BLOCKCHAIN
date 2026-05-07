# Organ Donation Tracker

A Django and blockchain-based application for tracking organ donation workflows in hospitals.

## Project Structure

This project has been cleanly separated into backend and frontend directories:

- `backend/` - The Django project and all backend logic.
  - `core/` - Django app with models, forms, views, admin setup, and blockchain service.
  - `organ_donation_project/` - Django project settings and URL routing.
  - `contracts/` - Solidity contract and blockchain helper files.
  - `media/` - Uploaded profile images.
  - `scripts/` - Database seeding and utility scripts.
- `frontend/` - Frontend assets served by Django.
  - `templates/` - HTML templates.
  - `static/` - CSS, JS, and static image files.

## Features

- Donor, hospital, and admin portals
- Organ registration and matching
- Smart contract integration for immutable records
- Profile picture upload support
- Admin dashboard with analytics and hospital management

## Run Locally

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
