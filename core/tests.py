from unittest.mock import patch
import tempfile

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings

from .forms import BLOOD_GROUP_CHOICES, ORGAN_TYPE_CHOICES, OrganRegistrationForm
from .models import DonorProfile, HospitalProfile, OrganRecord, User


class FormChoicesTests(TestCase):
    def test_blood_group_labels_include_positive_negative_text(self):
        labels = dict(BLOOD_GROUP_CHOICES)
        self.assertEqual(labels['A+'], 'A+ (Positive)')
        self.assertEqual(labels['O-'], 'O- (Negative)')

    def test_organ_registration_form_includes_common_donatable_organs(self):
        organ_choices = dict(OrganRegistrationForm().fields['organ_type'].choices)
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
            registered_by=self.source_hospital,
        )

    @patch('core.views.match_organ_on_chain', return_value=True)
    def test_hospital_can_match_available_organ_for_itself(self, _mock_match):
        self.client.force_login(self.ace_user)

        response = self.client.post(reverse('match_organ', args=[self.organ.id]))

        self.assertRedirects(response, reverse('hospital_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.status, 'Matched')
        self.assertEqual(self.organ.recipient_hospital, self.ace_hospital)

    @patch('core.views.match_organ_on_chain', return_value=True)
    def test_admin_match_uses_selected_hospital_id(self, _mock_match):
        admin = User.objects.create_superuser(username='admin', password=self.password, email='admin@example.com')
        self.client.force_login(admin)

        response = self.client.post(
            reverse('match_organ', args=[self.organ.id]),
            {'hospital_id': self.third_hospital.pk},
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.organ.refresh_from_db()
        self.assertEqual(self.organ.recipient_hospital, self.third_hospital)


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
