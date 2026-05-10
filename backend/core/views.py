from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from django.urls import reverse_lazy
import json

class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('admin_dashboard')
        elif getattr(user, 'is_hospital', False):
            return reverse_lazy('hospital_dashboard')
        elif getattr(user, 'is_donor', False):
            return reverse_lazy('donor_dashboard')
        return super().get_success_url()

from .forms import (
    DonorRegistrationForm, HospitalRegistrationForm, OrganRegistrationForm,
    ProfilePictureForm, AdminHospitalManagementForm, AdminProfileUpdateForm,
    ThemeSettingsForm, FeedbackForm, DeathCertificateForm, DonorProfileEditForm,
    HospitalProfileEditForm, DonorPledgeForm, ORGAN_TYPE_CHOICES, BLOOD_GROUP_CHOICES,
    RecipientForm
)
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate, Recipient, BlockchainTransaction, Transplant, AuditLog
from .blockchain.service import register_organ_on_chain, match_organ_on_chain, transplant_organ_on_chain, get_blockchain_status

def home(request):
    return render(request, 'core/home.html')

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('donor_dashboard')
    else:
        form = DonorRegistrationForm()
    return render(request, 'core/register_donor.html', {'form': form})

def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('hospital_dashboard')
    else:
        form = HospitalRegistrationForm()
    return render(request, 'core/register_hospital.html', {'form': form})

@login_required
def donor_dashboard(request):
    if not hasattr(request.user, 'donorprofile'):
        return redirect('home')
    organs = OrganRecord.objects.filter(donor=request.user.donorprofile)
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-submitted_at')
    feedback_form = FeedbackForm()

    if request.method == 'POST' and request.POST.get('form_type') == 'feedback':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            fb = feedback_form.save(commit=False)
            fb.user = request.user
            fb.sentiment = _analyze_sentiment(fb.message, fb.rating)
            fb.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('donor_dashboard')

    password_changed = False

    if request.method == 'POST' and request.POST.get('form_type') == 'edit_profile':
        profile_form = DonorProfileEditForm(
            request.POST,
            request.FILES,
            instance=request.user.donorprofile,
            user=request.user,
        )
        if profile_form.is_valid():
            password_changed = bool(profile_form.cleaned_data.get('new_password'))
            profile_form.save()
            if password_changed:
                update_session_auth_hash(request, request.user)
            messages.success(request, "Profile updated successfully!")
            return redirect('donor_dashboard')
        messages.error(request, "Please correct the highlighted profile details.")

    if request.method == 'POST' and request.POST.get('form_type') == 'pledge':
        pledge_form = DonorPledgeForm(request.POST)
        if pledge_form.is_valid():
            pledge = pledge_form.save(commit=False)
            pledge.donor = request.user.donorprofile
            pledge.status = 'Pledged'
            # We don't have a hospital yet, hospital will register it later
            pledge.save()
            messages.success(request, f"You have successfully pledged your {pledge.organ_type}! A hospital will contact you for verification.")
            return redirect('donor_dashboard')

    blockchain_transactions = BlockchainTransaction.objects.filter(donor=request.user.donorprofile).order_by('-timestamp')

    profile_edit_form = DonorProfileEditForm(instance=request.user.donorprofile, user=request.user)
    return render(request, 'core/donor_dashboard.html', {
        'organs': organs,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'theme_form': ThemeSettingsForm(instance=request.user),
        'feedback_form': feedback_form,
        'feedbacks': feedbacks,
        'blockchain_transactions': blockchain_transactions,
        'profile_edit_form': profile_edit_form,
        'pledge_form': DonorPledgeForm(),
    })


@login_required
def hospital_dashboard(request):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')
    hospital = request.user.hospitalprofile
    hospital_profile_form = HospitalProfileEditForm(instance=hospital, user=request.user)

    if request.method == 'POST' and request.POST.get('form_type') == 'update_details':
        hospital_profile_form = HospitalProfileEditForm(
            request.POST,
            request.FILES,
            instance=hospital,
            user=request.user,
        )
        if hospital_profile_form.is_valid():
            password_changed = bool(hospital_profile_form.cleaned_data.get('new_password'))
            hospital_profile_form.save()
            if password_changed:
                update_session_auth_hash(request, request.user)
            messages.success(request, "Hospital profile updated successfully.")
            return redirect('hospital_dashboard')
        messages.error(request, "Please correct the highlighted hospital profile details.")

    registered_organs = hospital.registered_organs.all()
    received_organs = hospital.received_organs.all()
    available_organs = OrganRecord.objects.filter(status='Available').exclude(registered_by=hospital)

    # All donors registered in the system
    all_donors = DonorProfile.objects.select_related('user').all()

    recipients = hospital.recipients.all()
    recipient_form = RecipientForm()

    if request.method == 'POST' and request.POST.get('form_type') == 'add_recipient':
        recipient_form = RecipientForm(request.POST)
        if recipient_form.is_valid():
            recipient = recipient_form.save(commit=False)
            recipient.hospital = hospital
            recipient.save()
            messages.success(request, "Recipient added successfully.")
            return redirect('hospital_dashboard')

    # Search functionality
    search_organ = request.GET.get('search_organ', '').strip()
    search_location = request.GET.get('search_location', '').strip()

    if search_organ:
        available_organs = available_organs.filter(organ_type__icontains=search_organ)
    if search_location:
        available_organs = available_organs.filter(
            registered_by__city__icontains=search_location
        ) | available_organs.filter(
            registered_by__state__icontains=search_location
        )

    transplants = hospital.transplants_managed.all().order_by('-created_at')
    blockchain_transactions = BlockchainTransaction.objects.filter(hospital=hospital).order_by('-timestamp')

    return render(request, 'core/hospital_dashboard.html', {
        'registered_organs': registered_organs,
        'received_organs': received_organs,
        'available_organs': available_organs,
        'all_donors': all_donors,
        'recipients': recipients,
        'transplants': transplants,
        'blockchain_transactions': blockchain_transactions,
        'recipient_form': recipient_form,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'theme_form': ThemeSettingsForm(instance=request.user),
        'hospital_profile_form': hospital_profile_form,
        'search_organ': search_organ,
        'search_location': search_location,
    })

@login_required
def register_organ(request):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')
        
    donor_id = request.GET.get('donor_id')
    initial_data = {}
    if donor_id:
        initial_data['donor'] = donor_id

    if request.method == 'POST':
        form = OrganRegistrationForm(request.POST)
        if form.is_valid():
            organ = form.save(commit=False)

            
            # Automatically pull the blood group from the Donor's fixed profile
            organ.blood_group = organ.donor.blood_group
            
            # Store the approval log on Ganache, then cache the receipt in MySQL.
            try:
                hospital = request.user.hospitalprofile
                doctor_name = request.user.get_full_name() or request.user.username
                blockchain_receipt = register_organ_on_chain(
                    donor_id=organ.donor.user.id,
                    donor_name=organ.donor.user.get_full_name() or organ.donor.user.username,
                    organ_type=organ.organ_type,
                    hospital_name=hospital.hospital_name,
                    doctor_name=doctor_name,
                    sender_address=hospital.blockchain_wallet_address,
                )
                if blockchain_receipt is not None:
                    if isinstance(blockchain_receipt, dict):
                        organ.blockchain_id = blockchain_receipt['blockchain_id']
                        organ.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                        organ.blockchain_block_number = blockchain_receipt['block_number']
                        organ.blockchain_timestamp = blockchain_receipt['timestamp']
                    else:
                        organ.blockchain_id = blockchain_receipt
                    organ.registered_by = request.user.hospitalprofile
                    organ.save()
                    messages.success(request, "Organ donation approved and saved to blockchain.")
                    return redirect('hospital_dashboard')
                else:
                    form.add_error(None, "Blockchain transaction failed to return an ID.")
            except Exception as e:
                form.add_error(None, _format_blockchain_error(e))
    else:
        form = OrganRegistrationForm(initial=initial_data)
    
    return render(request, 'core/register_organ.html', {'form': form})


def _format_blockchain_error(error):
    error_text = str(error)
    connection_markers = [
        "HTTPConnectionPool",
        "NewConnectionError",
        "WinError 10061",
        "Failed to establish a new connection",
        "Blockchain not connected",
    ]

    if any(marker in error_text for marker in connection_markers):
        return (
            "Blockchain service is not running. Start Ganache or your local "
            "blockchain RPC at http://127.0.0.1:7545, then try registering "
            "the organ again."
        )

    return f"Blockchain error: {error_text}"

def _analyze_sentiment(message, rating):
    """Simple rule-based sentiment analysis based on rating and keywords."""
    positive_words = ['great', 'excellent', 'good', 'wonderful', 'amazing', 'helpful', 'best', 'love', 'happy', 'satisfied', 'outstanding']
    negative_words = ['bad', 'poor', 'terrible', 'worst', 'hate', 'awful', 'disappointing', 'horrible', 'problem', 'issue', 'frustrated']
    
    message_lower = message.lower()
    pos_count = sum(1 for w in positive_words if w in message_lower)
    neg_count = sum(1 for w in negative_words if w in message_lower)
    
    if rating >= 4 or (pos_count > neg_count):
        return 'positive'
    elif rating <= 2 or (neg_count > pos_count):
        return 'negative'
    else:
        return 'neutral'

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    hospital_form = AdminHospitalManagementForm()
    cert_form = DeathCertificateForm()

    if request.method == 'POST':
        admin_action = request.POST.get('admin_action')

        if admin_action == 'add_hospital':
            hospital_form = AdminHospitalManagementForm(request.POST, request.FILES)
            if hospital_form.is_valid():
                hospital_user = hospital_form.save()
                messages.success(request, f"Hospital {hospital_user.hospitalprofile.hospital_name} added successfully.")
                return redirect('admin_dashboard')
            messages.error(request, "Unable to add hospital. Please correct the highlighted details.")

        elif admin_action == 'update_user':
            user_id = request.POST.get('user_id')
            if user_id:
                _update_user_from_admin_post(request, user_id)
            return redirect('admin_dashboard')

        elif admin_action == 'approve_user':
            user_id = request.POST.get('user_id')
            if user_id:
                acc = get_object_or_404(User, pk=user_id)
                acc.is_approved = True
                acc.is_active = True
                acc.save()
                messages.success(request, f"User {acc.username} approved.")
            return redirect('admin_dashboard')

        elif admin_action == 'reject_user':
            user_id = request.POST.get('user_id')
            if user_id:
                acc = get_object_or_404(User, pk=user_id)
                acc.is_active = False
                acc.save()
                messages.warning(request, f"User {acc.username} rejected/deactivated.")
            return redirect('admin_dashboard')

        elif admin_action == 'update_admin_profile':
            admin_form = AdminProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if admin_form.is_valid():
                password_changed = bool(admin_form.cleaned_data.get('new_password'))
                admin_form.save()
                if password_changed:
                    update_session_auth_hash(request, request.user)
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('admin_dashboard')
            messages.error(request, "Error updating profile. Please check the details.")

        elif admin_action == 'update_organ_status':
            organ_id = request.POST.get('organ_id')
            if organ_id:
                _update_organ_status_from_admin_post(request, organ_id)
            return redirect('admin_dashboard')

        elif admin_action == 'issue_death_certificate':
            cert_form = DeathCertificateForm(request.POST)
            if cert_form.is_valid():
                cert = cert_form.save(commit=False)
                cert.issued_by = HospitalProfile.objects.first()  # admin issues on behalf
                # Mark donor as deceased
                cert.donor.is_deceased = True
                cert.donor.save()
                cert.save()
                messages.success(request, f"Death certificate #{cert.certificate_number} issued.")
                return redirect('admin_dashboard')
            messages.error(request, "Error issuing certificate. Please check the details.")

        elif admin_action == 'delete_feedback':
            fb_id = request.POST.get('feedback_id')
            if fb_id:
                fb = get_object_or_404(Feedback, pk=fb_id)
                fb.delete()
                messages.success(request, "Feedback deleted.")
            return redirect('admin_dashboard')

    organs = OrganRecord.objects.all().order_by('-created_at')
    hospitals = HospitalProfile.objects.all()
    donors = DonorProfile.objects.select_related('user').all().order_by('user__username')
    users = User.objects.all().order_by('username')
    # User Management section: only show regular users (not hospital, not donor, not admin)
    plain_users = User.objects.filter(
        is_superuser=False, is_hospital=False, is_donor=False
    ).order_by('username')
    pending_users = User.objects.filter(is_approved=False).order_by('date_joined')
    feedbacks = Feedback.objects.select_related('user').all().order_by('-submitted_at')
    certificates = DeathCertificate.objects.select_related('donor', 'issued_by').all().order_by('-issued_at')
    
    transplants = Transplant.objects.all().order_by('-created_at')
    recipients = Recipient.objects.select_related('hospital').all().order_by('-created_at')
    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    blockchain_txs = BlockchainTransaction.objects.all().order_by('-timestamp')

    donors_count = DonorProfile.objects.count()
    hospitals_count = hospitals.count()
    organs_count = organs.count()
    matches_count = organs.filter(status='Matched').count()
    transplants_count = organs.filter(status='Transplanted').count()
    available_count = organs.filter(status='Available').count()
    admins_count = users.filter(is_superuser=True).count()
    other_users_count = plain_users.count()
    blockchain_tx_count = blockchain_txs.count()
    recipients_count = Recipient.objects.count()
    organ_type_counts = list(
        organs.values('organ_type')
        .annotate(total=Count('id'))
        .order_by('organ_type')
    )

    # Sentiment analysis data
    sentiment_data = {
        'positive': feedbacks.filter(sentiment='positive').count(),
        'negative': feedbacks.filter(sentiment='negative').count(),
        'neutral': feedbacks.filter(sentiment='neutral').count(),
    }
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0

    # Monthly feedback counts for chart (last 6 months)
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    monthly_labels = []
    monthly_counts = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        count = feedbacks.filter(submitted_at__gte=month_start, submitted_at__lt=month_end).count()
        monthly_labels.append(month_start.strftime('%b %Y'))
        monthly_counts.append(count)

    context = {
        'organs': organs,
        'hospitals': hospitals,
        'donors': donors,
        'users': users,
        'plain_users': plain_users,
        'pending_users': pending_users,
        'feedbacks': feedbacks,
        'certificates': certificates,
        'transplants': transplants,
        'recipients': recipients,
        'audit_logs': audit_logs,
        'blockchain_txs': blockchain_txs,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'theme_form': ThemeSettingsForm(instance=request.user),
        'hospital_management_form': hospital_form,
        'admin_profile_form': AdminProfileUpdateForm(instance=request.user),
        'cert_form': cert_form,
        'stats': {
            'donors': donors_count,
            'recipients': recipients_count,
            'hospitals': hospitals_count,
            'admins': admins_count,
            'other_users': other_users_count,
            'organs': organs_count,
            'matches': matches_count,
            'transplants': transplants_count,
            'available': available_count,
            'pending': pending_users.count(),
            'feedbacks': feedbacks.count(),
            'blockchain_txs': blockchain_tx_count,
        },
        'chart_data': {
            'available': available_count,
            'matched': matches_count,
            'transplanted': transplants_count,
        },
        'user_category_data': [
            {'label': 'Admins', 'total': admins_count},
            {'label': 'Donors', 'total': donors_count},
            {'label': 'Hospitals', 'total': hospitals_count},
            {'label': 'Recipients', 'total': recipients_count},
        ],
        'organ_type_counts': organ_type_counts,
        'sentiment_data': sentiment_data,
        'avg_rating': round(avg_rating, 1),
        'monthly_labels': monthly_labels,
        'monthly_counts': monthly_counts,
        'blockchain_status': get_blockchain_status(),
    }
    return render(request, 'core/admin_dashboard.html', context)


def _update_user_from_admin_post(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    role = request.POST.get('role', 'user')
    is_active = request.POST.get('status') == 'active'
    hospital_name = request.POST.get('hospital_name', '').strip()

    if not username:
        messages.error(request, "Username cannot be empty.")
        return

    if User.objects.filter(username=username).exclude(pk=account.pk).exists():
        messages.error(request, f"Username {username} is already in use.")
        return

    if account == request.user and not is_active:
        messages.error(request, "You cannot block your own admin account.")
        return

    if role == 'hospital' and not hasattr(account, 'hospitalprofile'):
        messages.error(request, "Only users with a hospital profile can be changed to Hospital role.")
        return

    if role == 'donor' and not hasattr(account, 'donorprofile'):
        messages.error(request, "Only users with a donor profile can be changed to Donor role.")
        return

    account.username = username
    account.email = email
    account.first_name = first_name
    account.last_name = last_name
    account.is_active = is_active
    account.is_superuser = role == 'admin'
    account.is_staff = role == 'admin'
    account.is_hospital = role == 'hospital'
    account.is_donor = role == 'donor'
    
    if 'profile_picture' in request.FILES:
        account.profile_picture = request.FILES['profile_picture']
        
    account.save()

    if hasattr(account, 'hospitalprofile') and hospital_name:
        hospital_profile = account.hospitalprofile
        hospital_profile.hospital_name = hospital_name
        update_fields = ['hospital_name']
        if 'background_image' in request.FILES:
            hospital_profile.background_image = request.FILES['background_image']
            update_fields.append('background_image')
        hospital_profile.save(update_fields=update_fields)

    messages.success(request, f"Updated account {account.username}.")


def _update_organ_status_from_admin_post(request, organ_id):
    organ = get_object_or_404(OrganRecord, pk=organ_id)
    status = request.POST.get('status')
    if status not in {'Available', 'Matched', 'Transplanted'}:
        messages.error(request, "Invalid organ status selected.")
        return

    organ.status = status
    if status == 'Available':
        organ.recipient_hospital = None
    organ.save(update_fields=['status', 'recipient_hospital'])

    messages.success(request, f"Organ #{organ.blockchain_id} status changed to {status}.")


@user_passes_test(lambda u: u.is_superuser)
def delete_hospital(request, hospital_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    hospital = get_object_or_404(HospitalProfile, pk=hospital_id)
    hospital_name = hospital.hospital_name
    hospital.user.delete()
    messages.success(request, f"Hospital {hospital_name} deleted successfully.")
    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def admin_update_user(request, user_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    account = get_object_or_404(User, pk=user_id)
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    role = request.POST.get('role', 'user')
    is_active = request.POST.get('status') == 'active'
    hospital_name = request.POST.get('hospital_name', '').strip()

    if not username:
        messages.error(request, "Username cannot be empty.")
        return redirect('admin_dashboard')

    if User.objects.filter(username=username).exclude(pk=account.pk).exists():
        messages.error(request, f"Username {username} is already in use.")
        return redirect('admin_dashboard')

    if account == request.user and not is_active:
        messages.error(request, "You cannot block your own admin account.")
        return redirect('admin_dashboard')

    if role == 'hospital' and not hasattr(account, 'hospitalprofile'):
        messages.error(request, "Only users with a hospital profile can be changed to Hospital role.")
        return redirect('admin_dashboard')

    if role == 'donor' and not hasattr(account, 'donorprofile'):
        messages.error(request, "Only users with a donor profile can be changed to Donor role.")
        return redirect('admin_dashboard')

    account.username = username
    account.email = email
    account.first_name = first_name
    account.last_name = last_name
    account.is_active = is_active
    account.is_superuser = role == 'admin'
    account.is_staff = role == 'admin'
    account.is_hospital = role == 'hospital'
    account.is_donor = role == 'donor'
    
    if 'profile_picture' in request.FILES:
        account.profile_picture = request.FILES['profile_picture']
        
    account.save()

    if hasattr(account, 'hospitalprofile') and hospital_name:
        hospital_profile = account.hospitalprofile
        hospital_profile.hospital_name = hospital_name
        update_fields = ['hospital_name']
        if 'background_image' in request.FILES:
            hospital_profile.background_image = request.FILES['background_image']
            update_fields.append('background_image')
        hospital_profile.save(update_fields=update_fields)

    messages.success(request, f"Updated account {account.username}.")
    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def admin_update_organ_status(request, organ_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    organ = get_object_or_404(OrganRecord, pk=organ_id)
    status = request.POST.get('status')
    if status not in {'Available', 'Matched', 'Transplanted'}:
        messages.error(request, "Invalid organ status selected.")
        return redirect('admin_dashboard')

    organ.status = status
    if status == 'Available':
        organ.recipient_hospital = None
    organ.save(update_fields=['status', 'recipient_hospital'])

    messages.success(request, f"Organ #{organ.blockchain_id} status changed to {status}.")
    return redirect('admin_dashboard')


@login_required
def hospital_update_organ_status(request, organ_id):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')

    if request.method != 'POST':
        return redirect('hospital_dashboard')

    hospital = request.user.hospitalprofile
    organ = get_object_or_404(OrganRecord, pk=organ_id)
    status = request.POST.get('status')

    if status not in {'Available', 'Matched', 'Transplanted'}:
        messages.error(request, "Invalid organ status selected.")
        return redirect('hospital_dashboard')

    owns_record = organ.registered_by == hospital
    receives_record = organ.recipient_hospital == hospital

    if not (owns_record or receives_record):
        messages.error(request, "You can update only organs connected to your hospital.")
        return redirect('hospital_dashboard')

    if owns_record:
        organ_type = request.POST.get('organ_type', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        valid_organs = {choice[0] for choice in ORGAN_TYPE_CHOICES}
        valid_blood_groups = {choice[0] for choice in BLOOD_GROUP_CHOICES}

        if organ_type and organ_type not in valid_organs:
            messages.error(request, "Invalid organ type selected.")
            return redirect('hospital_dashboard')

        if blood_group and blood_group not in valid_blood_groups:
            messages.error(request, "Invalid blood group selected.")
            return redirect('hospital_dashboard')

        if organ_type:
            organ.organ_type = organ_type
        if blood_group:
            organ.blood_group = blood_group

    if receives_record and not owns_record and status == 'Available':
        messages.error(request, "Received organs cannot be returned to Available from this dashboard.")
        return redirect('hospital_dashboard')

    if status == 'Transplanted' and organ.status != 'Transplanted':
        if hospital.blockchain_wallet_address:
            try:
                blockchain_receipt = transplant_organ_on_chain(organ.blockchain_id, hospital.blockchain_wallet_address)
                organ.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                organ.blockchain_block_number = blockchain_receipt['block_number']
            except Exception as e:
                messages.error(request, _format_blockchain_error(e))
                return redirect('hospital_dashboard')
        else:
            messages.warning(request, "Transplant status saved in database. Link a Ganache wallet to create the blockchain audit log.")

    organ.status = status
    if owns_record and status == 'Available':
        organ.recipient_hospital = None
    organ.save(update_fields=['organ_type', 'blood_group', 'status', 'recipient_hospital', 'blockchain_tx_hash', 'blockchain_block_number'])

    messages.success(request, f"Organ #{organ.blockchain_id} details updated.")
    return redirect('hospital_dashboard')


@login_required
def update_profile_picture(request):
    if request.method != 'POST':
        return redirect('home')

    form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile picture updated successfully.")
    else:
        messages.error(request, "Please upload a valid image file for the profile picture.")

    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'hospitalprofile'):
        return redirect('hospital_dashboard')
    if hasattr(request.user, 'donorprofile'):
        return redirect('donor_dashboard')
    return redirect('home')

@login_required
def match_organ(request, organ_id):
    if not (request.user.is_superuser or hasattr(request.user, 'hospitalprofile')):
        return redirect('home')

    if request.method == 'POST':
        organ = get_object_or_404(OrganRecord, id=organ_id)
        if organ.status == 'Available':
            recipient = None

            if hasattr(request.user, 'hospitalprofile'):
                recipient = request.user.hospitalprofile
            elif request.user.is_superuser:
                hospital_id = request.POST.get('hospital_id')
                if hospital_id:
                    recipient = get_object_or_404(HospitalProfile, pk=hospital_id)
                else:
                    recipient = HospitalProfile.objects.exclude(user=organ.registered_by.user).first()

            if recipient:
                if recipient == organ.registered_by:
                    messages.error(request, "Originating hospital cannot match its own organ.")
                    redirect_name = 'hospital_dashboard' if hasattr(request.user, 'hospitalprofile') else 'admin_dashboard'
                    return redirect(redirect_name)
                try:
                    blockchain_receipt = match_organ_on_chain(organ.blockchain_id, recipient.hospital_name, recipient.blockchain_wallet_address)
                    receipt_succeeded = (
                        blockchain_receipt is True
                        or getattr(blockchain_receipt, 'status', None) == 1
                        or (isinstance(blockchain_receipt, dict) and blockchain_receipt.get('status') == 1)
                    )
                    if blockchain_receipt and receipt_succeeded:
                        organ.status = 'Matched'
                        organ.recipient_hospital = recipient
                        if isinstance(blockchain_receipt, dict):
                            organ.blockchain_tx_hash = blockchain_receipt.get('transaction_hash')
                            organ.blockchain_block_number = blockchain_receipt.get('block_number')
                        organ.save()
                        if organ.blockchain_tx_hash:
                            messages.success(request, f"Organ #{organ.blockchain_id} successfully matched to {recipient.hospital_name} on the blockchain. TX: {organ.blockchain_tx_hash[:10]}...")
                        else:
                            messages.success(request, f"Organ #{organ.blockchain_id} successfully matched to {recipient.hospital_name}.")
                    else:
                        messages.error(request, "Blockchain smart contract matching failed.")
                except Exception as e:
                    messages.error(request, _format_blockchain_error(e))
            else:
                messages.error(request, "No eligible recipient hospitals found in the network.")
        redirect_name = 'hospital_dashboard' if hasattr(request.user, 'hospitalprofile') else 'admin_dashboard'
        return redirect(redirect_name)
    return redirect('hospital_dashboard' if hasattr(request.user, 'hospitalprofile') else 'admin_dashboard')

@login_required
def update_theme(request):
    if request.method == 'POST':
        form = ThemeSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Theme settings updated successfully.")
        else:
            messages.error(request, "Error updating theme settings.")
    
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'hospitalprofile'):
        return redirect('hospital_dashboard')
    if hasattr(request.user, 'donorprofile'):
        return redirect('donor_dashboard')
    return redirect('home')

@login_required
def submit_feedback(request):
    """Handle feedback submission from any portal."""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            fb.sentiment = _analyze_sentiment(fb.message, fb.rating)
            fb.save()
            messages.success(request, "Thank you for your feedback!")
        else:
            messages.error(request, "Please correct the errors in your feedback.")

    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'hospitalprofile'):
        return redirect('hospital_dashboard')
    return redirect('donor_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def issue_death_certificate(request):
    if request.method == 'POST':
        form = DeathCertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            # Get the hospital that registered most organs, or first one
            hospital = HospitalProfile.objects.first()
            if hospital:
                cert.issued_by = hospital
            cert.donor.is_deceased = True
            cert.donor.save()
            cert.save()
            messages.success(request, f"Death certificate #{cert.certificate_number} issued successfully.")
        else:
            messages.error(request, "Error issuing certificate.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            messages.error(request, "Cannot delete your own account.")
        else:
            username = user.username
            user.delete()
            messages.success(request, f"User {username} deleted.")
    return redirect('admin_dashboard')
