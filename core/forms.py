from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonorProfile, HospitalProfile, OrganRecord

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+ (Positive)'),
    ('A-', 'A- (Negative)'),
    ('B+', 'B+ (Positive)'),
    ('B-', 'B- (Negative)'),
    ('O+', 'O+ (Positive)'),
    ('O-', 'O- (Negative)'),
    ('AB+', 'AB+ (Positive)'),
    ('AB-', 'AB- (Negative)'),
]

ORGAN_TYPE_CHOICES = [
    ('Kidney', 'Kidney'),
    ('Liver', 'Liver'),
    ('Heart', 'Heart'),
    ('Lung', 'Lung'),
    ('Pancreas', 'Pancreas'),
    ('Intestine', 'Intestine'),
    ('Cornea', 'Cornea'),
    ('Bone Marrow', 'Bone Marrow'),
    ('Skin Tissue', 'Skin Tissue'),
]

class DonorRegistrationForm(UserCreationForm):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        user.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            DonorProfile.objects.create(
                user=user,
                blood_group=self.cleaned_data.get('blood_group'),
                contact_number=self.cleaned_data.get('contact_number'),
                address=self.cleaned_data.get('address')
            )
        return user

class HospitalRegistrationForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=100)
    registration_number = forms.CharField(max_length=50)
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_hospital = True
        user.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            HospitalProfile.objects.create(
                user=user,
                hospital_name=self.cleaned_data.get('hospital_name'),
                registration_number=self.cleaned_data.get('registration_number'),
                contact_number=self.cleaned_data.get('contact_number'),
                address=self.cleaned_data.get('address')
            )
        return user

class OrganRegistrationForm(forms.ModelForm):
    organ_type = forms.ChoiceField(
        choices=ORGAN_TYPE_CHOICES,
        label="Organ Type",
        help_text="Select the organ or tissue being donated.",
    )

    class Meta:
        model = OrganRecord
        fields = ['donor', 'organ_type']
        widgets = {
            'donor': forms.Select(),
            'organ_type': forms.Select(),
        }
        labels = {
            'donor': 'Donor',
        }


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']


class AdminHospitalManagementForm(forms.Form):
    hospital_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    registration_number = forms.CharField(max_length=50)
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean_registration_number(self):
        registration_number = self.cleaned_data['registration_number']
        if HospitalProfile.objects.filter(registration_number=registration_number).exists():
            raise forms.ValidationError("This registration number already exists.")
        return registration_number

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email', ''),
            password=self.cleaned_data['password'],
        )
        user.is_hospital = True
        user.profile_picture = self.cleaned_data.get('profile_picture')
        user.save()

        HospitalProfile.objects.create(
            user=user,
            hospital_name=self.cleaned_data['hospital_name'],
            registration_number=self.cleaned_data['registration_number'],
            contact_number=self.cleaned_data['contact_number'],
            address=self.cleaned_data['address'],
        )
        return user
