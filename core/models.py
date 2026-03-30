from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_donor = models.BooleanField(default=False)
    is_hospital = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # The built-in is_superuser identifies the admin

class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    blood_group = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hospital_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    blockchain_address = models.CharField(max_length=42, help_text="Ethereum Address", blank=True, null=True)

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organ_type} ({self.status})"
