"""
Management command: seed_workflow_demo
======================================
Creates complete demo data to illustrate the full OrganChain workflow.

Donor 1 – Ramesh Kumar (ramesh01)
  Workflow: Registration → Admin Approval → Hospital Review → Organ Rejected → Case Closed
  Result:   NO blockchain record exists.

Donor 2 – Suresh Reddy (suresh01)
  Workflow: Registration → Admin Approval → Hospital Review → Organ Suitable →
            Submitted to Admin → Blockchain Approved → Matched with Priya →
            Transplant Completed
  Result:   Full blockchain trail exists.

Recipient – Priya Sharma
  Added by Apollo Hospital dashboard (no login account).
  Matched to Suresh's Liver.

Run with:
    python manage.py seed_workflow_demo [--reset]

The --reset flag wipes ONLY the two demo donors + their organs/transplants and
Priya Sharma before re-seeding (safe for use alongside existing data).
"""
import os
import sys
import shutil

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from core.models import (
    User, DonorProfile, HospitalProfile, OrganRecord, Recipient,
    Transplant, BlockchainTransaction, AuditLog, OrganStatusHistory,
    DeathCertificate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DEMO_USERNAMES = ('ramesh01', 'suresh01')
PRIYA_NAME     = 'Priya Sharma'
AVATAR_SRC     = os.path.join(
    settings.MEDIA_ROOT, 'profile_pics', 'demo_avatar.png'
)


def _copy_avatar(filename: str) -> str:
    """Copy the demo avatar to a uniquely-named file and return the relative path."""
    dest_rel  = f'profile_pics/{filename}'
    dest_abs  = os.path.join(settings.MEDIA_ROOT, 'profile_pics', filename)
    if os.path.exists(AVATAR_SRC):
        shutil.copy2(AVATAR_SRC, dest_abs)
    return dest_rel


def _log_status(organ, old, new, user):
    OrganStatusHistory.objects.create(
        organ_record=organ,
        previous_status=old,
        new_status=new,
        updated_by=user,
    )


def _audit(user, action, ip='127.0.0.1'):
    AuditLog.objects.create(user=user, action=action, ip_address=ip)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------
class Command(BaseCommand):
    help = (
        'Seeds Ramesh (rejected workflow) and Suresh (successful transplant '
        'workflow) demo donors plus recipient Priya Sharma.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete only the two demo donors + Priya before re-seeding.',
        )

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        # ── 1. Locate Apollo Hospital ──────────────────────────────────
        apollo = HospitalProfile.objects.filter(
            hospital_name__icontains='Apollo'
        ).first()
        if not apollo:
            raise CommandError(
                "Apollo Hospital not found. Please run 'seed_demo_data' first "
                "to create the base hospital accounts."
            )

        # ── 2. Locate Admin ────────────────────────────────────────────
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            raise CommandError(
                "No superuser found. Create one with: "
                "python manage.py createsuperuser"
            )

        # ── 3. Optional reset ──────────────────────────────────────────
        if options['reset']:
            self._reset_demo(admin_user)

        # ── 4. Guard: skip if already seeded ──────────────────────────
        if User.objects.filter(username__in=DEMO_USERNAMES).exists():
            existing = User.objects.filter(username__in=DEMO_USERNAMES).values_list(
                'username', flat=True
            )
            self.stdout.write(
                self.style.WARNING(
                    f"Demo accounts already exist: {list(existing)}. "
                    "Run with --reset to re-seed."
                )
            )
            return

        # ── 5. Seed data ───────────────────────────────────────────────
        with transaction.atomic():
            self._seed_ramesh(apollo, admin_user)
            self._seed_suresh(apollo, admin_user)

        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('[OK] Demo workflow data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        self.stdout.write('  Donor 1  | ramesh01  | password: Test@123')
        self.stdout.write('           | Workflow:  Rejected (no blockchain)')
        self.stdout.write('')
        self.stdout.write('  Donor 2  | suresh01  | password: Test@123')
        self.stdout.write('           | Workflow:  Transplanted (full blockchain)')
        self.stdout.write('')
        self.stdout.write('  Recipient | Priya Sharma - matched to Suresh, Apollo Hospital')
        self.stdout.write('')

    # ------------------------------------------------------------------
    # Reset helper
    # ------------------------------------------------------------------
    def _reset_demo(self, admin_user):
        self.stdout.write('[RESET] Removing existing demo records ...')
        for uname in DEMO_USERNAMES:
            user = User.objects.filter(username=uname).first()
            if user:
                # Delete in dependency order
                if hasattr(user, 'donorprofile'):
                    dp = user.donorprofile
                    Transplant.objects.filter(donor=dp).delete()
                    for org in OrganRecord.objects.filter(donor=dp):
                        OrganStatusHistory.objects.filter(organ_record=org).delete()
                        DeathCertificate.objects.filter(donor=dp).delete()
                    OrganRecord.objects.filter(donor=dp).delete()
                    BlockchainTransaction.objects.filter(donor=dp).delete()
                    AuditLog.objects.filter(user=user).delete()
                user.delete()
        # Remove Priya Sharma recipient
        Recipient.objects.filter(full_name=PRIYA_NAME).delete()
        self.stdout.write(self.style.SUCCESS('[OK] Reset complete.'))

    # ------------------------------------------------------------------
    # Donor 1 – Ramesh Kumar (rejected workflow)
    # ------------------------------------------------------------------
    def _seed_ramesh(self, apollo: HospitalProfile, admin_user: User):
        self.stdout.write('[DONOR 1] Creating Ramesh Kumar (Rejected workflow) ...')

        # ── User + DonorProfile ────────────────────────────────────────
        avatar_rel = _copy_avatar('ramesh01_avatar.png')

        ramesh_user = User.objects.create_user(
            username='ramesh01',
            password='Test@123',
            email='ramesh01@gmail.com',
            first_name='Ramesh',
            last_name='Kumar',
            is_donor=True,
            is_approved=True,   # Admin has approved the account
        )
        ramesh_user.profile_picture = avatar_rel
        ramesh_user.save()

        ramesh = DonorProfile.objects.create(
            user=ramesh_user,
            blood_group='A+',
            contact_number='9876543210',
            address='Kukatpally, Hyderabad',
            city='Hyderabad',
            state='Telangana',
            gender='male',
            age=35,
            pledged_organ='Kidney',
            is_deceased=True,       # Deceased – hospital has taken the case
            approval_status='Accepted',   # Admin approved the donor account
            assigned_hospital=apollo,
        )

        # ── OrganRecord – progress: Registered → Under Review →
        #                            Organ Rejected → Case Closed ───────
        organ = OrganRecord.objects.create(
            donor=ramesh,
            organ_type='Kidney',
            blood_group='A+',
            status='Case Closed',
            rejection_reason=(
                'Donor kidney found to be non-viable on pathological '
                'examination. Renal failure with severe cortical scarring '
                'identified during hospital review.'
            ),
            registered_by=apollo,
            recipient_hospital=None,
            # No blockchain fields – never reached admin approval
            blockchain_id=None,
            blockchain_tx_hash=None,
        )

        # ── Status History (full audit trail) ─────────────────────────
        steps = [
            (None,           'Registered',    admin_user),
            ('Registered',   'Under Review',  apollo.user),
            ('Under Review', 'Organ Rejected', apollo.user),
            ('Organ Rejected', 'Case Closed', apollo.user),
        ]
        for prev, nxt, usr in steps:
            _log_status(organ, prev, nxt, usr)

        # ── Audit Logs ─────────────────────────────────────────────────
        _audit(admin_user,  'Admin approved donor account ramesh01 (Pledge: Kidney) - Stored in Database as Registered.')
        _audit(apollo.user, 'Hospital accepted donation case for ramesh01 (Kidney) — Under Review.')
        _audit(apollo.user, 'Hospital rejected organ: Kidney for donor ramesh01 — Non-viable organ.')
        _audit(apollo.user, 'Hospital closed case for ramesh01. Organ Rejected — no blockchain transaction created.')

        self.stdout.write(self.style.SUCCESS('[OK] Ramesh Kumar seeded. Status: Case Closed (no blockchain).'))

    # ------------------------------------------------------------------
    # Donor 2 – Suresh Reddy (full successful workflow)
    # ------------------------------------------------------------------
    def _seed_suresh(self, apollo: HospitalProfile, admin_user: User):
        self.stdout.write('[DONOR 2] Creating Suresh Reddy (Successful transplant workflow) ...')

        # ── User + DonorProfile ────────────────────────────────────────
        avatar_rel = _copy_avatar('suresh01_avatar.png')

        suresh_user = User.objects.create_user(
            username='suresh01',
            password='Test@123',
            email='suresh01@gmail.com',
            first_name='Suresh',
            last_name='Reddy',
            is_donor=True,
            is_approved=True,
        )
        suresh_user.profile_picture = avatar_rel
        suresh_user.save()

        suresh = DonorProfile.objects.create(
            user=suresh_user,
            blood_group='O+',
            contact_number='9876543211',
            address='Madhapur, Hyderabad',
            city='Hyderabad',
            state='Telangana',
            gender='male',
            age=29,
            pledged_organ='Liver',
            is_deceased=True,
            approval_status='Accepted',
            assigned_hospital=apollo,
        )

        # ── Recipient – Priya Sharma (no login, added by Apollo) ───────
        priya = Recipient.objects.create(
            full_name='Priya Sharma',
            age=27,
            gender='female',
            blood_group='O+',
            organ_needed='Liver',
            hospital=apollo,
            doctor_assigned='Dr. Ravi Kumar',
            emergency_priority='High',
            medical_notes=(
                'Patient diagnosed with End-stage Liver Disease (ESLD). '
                'Requires emergency liver transplant. Blood group O+. '
                'Gachibowli, Hyderabad.'
            ),
            status='Transplanted',
            # Simulated blockchain IDs (no running blockchain needed for demo)
            blockchain_id='BC-REC-001',
            blockchain_tx_hash='0x' + 'b' * 64,
        )

        # ── OrganRecord – full happy path ─────────────────────────────
        # Use a very high blockchain_id to avoid collision with real blockchain records
        max_bc_id = OrganRecord.objects.exclude(blockchain_id=None).order_by('-blockchain_id').values_list('blockchain_id', flat=True).first() or 0
        demo_bc_id = max(max_bc_id + 1, 9001)
        uid = suresh_user.id
        fake_tx_hash = f'0xdemo{uid:04d}' + 'a' * (62 - len(f'{uid:04d}'))
        organ = OrganRecord.objects.create(
            donor=suresh,
            organ_type='Liver',
            blood_group='O+',
            status='Transplanted',
            registered_by=apollo,
            recipient_hospital=apollo,
            # Simulated blockchain data
            blockchain_id=demo_bc_id,
            blockchain_tx_hash=fake_tx_hash,
            blockchain_block_number=42,
            blockchain_timestamp=timezone.now(),
        )

        # ── Status History ─────────────────────────────────────────────
        steps = [
            (None,                  'Registered',          admin_user),
            ('Registered',          'Under Review',        apollo.user),
            ('Under Review',        'Organ Suitable',      apollo.user),
            ('Organ Suitable',      'Submitted to Admin',  apollo.user),
            ('Submitted to Admin',  'Available',           admin_user),
            ('Available',           'Matched',             admin_user),
            ('Matched',             'Transplanted',        admin_user),
        ]
        for prev, nxt, usr in steps:
            _log_status(organ, prev, nxt, usr)

        # ── Transplant record ──────────────────────────────────────────
        transplant = Transplant.objects.create(
            donor=suresh,
            recipient=priya,
            organ=organ,
            hospital=apollo,
            match_status='Completed',
            blockchain_tx_hash=fake_tx_hash,
        )

        # ── BlockchainTransaction records (organ registration + match + transplant) ─
        tx1 = f'0xreg{uid:04d}' + 'c' * (62 - len(f'{uid:04d}'))
        tx2 = f'0xrec{uid:04d}' + 'd' * (62 - len(f'{uid:04d}'))
        blockchain_entries = [
            {
                'donor': suresh,
                'recipient': None,
                'hospital': apollo,
                'organ_type': 'Liver',
                'tx_hash': tx1,
                'label': 'Organ registered on blockchain by Admin',
            },
            {
                'donor': suresh,
                'recipient': priya,
                'hospital': apollo,
                'organ_type': 'Liver',
                'tx_hash': tx2,
                'label': 'Recipient Priya Sharma registered on blockchain',
            },
            {
                'donor': suresh,
                'recipient': priya,
                'hospital': apollo,
                'organ_type': 'Liver',
                'tx_hash': fake_tx_hash,
                'label': 'Organ matched to Priya Sharma on blockchain',
            },
        ]
        for entry in blockchain_entries:
            BlockchainTransaction.objects.create(
                donor=entry['donor'],
                recipient=entry['recipient'],
                hospital=entry['hospital'],
                organ_type=entry['organ_type'],
                tx_hash=entry['tx_hash'],
            )

        # ── Audit Logs ─────────────────────────────────────────────────
        _audit(admin_user,  'Admin approved donor account suresh01 (Pledge: Liver) - Stored in Database as Registered.')
        _audit(apollo.user, 'Hospital accepted donation case for suresh01 (Liver) — Under Review.')
        _audit(apollo.user, 'Hospital marked organ as Organ Suitable for suresh01.')
        _audit(apollo.user, 'Hospital submitted case for suresh01 to Admin for final approval.')
        _audit(admin_user,  'Admin approved organ submission for suresh01 (Liver) and registered on blockchain as BC#1.')
        _audit(admin_user,  'Admin registered recipient Priya Sharma (BC-REC-001) on blockchain.')
        _audit(admin_user,  'Admin matched organ BC#1 (Liver) to recipient Priya Sharma (Apollo Hospital).')
        _audit(admin_user,  'Admin confirmed transplant for organ BC#1 (Liver). Transplant completed and recorded on blockchain.')

        self.stdout.write(self.style.SUCCESS('[OK] Suresh Reddy + Priya Sharma seeded. Status: Transplanted (blockchain).'))
