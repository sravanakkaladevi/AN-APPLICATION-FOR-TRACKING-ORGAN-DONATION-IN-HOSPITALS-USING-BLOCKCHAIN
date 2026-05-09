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
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    custom_theme_color = models.CharField(max_length=7, default='#1e1e1e')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)  # False = pending approval
    # The built-in is_superuser identifies the admin

class DonorProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    blood_group = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)
    is_deceased = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    blockchain_wallet_address = models.CharField(max_length=42, help_text="Ethereum Address from Ganache", blank=True, null=True)

    def __str__(self):
        return self.hospital_name

class OrganRecord(models.Model):
    # This acts as a cache for the blockchain data for quick database queries
    blockchain_id = models.IntegerField(unique=True, help_text="ID from Blockchain")
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    organ_type = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=5)
    status_choices = [
        ('Available', 'Available'),
        ('Matched', 'Matched'),
        ('Transplanted', 'Transplanted')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Available')
    registered_by = models.ForeignKey(HospitalProfile, related_name="registered_organs", on_delete=models.CASCADE)
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
