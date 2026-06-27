from unittest.mock import patch
import tempfile

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings

from .forms import BLOOD_GROUP_CHOICES, ORGAN_TYPE_CHOICES, DonorRegistrationForm
from .models import DonorProfile, HospitalProfile, OrganRecord, User, Recipient


class FormChoicesTests(TestCase):
    def test_blood_group_labels_include_positive_negative_text(self):
        labels = dict(BLOOD_GROUP_CHOICES)
        self.assertEqual(labels['A+'], 'A+ (Positive)')
        self.assertEqual(labels['O-'], 'O- (Negative)')

    def test_donor_registration_form_includes_common_pledge_organs(self):
        organ_choices = dict(DonorRegistrationForm().fields['pledged_organ'].choices)
        self.assertIn('Kidney', organ_choices)
        self.assertIn('Liver', organ_choices)
        self.assertIn('Heart', organ_choices)


class MatchOrganViewTests(TestCase):
    def setUp(self):
        self.password = 'Admin123'

        self.source_user = User.objects.create_user(username='source_hospital', password=self.password, is_hospital=True)
        self.source_hospital = HospitalProfile.objects.create(
            user=self.source_user,
            hospital_name='Source Hospital',
            registration_number='SRC-001',
            contact_number='1111111111',
            address='Source Address',
        )

        self.ace_user = User.objects.create_user(username='acehospital_1', password=self.password, is_hospital=True)
        self.ace_hospital = HospitalProfile.objects.create(
            user=self.ace_user,
            hospital_name='Ace Hospital',
            registration_number='ACE-001',
            contact_number='2222222222',
            address='Ace Address',
        )

        self.third_user = User.objects.create_user(username='third_hospital', password=self.password, is_hospital=True)
        self.third_hospital = HospitalProfile.objects.create(
            user=self.third_user,
            hospital_name='Third Hospital',
            registration_number='THD-001',
            contact_number='3333333333',
            address='Third Address',
        )

        self.donor_user = User.objects.create_user(username='demo_donor', password=self.password, is_donor=True)
        self.donor = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group='A+',
            contact_number='9999999999',
            address='Donor Address',
        )

        self.organ = OrganRecord.objects.create(
            blockchain_id=101,
            donor=self.donor,
            organ_type='Kidney',
            blood_group='A+',
            status='Available',
            registered_by=self.source_hospital,
        )

    def test_admin_can_complete_transplant_of_matched_organ(self):
        with patch('core.views.transplant_organ_on_chain', return_value=True):
            admin = User.objects.create_superuser(username='admin', password=self.password, email='admin@example.com')
            self.client.force_login(admin)

            # Set up a matched organ and transplant record
            self.organ.status = 'Matched'
            self.organ.recipient_hospital = self.ace_hospital
            self.organ.save(update_fields=['status', 'recipient_hospital'])

            # Create recipient in the target hospital
            from .models import Recipient
            recipient = Recipient.objects.create(
                full_name="Alice Smith",
                age=30,
                gender="female",
                blood_group="A+",
                organ_needed="Kidney",
                hospital=self.ace_hospital,
                doctor_assigned="Dr. House",
                blockchain_id="123"  # Set to bypass blockchain registration in view
            )

            from .models import Transplant
            Transplant.objects.create(
                donor=self.donor,
                recipient=recipient,
                organ=self.organ,
                hospital=self.ace_hospital,
                match_status='Approved'
            )

            response = self.client.post(
                reverse('admin_complete_transplant', args=[self.organ.pk])
            )

            self.assertRedirects(response, reverse('admin_dashboard'))
            self.organ.refresh_from_db()
            self.assertEqual(self.organ.status, 'Transplanted')

    def test_hospital_can_edit_owned_organ_details(self):
        self.organ.status = 'Under Testing'
        self.organ.blockchain_id = None
        self.organ.save()
        self.client.force_login(self.source_user)

        response = self.client.post(
            reverse('hospital_update_organ_status', args=[self.organ.pk]),
            {
                'organ_type': 'Liver',
                'blood_group': 'O-',
                'status': 'Eligible',
            },
        )

        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.organ_type, 'Liver')
        self.assertEqual(self.organ.blood_group, 'O-')


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProfilePictureUploadTests(TestCase):
    def test_donor_can_upload_profile_picture(self):
        user = User.objects.create_user(username='photo_user', password='Admin123', is_donor=True)
        DonorProfile.objects.create(
            user=user,
            blood_group='B+',
            contact_number='7777777777',
            address='Donor Street',
            approval_status='Accepted',
        )
        self.client.force_login(user)

        image = SimpleUploadedFile(
            'avatar.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(reverse('update_profile_picture'), {'profile_picture': image})

        self.assertRedirects(response, reverse('donor_dashboard'))
        user.refresh_from_db()
        self.assertTrue(bool(user.profile_picture))

    def test_donor_can_update_profile_and_password_from_dashboard(self):
        user = User.objects.create_user(username='donor_profile', password='OldPass123', is_donor=True)
        profile = DonorProfile.objects.create(
            user=user,
            blood_group='B+',
            contact_number='7777777777',
            address='Old Donor Street',
            approval_status='Accepted',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('donor_dashboard'),
            {
                'form_type': 'edit_profile',
                'first_name': 'Demo',
                'last_name': 'Donor',
                'email': 'donor@example.com',
                'blood_group': 'O+',
                'contact_number': '8888888888',
                'city': 'Pune',
                'state': 'Maharashtra',
                'address': 'New Donor Street',
                'new_password': 'NewPass123',
                'confirm_password': 'NewPass123',
            },
        )

        self.assertRedirects(response, reverse('donor_dashboard'))
        user.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(user.first_name, 'Demo')
        self.assertEqual(user.email, 'donor@example.com')
        self.assertTrue(user.check_password('NewPass123'))
        self.assertEqual(profile.blood_group, 'O+')
        self.assertEqual(profile.city, 'Pune')

    def test_donor_profile_dashboard_renders(self):
        user = User.objects.create_user(username='render_donor', password='Admin123', is_donor=True)
        DonorProfile.objects.create(
            user=user,
            blood_group='A+',
            contact_number='7777777777',
            address='Donor Street',
            approval_status='Accepted',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('donor_dashboard') + '#donor-profile')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Save Profile & Password')

    def test_hospital_can_update_profile_logo_fields_and_password_from_dashboard(self):
        user = User.objects.create_user(
            username='old_hospital_login',
            password='OldPass123',
            email='old@example.com',
            is_hospital=True,
        )
        hospital = HospitalProfile.objects.create(
            user=user,
            hospital_name='Old Hospital',
            registration_number='HOSP-PROF-001',
            contact_number='1111111111',
            address='Old Hospital Address',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('hospital_dashboard'),
            {
                'form_type': 'update_details',
                'username': 'new_hospital_login',
                'email': 'new@example.com',
                'hospital_name': 'New Hospital',
                'contact_email': 'contact@newhospital.example',
                'contact_number': '2222222222',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'address': 'New Hospital Address',
                'new_password': 'NewPass123',
                'confirm_password': 'NewPass123',
            },
        )

        self.assertRedirects(response, reverse('hospital_dashboard'))
        user.refresh_from_db()
        hospital.refresh_from_db()
        self.assertEqual(user.username, 'new_hospital_login')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('NewPass123'))
        self.assertEqual(hospital.hospital_name, 'New Hospital')
        self.assertEqual(hospital.contact_email, 'contact@newhospital.example')
        self.assertEqual(hospital.city, 'Mumbai')

    def test_hospital_profile_dashboard_renders(self):
        user = User.objects.create_user(username='render_hospital', password='Admin123', is_hospital=True)
        HospitalProfile.objects.create(
            user=user,
            hospital_name='Render Hospital',
            registration_number='HOSP-RENDER-001',
            contact_number='1111111111',
            address='Render Hospital Address',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('hospital_dashboard') + '#hosp-profile')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Save Profile')

    def test_admin_can_upload_hospital_background(self):
        admin = User.objects.create_superuser(username='bg_admin', password='Admin123', email='admin@example.com')
        hospital_user = User.objects.create_user(username='bg_hospital', password='Admin123', is_hospital=True)
        hospital = HospitalProfile.objects.create(
            user=hospital_user,
            hospital_name='Background Hospital',
            registration_number='BG-001',
            contact_number='1111111111',
            address='Background Address',
        )
        self.client.force_login(admin)
        background = SimpleUploadedFile(
            'hospital-bg.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(
            reverse('admin_dashboard'),
            {
                'admin_action': 'update_user',
                'user_id': hospital_user.pk,
                'username': hospital_user.username,
                'email': hospital_user.email,
                'first_name': '',
                'last_name': '',
                'hospital_name': 'Background Hospital',
                'role': 'hospital',
                'status': 'active',
                'background_image': background,
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        hospital.refresh_from_db()
        self.assertTrue(bool(hospital.background_image))

    def test_admin_can_update_own_dashboard_background(self):
        admin = User.objects.create_superuser(
            username='admin_background',
            password='Admin123',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
        )
        self.client.force_login(admin)
        background = SimpleUploadedFile(
            'admin-bg.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(
            reverse('admin_dashboard'),
            {
                'admin_action': 'update_admin_profile',
                'username': admin.username,
                'email': admin.email,
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'background_image': background,
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        admin.refresh_from_db()
        self.assertTrue(bool(admin.background_image))

    def test_admin_dashboard_background_renders(self):
        admin = User.objects.create_superuser(username='admin_bg_render', password='Admin123', email='admin@example.com')
        admin.background_image.save(
            'admin-render-bg.gif',
            SimpleUploadedFile(
                'admin-render-bg.gif',
                b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
                content_type='image/gif',
            ),
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('admin_dashboard') + '#admin-profile')

        self.assertContains(response, 'admin-bg-shell has-image')
        self.assertContains(response, 'Dashboard background')

    def test_hospital_background_renders_on_home_and_dashboard(self):
        user = User.objects.create_user(username='bg_render_hospital', password='Admin123', is_hospital=True)
        hospital = HospitalProfile.objects.create(
            user=user,
            hospital_name='Render Background Hospital',
            registration_number='BG-RENDER-001',
            contact_number='1111111111',
            address='Background Address',
        )
        hospital.background_image.save(
            'render-bg.gif',
            SimpleUploadedFile(
                'render-bg.gif',
                b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
                content_type='image/gif',
            ),
        )
        self.client.force_login(user)

        home_response = self.client.get(reverse('home'))
        dashboard_response = self.client.get(reverse('hospital_dashboard'))

        self.assertContains(home_response, 'hospital-home-bg')
        self.assertContains(dashboard_response, 'hospital-bg-shell has-image')


class AdminHospitalManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_master',
            password='Admin123',
            email='admin@example.com',
        )

    def test_admin_can_add_hospital_from_dashboard(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('admin_dashboard'),
            {
                'admin_action': 'add_hospital',
                'hospital_name': 'New Admin Hospital',
                'username': 'new_admin_hospital',
                'email': 'hospital@example.com',
                'password': 'Admin123',
                'registration_number': 'ADM-NEW-001',
                'contact_number': '5555555555',
                'address': 'Admin Created Address',
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(User.objects.filter(username='new_admin_hospital', is_hospital=True).exists())
        self.assertTrue(HospitalProfile.objects.filter(registration_number='ADM-NEW-001').exists())

    def test_admin_can_delete_hospital(self):
        hospital_user = User.objects.create_user(username='delete_me_hospital', password='Admin123', is_hospital=True)
        hospital = HospitalProfile.objects.create(
            user=hospital_user,
            hospital_name='Delete Me Hospital',
            registration_number='DEL-001',
            contact_number='1111111111',
            address='Delete Address',
        )
        self.client.force_login(self.admin)

        response = self.client.post(reverse('delete_hospital', args=[hospital.pk]))

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertFalse(HospitalProfile.objects.filter(pk=hospital.pk).exists())
        self.assertFalse(User.objects.filter(username='delete_me_hospital').exists())

    def test_admin_can_update_hospital_user_and_approval_status(self):
        hospital_user = User.objects.create_user(
            username='old_hospital_user',
            password='Admin123',
            email='old@example.com',
            is_hospital=True,
        )
        hospital = HospitalProfile.objects.create(
            user=hospital_user,
            hospital_name='Old Hospital',
            registration_number='UPD-001',
            contact_number='1111111111',
            address='Old Address',
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('admin_update_user', args=[hospital_user.pk]),
            {
                'username': 'new_hospital_user',
                'email': 'new@example.com',
                'first_name': 'New',
                'last_name': 'Owner',
                'hospital_name': 'New Hospital',
                'role': 'hospital',
                'status': 'blocked',
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        hospital_user.refresh_from_db()
        hospital.refresh_from_db()
        self.assertEqual(hospital_user.username, 'new_hospital_user')
        self.assertEqual(hospital_user.email, 'new@example.com')
        self.assertFalse(hospital_user.is_active)
        self.assertTrue(hospital_user.is_hospital)
        self.assertEqual(hospital.hospital_name, 'New Hospital')

    def test_admin_can_update_organ_status(self):
        hospital_user = User.objects.create_user(username='status_hospital', password='Admin123', is_hospital=True)
        hospital = HospitalProfile.objects.create(
            user=hospital_user,
            hospital_name='Status Hospital',
            registration_number='STS-001',
            contact_number='1111111111',
            address='Status Address',
        )
        donor_user = User.objects.create_user(username='status_donor', password='Admin123', is_donor=True)
        donor = DonorProfile.objects.create(
            user=donor_user,
            blood_group='O+',
            contact_number='2222222222',
            address='Donor Address',
        )
        organ = OrganRecord.objects.create(
            blockchain_id=909,
            donor=donor,
            organ_type='Heart',
            blood_group='O+',
            registered_by=hospital,
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('admin_update_organ_status', args=[organ.pk]),
            {'status': 'Transplanted'},
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        organ.refresh_from_db()
        self.assertEqual(organ.status, 'Transplanted')


class OrganWorkflowTests(TestCase):
    def setUp(self):
        self.password = 'Admin123'
        self.admin = User.objects.create_superuser(username='admin_wf', password=self.password, email='admin@example.com')
        
        self.hospital_user = User.objects.create_user(username='hosp_wf', password=self.password, is_hospital=True)
        self.hospital = HospitalProfile.objects.create(
            user=self.hospital_user,
            hospital_name='Workflow Hospital',
            registration_number='WF-HOSP-001',
            contact_number='1112223333',
            address='Workflow Street',
            blockchain_wallet_address='0x90F8bf6A479f320ead074411a4B0e7944EAE8626',
        )
        
        self.donor_user = User.objects.create_user(username='donor_wf', password=self.password, is_donor=True)
        self.donor = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group='O+',
            contact_number='4445556666',
            address='Donor Street',
            approval_status='Accepted',
        )
        
        # Admin approves donor and automatically creates Registered OrganRecord
        self.organ = OrganRecord.objects.create(
            donor=self.donor,
            organ_type='Kidney',
            blood_group='O+',
            status='Registered',
            registered_by=self.hospital,
        )

    def test_hospital_local_transitions(self):
        self.client.force_login(self.hospital_user)
        self.organ.status = 'Pending'
        self.organ.save()

        # 1. Pending -> Under Testing
        response = self.client.post(
            reverse('hospital_transition_organ', args=[self.organ.pk]),
            {'status': 'Under Testing'}
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Under Testing')

        # 2. Under Testing -> Eligible (Waiting For Blockchain Approval)
        response = self.client.post(
            reverse('hospital_transition_organ', args=[self.organ.pk]),
            {'status': 'Eligible'}
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Waiting For Blockchain Approval')

    def test_hospital_rejection_transition(self):
        self.client.force_login(self.hospital_user)
        self.organ.status = 'Under Testing'
        self.organ.save()

        # Under Testing -> Rejected
        response = self.client.post(
            reverse('hospital_transition_organ', args=[self.organ.pk]),
            {'status': 'Rejected', 'medical_remarks': 'Medical failure'}
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Rejected')

    @patch('core.views.register_organ_on_chain')
    def test_admin_approve_organ_write_to_blockchain(self, mock_register):
        from django.utils import timezone
        mock_register.return_value = {
            'blockchain_id': 202,
            'transaction_hash': '0xhash',
            'block_number': 42,
            'timestamp': timezone.now(),
        }
        self.organ.status = 'Waiting For Blockchain Approval'
        self.organ.save()

        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin_approve_organ', args=[self.organ.pk]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Blockchain Verified')
        self.assertEqual(self.organ.blockchain_id, 202)
        mock_register.assert_called_once()

    def test_admin_reject_and_return_organ(self):
        self.client.force_login(self.admin)

        # Case 1: Return for correction (action == 'return' -> Under Testing)
        self.organ.status = 'Waiting For Blockchain Approval'
        self.organ.save()
        response = self.client.post(
            reverse('admin_reject_organ', args=[self.organ.pk]),
            {'action': 'return'}
        )
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Under Testing')

        # Case 2: Permanent Rejection (action != 'return' -> Rejected)
        self.organ.status = 'Waiting For Blockchain Approval'
        self.organ.save()
        response = self.client.post(
            reverse('admin_reject_organ', args=[self.organ.pk]),
            {'action': 'reject'}
        )
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Rejected')

    def test_delete_organ_permissions(self):
        # 1. Hospital CANNOT delete organ
        self.client.force_login(self.hospital_user)
        response = self.client.post(reverse('delete_organ', args=[self.organ.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect with error
        self.assertTrue(OrganRecord.objects.filter(pk=self.organ.pk).exists())

        # 2. Admin CAN delete rejected organ
        self.client.force_login(self.admin)
        self.organ.status = 'Rejected'
        self.organ.save()
        response = self.client.post(reverse('delete_organ', args=[self.organ.pk]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertFalse(OrganRecord.objects.filter(pk=self.organ.pk).exists())

        # Re-create donor and organ for next tests
        new_donor_user = User.objects.create_user(username='donor_wf_new', password=self.password, is_donor=True)
        new_donor = DonorProfile.objects.create(
            user=new_donor_user,
            blood_group='O+',
            contact_number='4445556666',
            address='Donor Street',
            approval_status='Accepted',
        )
        self.organ = OrganRecord.objects.create(
            donor=new_donor,
            organ_type='Kidney',
            blood_group='O+',
            status='Submitted to Admin',
            registered_by=self.hospital,
        )

        # 2. Hospital CANNOT delete submitted organ
        response = self.client.post(reverse('delete_organ', args=[self.organ.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect with error
        self.assertTrue(OrganRecord.objects.filter(pk=self.organ.pk).exists())

        # 3. Admin CAN delete un-blockchain-registered organ
        self.client.force_login(self.admin)
        self.organ.status = 'Rejected'
        self.organ.save()
        response = self.client.post(reverse('delete_organ', args=[self.organ.pk]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertFalse(OrganRecord.objects.filter(pk=self.organ.pk).exists())


class DonorVerificationWorkflowTests(TestCase):
    def setUp(self):
        self.password = 'Admin123'
        self.admin = User.objects.create_superuser(username='admin_dv', password=self.password, email='admin@example.com')
        
        self.hospital_user = User.objects.create_user(username='hosp_dv', password=self.password, is_hospital=True)
        self.hospital = HospitalProfile.objects.create(
            user=self.hospital_user,
            hospital_name='Verification Hospital',
            registration_number='VH-001',
            contact_number='1112223333',
            address='Verification St',
            blockchain_wallet_address='0x90F8bf6A479f320ead074411a4B0e7944EAE8626',
        )

    def test_donor_registration_without_assigned_hospital(self):
        from .forms import DonorRegistrationForm
        form = DonorRegistrationForm(data={
            'username': 'registered_donor_test',
            'email': 'donor_test@example.com',
            'first_name': 'Test',
            'last_name': 'Donor',
            'age': 35,
            'medical_history': 'None',
            'blood_group': 'B+',
            'gender': 'male',
            'contact_number': '1234567890',
            'address': 'Test Road',
            'pledged_organ': 'Heart',
            'password1': 'Password123!',
            'password2': 'Password123!',
            'policy_accepted': True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        donor = user.donorprofile
        self.assertEqual(donor.approval_status, 'Pending')
        self.assertTrue(user.is_approved)

    @patch('core.views.register_organ_on_chain')
    def test_donor_registration_and_blockchain_approval_flow(self, mock_register):
        from django.utils import timezone
        mock_register.return_value = {
            'blockchain_id': 202,
            'transaction_hash': '0xhash',
            'block_number': 42,
            'timestamp': timezone.now(),
        }
        
        # 1. Register donor
        from .forms import DonorRegistrationForm
        form = DonorRegistrationForm(data={
            'username': 'registered_donor_flow',
            'email': 'donor_flow@example.com',
            'first_name': 'Test',
            'last_name': 'Donor',
            'age': 35,
            'medical_history': 'None',
            'blood_group': 'B+',
            'gender': 'male',
            'contact_number': '1234567890',
            'address': 'Test Road',
            'pledged_organ': 'Heart',
            'password1': 'Password123!',
            'password2': 'Password123!',
            'policy_accepted': True,
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        donor = user.donorprofile
        self.assertEqual(donor.approval_status, 'Pending')
        self.assertTrue(user.is_approved)
        
        # An OrganRecord is automatically created with status Pending
        organ = OrganRecord.objects.get(donor=donor)
        self.assertEqual(organ.status, 'Pending')
        
        # 2. Hospital updates to Eligible
        self.client.force_login(self.hospital_user)
        response = self.client.post(
            reverse('hospital_update_organ_status', args=[organ.pk]),
            {
                'organ_type': 'Heart',
                'blood_group': 'B+',
                'status': 'Eligible',
                'medical_remarks': 'Perfect heart',
            }
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        organ.refresh_from_db()
        self.assertEqual(organ.status, 'Waiting For Blockchain Approval')
        
        # 3. Admin approves for Blockchain
        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin_approve_organ', args=[organ.pk]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        organ.refresh_from_db()
        self.assertEqual(organ.status, 'Blockchain Verified')
        self.assertEqual(organ.blockchain_id, 202)

    def test_hospital_rejects_donor(self):
        donor_user = User.objects.create_user(username='pending_donor', password=self.password, is_donor=True)
        donor = DonorProfile.objects.create(
            user=donor_user,
            blood_group='O+',
            contact_number='9990001111',
            address='Donor Addr',
            pledged_organ='Kidney',
            approval_status='Pending',
            assigned_hospital=self.hospital,
        )
        organ = OrganRecord.objects.create(
            donor=donor,
            organ_type='Kidney',
            blood_group='O+',
            status='Pending',
            registered_by=self.hospital,
        )
        self.client.force_login(self.hospital_user)
        response = self.client.post(
            reverse('hospital_update_organ_status', args=[organ.pk]),
            {
                'organ_type': 'Kidney',
                'blood_group': 'O+',
                'status': 'Rejected',
                'medical_remarks': 'Disqualified',
            }
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        donor.refresh_from_db()
        self.assertEqual(donor.approval_status, 'Rejected')

    def test_admin_cannot_delete_blockchain_registered_donor(self):
        donor_user = User.objects.create_user(username='bc_donor', password=self.password, is_donor=True)
        donor = DonorProfile.objects.create(
            user=donor_user,
            blood_group='O+',
            contact_number='9990001111',
            address='Donor Addr',
            pledged_organ='Kidney',
            approval_status='Accepted',
            is_deceased=True,
        )
        organ = OrganRecord.objects.create(
            donor=donor,
            organ_type='Kidney',
            blood_group='O+',
            status='Available',
            blockchain_id=123,
            blockchain_tx_hash='0x1234567890abcdef',
            registered_by=self.hospital,
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('delete_user', args=[donor_user.id]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify user still exists
        self.assertTrue(User.objects.filter(pk=donor_user.id).exists())

    def test_admin_can_delete_deceased_donor_credentials(self):
        # Create a deceased donor
        donor_user = User.objects.create_user(username='deceased_donor', password=self.password, is_donor=True)
        donor = DonorProfile.objects.create(
            user=donor_user,
            blood_group='O+',
            contact_number='9990001111',
            address='Donor Addr',
            pledged_organ='Kidney',
            approval_status='Accepted',
            is_deceased=True,
        )

        self.client.force_login(self.admin)

        response = self.client.post(reverse('delete_user', args=[donor_user.id]))
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertFalse(User.objects.filter(pk=donor_user.id).exists())
        self.assertFalse(DonorProfile.objects.filter(pk=donor_user.id).exists())


class AdminOnlyFeatureTests(TestCase):
    def setUp(self):
        self.password = 'Admin123'
        self.admin = User.objects.create_superuser(username='admin_feat', password=self.password, email='admin@example.com')
        
        self.hospital_user = User.objects.create_user(username='hosp_feat', password=self.password, is_hospital=True)
        self.hospital = HospitalProfile.objects.create(
            user=self.hospital_user,
            hospital_name='Features Hospital',
            registration_number='FH-001',
            contact_number='1112223333',
            address='Features St',
            blockchain_wallet_address='0x90F8bf6A479f320ead074411a4B0e7944EAE8626',
        )
        
        self.donor_user = User.objects.create_user(username='donor_feat', password=self.password, is_donor=True)
        self.donor = DonorProfile.objects.create(
            user=self.donor_user,
            blood_group='A+',
            contact_number='9999999999',
            address='Donor Addr',
            pledged_organ='Kidney',
            approval_status='Approved',
            assigned_hospital=self.hospital,
        )
        
        self.organ = OrganRecord.objects.create(
            donor=self.donor,
            organ_type='Kidney',
            blood_group='A+',
            status='Approved',
            registered_by=self.hospital,
        )
        
        from .models import Recipient
        self.recipient = Recipient.objects.create(
            full_name="Bob Patient",
            age=45,
            gender="male",
            blood_group="A+",
            organ_needed="Kidney",
            hospital=self.hospital,
            doctor_assigned="Dr. House"
        )

    def test_hospital_cannot_match_organ(self):
        self.client.force_login(self.hospital_user)
        response = self.client.post(reverse('match_organ', args=[self.organ.pk]))
        self.assertRedirects(response, f"/login/?next={reverse('match_organ', args=[self.organ.pk])}")
        self.organ.refresh_from_db()
        self.assertNotEqual(self.organ.status, 'Matched')

    @patch('core.views.register_organ_on_chain')
    @patch('core.views.register_recipient_on_chain')
    @patch('core.views.match_organ_on_chain')
    def test_admin_can_match_organ(self, mock_match, mock_register_recipient, mock_register_organ):
        mock_register_recipient.return_value = {
            'blockchain_id': 'BC-1001',
            'transaction_hash': '0xrecipient',
        }
        mock_register_organ.return_value = {
            'blockchain_id': 1,
            'transaction_hash': '0xorgan',
            'block_number': 1,
            'timestamp': None,
        }
        mock_match.return_value = {
            'transaction_hash': '0xmatch',
            'block_number': 2,
            'status': 1,
        }
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('admin_match_organ', args=[self.organ.pk]),
            {'recipient_id': self.recipient.pk}
        )
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Matched')
        self.assertEqual(self.organ.recipient_hospital, self.hospital)
        
        self.recipient.refresh_from_db()
        self.assertEqual(self.recipient.status, 'Matched')
        
        from .models import Transplant
        self.assertTrue(Transplant.objects.filter(organ=self.organ, recipient=self.recipient).exists())

    def test_admin_matching_compatibility_validation(self):
        from .models import Recipient
        incompatible_recipient = Recipient.objects.create(
            full_name="Bob Patient Incompatible",
            age=45,
            gender="male",
            blood_group="B-",
            organ_needed="Kidney",
            hospital=self.hospital,
            doctor_assigned="Dr. House"
        )
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('admin_match_organ', args=[self.organ.pk]),
            {'recipient_id': incompatible_recipient.pk}
        )
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertNotEqual(self.organ.status, 'Matched')

    def test_hospital_can_set_death_statuses_and_marks_donor_deceased(self):
        self.client.force_login(self.hospital_user)
        response = self.client.post(
            reverse('hospital_update_organ_status', args=[self.organ.pk]),
            {
                'organ_type': 'Kidney',
                'blood_group': 'A+',
                'status': 'Death but Eligible Transplant',
                'medical_remarks': 'Deceased eligible',
            }
        )
        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Death but Eligible Transplant')
        
        self.donor.refresh_from_db()
        self.assertEqual(self.donor.approval_status, 'Death but Eligible Transplant')
        self.assertTrue(self.donor.is_deceased)

    def test_recipient_edit_delete(self):
        recipient = Recipient.objects.create(
            full_name="Bob Patient",
            age=45,
            gender="male",
            blood_group="A+",
            organ_needed="Kidney",
            hospital=self.hospital,
            doctor_assigned="Dr. House"
        )
        self.client.force_login(self.hospital_user)
        response = self.client.post(
            reverse('hospital_edit_recipient', args=[recipient.pk]),
            {
                'full_name': "Bob Patient Edited",
                'age': 46,
                'gender': "male",
                'blood_group': "A+",
                'organ_needed': "Kidney",
                'doctor_assigned': "Dr. House Updated",
                'emergency_priority': "High",
                'medical_notes': "Severe kidney disease"
            }
        )
        self.assertRedirects(response, '/dashboard/hospital/#hosp-recipients')
        recipient.refresh_from_db()
        self.assertEqual(recipient.full_name, "Bob Patient Edited")
        self.assertEqual(recipient.age, 46)
        self.assertEqual(recipient.emergency_priority, "High")
        
        response = self.client.post(reverse('hospital_delete_recipient', args=[recipient.pk]))
        self.assertRedirects(response, '/dashboard/hospital/#hosp-recipients')
        self.assertFalse(Recipient.objects.filter(pk=recipient.pk).exists())
        
        recipient2 = Recipient.objects.create(
            full_name="Alice Patient",
            age=30,
            gender="female",
            blood_group="O+",
            organ_needed="Liver",
            hospital=self.hospital,
            doctor_assigned="Dr. Wilson"
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin_delete_recipient', args=[recipient2.pk]))
        self.assertRedirects(response, '/dashboard/admin/#admin-recipients')
        self.assertFalse(Recipient.objects.filter(pk=recipient2.pk).exists())



