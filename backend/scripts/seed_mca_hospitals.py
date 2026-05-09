import os
import django
import sys
from web3 import Web3

# Set up Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organ_donation_project.settings')
django.setup()

from core.models import User, HospitalProfile
from django.conf import settings

def seed_hospitals():
    print("Connecting to Ganache...")
    w3 = Web3(Web3.HTTPProvider(settings.GANACHE_RPC_URL))
    
    if not w3.is_connected():
        print(f"Error: Could not connect to Ganache at {settings.GANACHE_RPC_URL}")
        return

    accounts = w3.eth.accounts
    if len(accounts) < 5:
        print("Error: Ganache needs at least 5 accounts.")
        return

    hospitals = [
        {"name": "Apollo Hospital", "email": "admin@apollo.com", "username": "apollo_admin"},
        {"name": "Yashoda Hospital", "email": "admin@yashoda.com", "username": "yashoda_admin"},
        {"name": "CARE Hospital", "email": "admin@care.com", "username": "care_admin"},
        {"name": "KIMS Hospital", "email": "admin@kims.com", "username": "kims_admin"},
        {"name": "AIG Hospital", "email": "admin@aig.com", "username": "aig_admin"},
    ]

    print("Seeding hospitals...")
    for i, hosp_data in enumerate(hospitals):
        username = hosp_data["username"]
        email = hosp_data["email"]
        wallet = accounts[i]
        
        # Create User
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_hospital": True,
                "is_approved": True
            }
        )
        if created:
            user.set_password("Hospital123")
            user.save()
            print(f"Created user: {username}")
        else:
            print(f"User {username} already exists.")

        # Create Hospital Profile
        profile, p_created = HospitalProfile.objects.update_or_create(
            user=user,
            defaults={
                "hospital_name": hosp_data["name"],
                "contact_email": email,
                "blockchain_wallet_address": wallet,
                "registration_number": f"REG-HOSP-00{i+1}",
                "contact_number": f"987654321{i}",
                "address": "Hyderabad, Telangana",
                "city": "Hyderabad",
                "state": "Telangana"
            }
        )
        if p_created:
            print(f"Created profile for {hosp_data['name']} with wallet {wallet}")
        else:
            print(f"Updated profile for {hosp_data['name']} with wallet {wallet}")

    print("\nSeeding complete! All 5 hospitals are ready.")

if __name__ == "__main__":
    seed_hospitals()
