import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organ_donation_project.settings')
django.setup()

from core.models import User, HospitalProfile

# Password requested by user
PASSWORD = "Admin123"

# List of 28 Hospitals representing states/locations in India:
# Prioritizing the exact ones requested by the user, then filling the rest to hit 28 total.
hospitals_data = [
    {"name": "Ace Hospital", "state": "Maharashtra"},
    {"name": "AIIMS Delhi", "state": "Delhi"},
    {"name": "Fortis Hospital", "state": "Punjab"},
    {"name": "GB Pant Hospital", "state": "Delhi"},
    {"name": "Birla Hospital", "state": "Madhya Pradesh"},
    {"name": "Apollo Hospital", "state": "Gujarat"},
    {"name": "Sahara Hospital", "state": "Uttar Pradesh"},
    {"name": "Columbia Asia Hospital", "state": "Karnataka"},
    {"name": "Apollo Hospitals Vizag", "state": "Andhra Pradesh"},
    {"name": "Medanta The Medicity", "state": "Haryana"},
    {"name": "Manipal Hospital Bengaluru", "state": "Karnataka"},
    {"name": "Amrita Hospital Kochi", "state": "Kerala"},
    {"name": "Apollo Hospitals Chennai", "state": "Tamil Nadu"},
    {"name": "Yashoda Hospitals Hyderabad", "state": "Telangana"},
    {"name": "Sanjay Gandhi PGI Lucknow", "state": "Uttar Pradesh"},
    {"name": "Apollo Multispeciality Kolkata", "state": "West Bengal"},
    # Below are filled to complete 28 representing other major states
    {"name": "AIIMS Patna", "state": "Bihar"},
    {"name": "AIIMS Raipur", "state": "Chhattisgarh"},
    {"name": "Goa Medical College", "state": "Goa"},
    {"name": "IGMC Shimla", "state": "Himachal Pradesh"},
    {"name": "RIMS Ranchi", "state": "Jharkhand"},
    {"name": "RIMS Imphal", "state": "Manipur"},
    {"name": "NEIGRIHMS Shillong", "state": "Meghalaya"},
    {"name": "AIIMS Bhubaneswar", "state": "Odisha"},
    {"name": "SMS Hospital Jaipur", "state": "Rajasthan"},
    {"name": "STNM Hospital Gangtok", "state": "Sikkim"},
    {"name": "AGMC Agartala", "state": "Tripura"},
    {"name": "AIIMS Rishikesh", "state": "Uttarakhand"}
]

created_count = 0

for idx, data in enumerate(hospitals_data):
    # Generate unique baseline strings
    base_name = data["name"].replace(" ", "").lower()
    username = f"{base_name}_{idx+1}"
    email = f"contact@{base_name}.in"
    reg_number = f"IND-{data['state'][:3].upper()}-{1000 + idx}"
    
    # Check if user already exists
    if not User.objects.filter(username=username).exists():
        # Create user
        user = User.objects.create_user(username=username, email=email, password=PASSWORD)
        user.is_hospital = True
        user.save()
        
        # Create hospital profile
        HospitalProfile.objects.create(
            user=user,
            hospital_name=data["name"],
            registration_number=reg_number,
            address=f"Main Junction, {data['state']}, India"
        )
        created_count += 1
        print(f"Created: {data['name']} (Username: {username})")
    else:
        print(f"Already exists: {data['name']}")

print(f"\nSuccessfully registered {created_count} hospitals.")
