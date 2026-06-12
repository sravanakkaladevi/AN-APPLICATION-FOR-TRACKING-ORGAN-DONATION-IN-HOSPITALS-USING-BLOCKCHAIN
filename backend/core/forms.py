from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate, Recipient

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

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
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
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    age = forms.IntegerField(required=True)
    medical_history = forms.CharField(widget=forms.Textarea, required=False)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(required=False)
    background_image = forms.ImageField(required=False)
    policy_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': "You must accept the policy before creating an account."},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_donor = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            DonorProfile.objects.create(
                user=user,
                age=self.cleaned_data.get('age'),
                medical_history=self.cleaned_data.get('medical_history'),
                blood_group=self.cleaned_data.get('blood_group'),
                gender=self.cleaned_data.get('gender'),
                contact_number=self.cleaned_data.get('contact_number'),
                address=self.cleaned_data.get('address'),
                city=self.cleaned_data.get('city', ''),
                state=self.cleaned_data.get('state', ''),
            )
        return user

class HospitalRegistrationForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=100)
    registration_number = forms.CharField(max_length=50)
    contact_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(required=False)
    policy_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': "You must accept the policy before creating an account."},
    )

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
                address=self.cleaned_data.get('address'),
                city=self.cleaned_data.get('city', ''),
                state=self.cleaned_data.get('state', ''),
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
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
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
            city=self.cleaned_data.get('city', ''),
            state=self.cleaned_data.get('state', ''),
            background_image=self.cleaned_data.get('background_image'),
        )
        return user


class AdminProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    background_image = forms.ImageField(required=False, label="Dashboard Background")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")
    remove_profile_picture = forms.BooleanField(required=False, label="Remove Profile Picture")
    remove_background_image = forms.BooleanField(required=False, label="Remove Dashboard Background")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture', 'background_image']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        if self.cleaned_data.get('remove_profile_picture'):
            user.profile_picture = None
            
        if self.cleaned_data.get('remove_background_image'):
            user.background_image = None

        if commit:
            user.save()
        return user

class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['theme', 'custom_theme_color']
        widgets = {
            'custom_theme_color': forms.TextInput(attrs={'type': 'color'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message', 'rating']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i>1 else ""}') for i in range(1, 6)]),
        }

class DeathCertificateForm(forms.ModelForm):
    class Meta:
        model = DeathCertificate
        fields = ['donor', 'certificate_number', 'date_of_death', 'cause_of_death', 'notes']
        widgets = {
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
            'cause_of_death': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DonorProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    profile_picture = forms.ImageField(required=False, label="Profile Picture")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = DonorProfile
        fields = ['blood_group', 'contact_number', 'address', 'city', 'state', 'age', 'medical_history']
        widgets = {
            'blood_group': forms.Select(choices=BLOOD_GROUP_CHOICES),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if self.cleaned_data.get('profile_picture'):
                self.user.profile_picture = self.cleaned_data['profile_picture']
            if self.cleaned_data.get('new_password'):
                self.user.set_password(self.cleaned_data['new_password'])
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class HospitalProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    profile_picture = forms.ImageField(required=False, label="Hospital Logo")
    background_image = forms.ImageField(required=False, label="Hospital Background")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = HospitalProfile
        fields = ['hospital_name', 'contact_email', 'contact_number', 'address', 'city', 'state', 'background_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        existing = User.objects.filter(username=username)
        if self.user:
            existing = existing.exclude(pk=self.user.pk)
        if existing.exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data.get('email', '')
            if self.cleaned_data.get('profile_picture'):
                self.user.profile_picture = self.cleaned_data['profile_picture']
            if self.cleaned_data.get('new_password'):
                self.user.set_password(self.cleaned_data['new_password'])
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile

class DonorPledgeForm(forms.ModelForm):
    class Meta:
        model = OrganRecord
        fields = ['organ_type']
        widgets = {
            'organ_type': forms.Select(choices=ORGAN_TYPE_CHOICES),
        }

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['full_name', 'age', 'gender', 'blood_group', 'organ_needed', 'doctor_assigned', 'emergency_priority', 'medical_notes']
        widgets = {
            'gender': forms.Select(choices=GENDER_CHOICES),
            'blood_group': forms.Select(choices=BLOOD_GROUP_CHOICES),
            'organ_needed': forms.Select(choices=ORGAN_TYPE_CHOICES),
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
        }
