import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organ_donation_project.settings')
django.setup()

from core.models import DonorProfile, HospitalProfile, OrganRecord, User


PASSWORD = "Admin123"


def ensure_hospital(username, hospital_name, registration_number):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@demo.local',
            'is_hospital': True,
        },
    )
    if created:
        user.set_password(PASSWORD)
        user.is_hospital = True
        user.save()

    hospital, _ = HospitalProfile.objects.get_or_create(
        user=user,
        defaults={
            'hospital_name': hospital_name,
            'registration_number': registration_number,
            'contact_number': '9999999999',
            'address': f'{hospital_name} Demo Address',
        },
    )
    return hospital


def ensure_donor(username, blood_group, contact_number):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@demo.local',
            'is_donor': True,
        },
    )
    if created:
        user.set_password(PASSWORD)
        user.is_donor = True
        user.save()

    donor, _ = DonorProfile.objects.get_or_create(
        user=user,
        defaults={
            'blood_group': blood_group,
            'contact_number': contact_number,
            'address': 'Demo Donor Address',
        },
    )
    return donor


def next_blockchain_id():
    current = OrganRecord.objects.order_by('-blockchain_id').first()
    return 1 if current is None else current.blockchain_id + 1


def main():
    ace_hospital = ensure_hospital('acehospital_1', 'Ace Hospital', 'ACE-DEMO-001')
    source_one = ensure_hospital('demo_source_1', 'Demo Source Hospital 1', 'SRC-DEMO-001')
    source_two = ensure_hospital('demo_source_2', 'Demo Source Hospital 2', 'SRC-DEMO-002')

    donor_one = ensure_donor('demo_donor_1', 'A+', '8888888881')
    donor_two = ensure_donor('demo_donor_2', 'O-', '8888888882')

    demos = [
        (donor_one, source_one, 'Kidney'),
        (donor_two, source_two, 'Liver'),
    ]

    created = 0
    blockchain_id = next_blockchain_id()

    for donor, source_hospital, organ_type in demos:
        organ, was_created = OrganRecord.objects.get_or_create(
            donor=donor,
            organ_type=organ_type,
            registered_by=source_hospital,
            defaults={
                'blockchain_id': blockchain_id,
                'blood_group': donor.blood_group,
                'status': 'Available',
            },
        )
        if was_created:
            created += 1
            blockchain_id += 1
            print(f'Created demo organ #{organ.blockchain_id}: {organ.organ_type} for {ace_hospital.user.username} matching view')
        else:
            print(f'Already exists: {organ.organ_type} from {source_hospital.hospital_name}')

    print(f'Demo setup complete for {ace_hospital.user.username}. New organs created: {created}')


if __name__ == '__main__':
    main()
