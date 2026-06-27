from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_donor = models.BooleanField(default=False)
    is_hospital = models.BooleanField(default=False)
    THEME_CHOICES = [
        ('white', 'White'),
        ('dark', 'Dark'),
        ('black_white', 'Black White'),
        ('custom', 'Custom'),
    ]
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='white')
    custom_theme_color = models.CharField(max_length=7, default='#1e1e1e')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    background_image = models.ImageField(upload_to='profile_backgrounds/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)  # False = pending approval
    # The built-in is_superuser identifies the admin

class DonorProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Testing', 'Under Testing'),
        ('Accepted', 'Accepted'),
        ('Approved', 'Approved'),
        ('Eligible', 'Eligible'),
        ('Not Eligible', 'Not Eligible'),
        ('Organ Failure', 'Organ Failure'),
        ('Rejected', 'Rejected'),
        ('Deceased', 'Deceased'),
        ('Death but Eligible Transplant', 'Death but Eligible Transplant'),
        ('Death but Ineligible Transplant', 'Death but Ineligible Transplant'),
    ]
    approval_status = models.CharField(max_length=50, choices=APPROVAL_CHOICES, default='Pending')
    assigned_hospital = models.ForeignKey('HospitalProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donors')

    blood_group = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    pledged_organ = models.CharField(max_length=50, blank=True, null=True)
    is_deceased = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hospitalprofile')
    hospital_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    background_image = models.ImageField(upload_to='hospital_backgrounds/', blank=True, null=True)
    blockchain_wallet_address = models.CharField(max_length=42, help_text="Ethereum Address from Ganache", blank=True, null=True)

    def __str__(self):
        return self.hospital_name

class OrganRecord(models.Model):
    # This acts as a cache for the blockchain data for quick database queries
    blockchain_id = models.IntegerField(unique=True, null=True, blank=True, help_text="ID from Blockchain")
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    organ_type = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=5)
    status_choices = [
        ('Pending', 'Pending'),
        ('Under Testing', 'Under Testing'),
        ('Accepted', 'Accepted'),
        ('Approved', 'Approved'),
        ('Eligible', 'Eligible'),
        ('Not Eligible', 'Not Eligible'),
        ('Organ Failure', 'Organ Failure'),
        ('Rejected', 'Rejected'),
        ('Deceased', 'Deceased'),
        ('Death but Eligible Transplant', 'Death but Eligible Transplant'),
        ('Death but Ineligible Transplant', 'Death but Ineligible Transplant'),
        ('Admin Approved', 'Admin Approved'),
        ('Registered', 'Registered'),
        ('Under Review', 'Under Review'),
        ('Organ Suitable', 'Organ Suitable'),
        ('Organ Rejected', 'Organ Rejected'),
        ('Submitted to Admin', 'Submitted to Admin'),
        ('Available', 'Available'),
        ('Matched', 'Matched'),
        ('Transplanted', 'Transplanted'),
        ('Case Closed', 'Case Closed'),
        ('Waiting For Blockchain Approval', 'Waiting For Blockchain Approval'),
        ('Blockchain Verified', 'Blockchain Verified'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    medical_remarks = models.TextField(blank=True, null=True)
    registered_by = models.ForeignKey(HospitalProfile, related_name="registered_organs", on_delete=models.CASCADE, null=True, blank=True)
    recipient_hospital = models.ForeignKey(HospitalProfile, related_name="received_organs", null=True, blank=True, on_delete=models.SET_NULL)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True, db_index=True)
    blockchain_block_number = models.PositiveIntegerField(blank=True, null=True)
    blockchain_timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organ_type} ({self.status})"

class DeathCertificate(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='death_certificates')
    issued_by = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='issued_certificates')
    certificate_number = models.CharField(max_length=100, unique=True)
    date_of_death = models.DateField()
    cause_of_death = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Certificate #{self.certificate_number} - {self.donor}"

class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    submitted_at = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=20, blank=True, null=True)  # positive/negative/neutral

    def __str__(self):
        return f"Feedback by {self.user.username} - {self.subject}"

class Recipient(models.Model):

    full_name = models.CharField(max_length=150)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    blood_group = models.CharField(max_length=5)
    organ_needed = models.CharField(max_length=50)
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name="recipients")
    doctor_assigned = models.CharField(max_length=100)
    emergency_priority = models.CharField(max_length=20, choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], default='Medium')
    medical_notes = models.TextField(blank=True, null=True)
    status_choices = [
        ('Requested', 'Requested'),
        ('On Blockchain', 'On Blockchain'),
        ('Matched', 'Matched'),
        ('Approved', 'Approved'),
        ('Organ Transported', 'Organ Transported'),
        ('Transplant Completed', 'Transplant Completed'),
        ('Transplanted', 'Transplanted')
    ]
    status = models.CharField(max_length=30, choices=status_choices, default='Requested')
    blockchain_id = models.CharField(max_length=50, blank=True, null=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.organ_needed}"

class Transplant(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name="donated_organs")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="received_organs", null=True, blank=True)
    organ = models.ForeignKey(OrganRecord, on_delete=models.CASCADE, related_name="transplant")
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name="transplants_managed")
    match_status_choices = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected')
    ]
    match_status = models.CharField(max_length=20, choices=match_status_choices, default='Pending Approval')
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.donor} to {self.recipient} - {self.organ.organ_type}"

class BlockchainTransaction(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.SET_NULL, null=True, blank=True)
    organ_type = models.CharField(max_length=50)
    tx_hash = models.CharField(max_length=66, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.tx_hash

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

class OrganStatusHistory(models.Model):
    organ_record = models.ForeignKey(OrganRecord, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=30, blank=True, null=True)
    new_status = models.CharField(max_length=30)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organ_record.organ_type} ({self.previous_status} -> {self.new_status}) by {self.updated_by} at {self.timestamp}"
