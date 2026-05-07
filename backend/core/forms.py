from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate

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
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
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
        user.is_donor = True
        user.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            DonorProfile.objects.create(
                user=user,
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
        )
        return user


class AdminProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']

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

    class Meta:
        model = DonorProfile
        fields = ['blood_group', 'contact_number', 'address', 'city', 'state']
        widgets = {
            'blood_group': forms.Select(choices=BLOOD_GROUP_CHOICES),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
