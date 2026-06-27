import sys
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from core.models import HospitalProfile, DonorProfile, OrganRecord, Recipient, Transplant, BlockchainTransaction, AuditLog, DeathCertificate, Feedback

User = get_user_model()

class Command(BaseCommand):
    help = "Clean database and seed fresh demo data for Organ Donation Tracking System"

    def handle(self, *args, **options):
        self.stdout.write("Starting database cleanup...")
        
        # 1. Cleanup existing records
        with transaction.atomic():
            # Delete dependents/matching tables first
            Transplant.objects.all().delete()
            BlockchainTransaction.objects.all().delete()
            DeathCertificate.objects.all().delete()
            AuditLog.objects.all().delete()
            Feedback.objects.all().delete()
            
            # Delete organs
            OrganRecord.objects.all().delete()
            
            # Delete recipients
            Recipient.objects.all().delete()
            
            # Delete donor users and profiles (Keep hospitals and admins)
            donor_users = User.objects.filter(is_donor=True)
            donor_users.delete() # Cascade deletes DonorProfile
            
            # Reset auto-increment IDs in sqlite_sequence
            if connection.vendor == 'sqlite':
                with connection.cursor() as cursor:
                    tables = [
                        'core_recipient',
                        'core_organrecord',
                        'core_transplant',
                        'core_blockchaintransaction',
                        'core_deathcertificate',
                        'core_auditlog',
                        'core_feedback'
                    ]
                    for table in tables:
                        try:
                            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                        except Exception as e:
                            self.stderr.write(f"Could not reset sequence for {table}: {e}")
            elif connection.vendor == 'mysql':
                with connection.cursor() as cursor:
                    tables = [
                        'core_recipient',
                        'core_organrecord',
                        'core_transplant',
                        'core_blockchaintransaction',
                        'core_deathcertificate',
                        'core_auditlog',
                        'core_feedback'
                    ]
                    for table in tables:
                        try:
                            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                        except Exception as e:
                            self.stderr.write(f"Could not reset sequence for {table}: {e}")
            
        self.stdout.write(self.style.SUCCESS("Cleanup completed successfully!"))
        
        self.stdout.write("Seeding fresh demo data...")
        
        # 2. Get or create hospitals (reusing existing configurations to keep keys/settings/wallet addresses intact)
        hospitals_data = [
            {"name": "Apollo Hospital", "username": "apollo_admin", "reg": "HOSP-AP-101", "email": "apollo@example.com"},
            {"name": "Yashoda Hospital", "username": "yashoda_admin", "reg": "HOSP-YA-102", "email": "yashoda@example.com"},
            {"name": "CARE Hospital", "username": "care_admin", "reg": "HOSP-CA-103", "email": "care@example.com"},
            {"name": "KIMS Hospital", "username": "kims_admin", "reg": "HOSP-KI-104", "email": "kims@example.com"},
            {"name": "AIG Hospital", "username": "aig_admin", "reg": "HOSP-AI-105", "email": "aig@example.com"},
        ]
        
        hospitals = []
        for h_info in hospitals_data:
            user, created = User.objects.get_or_create(
                username=h_info["username"],
                defaults={
                    "is_hospital": True,
                    "email": h_info["email"],
                    "is_approved": True,
                }
            )
            if created:
                user.set_password("Hospital123")
                user.save()
                
            profile, p_created = HospitalProfile.objects.get_or_create(
                user=user,
                defaults={
                    "hospital_name": h_info["name"],
                    "registration_number": h_info["reg"],
                    "contact_number": "1234567890",
                    "address": f"{h_info['name']} Street, Hyderabad",
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "blockchain_wallet_address": "0x" + "".join(["1"] * 40),
                }
            )
            hospitals.append(profile)
            
        # Helper dict to map name to profile
        hosp_map = {h.hospital_name: h for h in hospitals}
        
        # 3. Create Donors
        donors_data = [
            {
                "username": "rajesh_donor",
                "full_name": "Rajesh Kumar",
                "email": "rajesh@example.com",
                "blood_group": "A+",
                "organ": "Kidney",
                "hospital": "Apollo Hospital",
                "age": 34,
                "gender": "male",
                "city": "Hyderabad",
                "state": "Telangana",
                "address": "Madhapur, Hyderabad",
                "status": "Pending Verification",
                "is_deceased": False,
            },
            {
                "username": "sunita_donor",
                "full_name": "Sunita Sharma",
                "email": "sunita@example.com",
                "blood_group": "B+",
                "organ": "Liver",
                "hospital": "Yashoda Hospital",
                "age": 29,
                "gender": "female",
                "city": "Secunderabad",
                "state": "Telangana",
                "address": "Begumpet, Secunderabad",
                "status": "Pending Verification",
                "is_deceased": True,
            },
            {
                "username": "amit_donor",
                "full_name": "Amit Patel",
                "email": "amit@example.com",
                "blood_group": "O+",
                "organ": "Heart",
                "hospital": "CARE Hospital",
                "age": 42,
                "gender": "male",
                "city": "Hyderabad",
                "state": "Telangana",
                "address": "Banjara Hills, Hyderabad",
                "status": "Pending Verification",
                "is_deceased": False,
            },
            {
                "username": "priya_donor",
                "full_name": "Priya Nair",
                "email": "priya@example.com",
                "blood_group": "AB+",
                "organ": "Lung",
                "hospital": "KIMS Hospital",
                "age": 31,
                "gender": "female",
                "city": "Secunderabad",
                "state": "Telangana",
                "address": "Secunderabad Club Road",
                "status": "Pending Verification",
                "is_deceased": True,
            },
            {
                "username": "rohan_donor",
                "full_name": "Rohan Das",
                "email": "rohan@example.com",
                "blood_group": "O-",
                "organ": "Kidney",
                "hospital": "AIG Hospital",
                "age": 25,
                "gender": "male",
                "city": "Gachibowli",
                "state": "Telangana",
                "address": "AIG Campus, Gachibowli",
                "status": "Pending",
                "is_deceased": False,
            },
            {
                "username": "ananya_donor",
                "full_name": "Ananya Iyer",
                "email": "ananya@example.com",
                "blood_group": "A-",
                "organ": "Cornea",
                "hospital": "Apollo Hospital",
                "age": 27,
                "gender": "female",
                "city": "Jubilee Hills",
                "state": "Telangana",
                "address": "Jubilee Hills, Road No 36",
                "status": "Pending",
                "is_deceased": False,
            },
        ]
        
        for d_info in donors_data:
            first_name = d_info["full_name"].split()[0]
            last_name = d_info["full_name"].split()[1] if len(d_info["full_name"].split()) > 1 else ""
            
            d_user = User.objects.create_user(
                username=d_info["username"],
                password="Hospital123",
                email=d_info["email"],
                first_name=first_name,
                last_name=last_name,
                is_donor=True,
                is_approved=True
            )
            
            target_hosp = hosp_map[d_info["hospital"]]
            
            d_profile = DonorProfile.objects.create(
                user=d_user,
                approval_status=d_info["status"],
                assigned_hospital=target_hosp,
                blood_group=d_info["blood_group"],
                contact_number="9988776655",
                address=d_info["address"],
                city=d_info["city"],
                state=d_info["state"],
                gender=d_info["gender"],
                age=d_info["age"],
                pledged_organ=d_info["organ"],
                is_deceased=d_info["is_deceased"]
            )
            
            # For Pending Verification donors, automatically create the local OrganRecord
            if d_info["status"] == "Pending Verification":
                OrganRecord.objects.create(
                    donor=d_profile,
                    organ_type=d_info["organ"],
                    blood_group=d_info["blood_group"],
                    status='Pending Verification',
                    registered_by=target_hosp,
                    blockchain_id=None,
                    blockchain_tx_hash=None
                )
            
        self.stdout.write(self.style.SUCCESS("6 Donors created successfully!"))
        
        # 4. Create Recipients
        recipients_data = [
            {"name": "Suresh Raina", "hospital": "Apollo Hospital", "blood": "A+", "organ": "Kidney", "urgency": "High", "age": 45, "gender": "male"},
            {"name": "Deepa Mehta", "hospital": "Yashoda Hospital", "blood": "B+", "organ": "Liver", "urgency": "Medium", "age": 38, "gender": "female"},
            {"name": "Vikram Singh", "hospital": "CARE Hospital", "blood": "O+", "organ": "Heart", "urgency": "High", "age": 52, "gender": "male"},
            {"name": "Meera Bai", "hospital": "KIMS Hospital", "blood": "AB+", "organ": "Lung", "urgency": "Low", "age": 60, "gender": "female"},
            {"name": "Arjun Reddy", "hospital": "AIG Hospital", "blood": "O-", "organ": "Kidney", "urgency": "Medium", "age": 28, "gender": "male"},
            {"name": "Kavitha Rao", "hospital": "Apollo Hospital", "blood": "A-", "organ": "Cornea", "urgency": "High", "age": 33, "gender": "female"},
            {"name": "Ramesh Chand", "hospital": "Yashoda Hospital", "blood": "A+", "organ": "Kidney", "urgency": "Medium", "age": 50, "gender": "male"},
            {"name": "Shalini Sen", "hospital": "CARE Hospital", "blood": "B+", "organ": "Liver", "urgency": "Low", "age": 41, "gender": "female"},
            {"name": "Karan Johar", "hospital": "KIMS Hospital", "blood": "O+", "organ": "Heart", "urgency": "Medium", "age": 48, "gender": "male"},
            {"name": "Neetu Singh", "hospital": "AIG Hospital", "blood": "AB+", "organ": "Lung", "urgency": "High", "age": 55, "gender": "female"},
            {"name": "Harish Verma", "hospital": "Apollo Hospital", "blood": "O-", "organ": "Kidney", "urgency": "Low", "age": 64, "gender": "male"},
            {"name": "Divya Pillai", "hospital": "Yashoda Hospital", "blood": "A-", "organ": "Cornea", "urgency": "Medium", "age": 29, "gender": "female"},
            {"name": "Sanjay Dutt", "hospital": "CARE Hospital", "blood": "A+", "organ": "Kidney", "urgency": "High", "age": 59, "gender": "male"},
            {"name": "Geeta Phogat", "hospital": "KIMS Hospital", "blood": "B+", "organ": "Liver", "urgency": "High", "age": 31, "gender": "female"},
            {"name": "Vijay Deverakonda", "hospital": "AIG Hospital", "blood": "O+", "organ": "Heart", "urgency": "Low", "age": 35, "gender": "male"},
        ]
        
        for r_info in recipients_data:
            target_hosp = hosp_map[r_info["hospital"]]
            Recipient.objects.create(
                full_name=r_info["name"],
                age=r_info["age"],
                gender=r_info["gender"],
                blood_group=r_info["blood"],
                organ_needed=r_info["organ"],
                hospital=target_hosp,
                doctor_assigned="Dr. Srinivas",
                emergency_priority=r_info["urgency"],
                medical_notes=f"Requires compatible {r_info['blood']} {r_info['organ']} transplant.",
                status='Requested'
            )
            
        self.stdout.write(self.style.SUCCESS("15 Recipients created successfully!"))
        self.stdout.write(self.style.SUCCESS("All tasks completed! Database has been cleaned and seeded with fresh demo data!"))
