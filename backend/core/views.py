from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.urls import reverse_lazy
from django.db import transaction
import json
import logging
logger = logging.getLogger(__name__)

from django.http import JsonResponse

def ajax_response(request, success=True, redirect_url=None, errors=None, data=None):
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    messages_list = []
    for msg in storage:
        messages_list.append({
            'message': msg.message,
            'tags': msg.tags,
            'level': msg.level,
        })
    response_data = {
        'success': success,
        'messages': messages_list,
    }
    if redirect_url:
        response_data['redirect_url'] = redirect_url
    if errors:
        response_data['errors'] = errors
    if data:
        response_data['data'] = data
    return JsonResponse(response_data)


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
    DonorRegistrationForm, HospitalRegistrationForm,
    ProfilePictureForm, AdminHospitalManagementForm, AdminProfileUpdateForm,
    ThemeSettingsForm, FeedbackForm, DeathCertificateForm, DonorProfileEditForm, RecipientForm,
    HospitalProfileEditForm, ORGAN_TYPE_CHOICES, BLOOD_GROUP_CHOICES,
)
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate, Recipient, BlockchainTransaction, Transplant, AuditLog, OrganStatusHistory
from .blockchain.service import register_organ_on_chain, transplant_organ_on_chain, get_blockchain_status, register_recipient_on_chain, match_organ_on_chain

HOSPITAL_DONOR_STATUSES = {
    'Pending',
    'Under Testing',
    'Accepted',
    'Approved',
    'Eligible',
    'Not Eligible',
    'Organ Failure',
    'Rejected',
    'Deceased',
    'Death but Eligible Transplant',
    'Death but Ineligible Transplant',
}
BLOCKCHAIN_LOCKED_STATUSES = {'Available', 'Matched', 'Transplanted', 'Case Closed', 'Blockchain Verified'}

def home(request):
    return render(request, 'core/home.html')

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True, redirect_url='/dashboard/donor/')
            return redirect('donor_dashboard')
        else:
            logger.error("Donor Registration Form Errors: %s", form.errors)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False, errors=form.errors.get_json_data())
    else:
        form = DonorRegistrationForm()
    return render(request, 'core/register_donor.html', {'form': form})

def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True, redirect_url='/dashboard/hospital/')
            return redirect('hospital_dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False, errors=form.errors.get_json_data())
    else:
        form = HospitalRegistrationForm()
    return render(request, 'core/register_hospital.html', {'form': form})

@login_required
def donor_dashboard(request):
    if not hasattr(request.user, 'donorprofile'):
        return redirect('home')
    
    approval_status = request.user.donorprofile.approval_status
    if approval_status == 'Pending':
        return render(request, 'core/donor_pending.html', {'status': 'Pending'})
    elif approval_status in ['Under Testing', 'Approved', 'Eligible', 'Not Eligible', 'Organ Failure', 'Deceased']:
        return render(request, 'core/donor_pending.html', {'status': approval_status})
    elif approval_status == 'Rejected':
        return render(request, 'core/donor_pending.html', {'status': 'Rejected'})

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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True)
            return redirect('donor_dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False, errors=feedback_form.errors.get_json_data())

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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True)
            return redirect('donor_dashboard')
        else:
            messages.error(request, "Please correct the highlighted profile details.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False, errors=profile_form.errors.get_json_data())



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

    })


@login_required
def hospital_dashboard(request):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')
    hospital = request.user.hospitalprofile
    hospital_profile_form = HospitalProfileEditForm(instance=hospital, user=request.user)
    
    cert_form = DeathCertificateForm()
    cert_form.fields['donor'].queryset = DonorProfile.objects.filter(
        assigned_hospital=hospital, approval_status__in=['Approved', 'Eligible', 'Deceased'], is_deceased=False
    )

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'update_details':
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
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=True)
                return redirect('hospital_dashboard')
            else:
                messages.error(request, "Please correct the highlighted hospital profile details.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=False, errors=hospital_profile_form.errors.get_json_data())

        elif form_type == 'issue_death_certificate':
            cert_form = DeathCertificateForm(request.POST)
            cert_form.fields['donor'].queryset = DonorProfile.objects.filter(
                assigned_hospital=hospital, approval_status__in=['Approved', 'Eligible', 'Deceased'], is_deceased=False
            )
            if cert_form.is_valid():
                with transaction.atomic():
                    cert = cert_form.save(commit=False)
                    cert.issued_by = hospital
                    
                    donor = cert.donor
                    donor.is_deceased = True
                    donor.assigned_hospital = hospital
                    donor.save()
                    
                    cert.save()
                    
                    # Associate OrganRecord with the hospital and mark the donor as deceased for review.
                    organ = OrganRecord.objects.filter(donor=donor).first()
                    if organ:
                        organ.registered_by = hospital
                        organ.status = 'Deceased'
                        organ.save()

                    AuditLog.objects.create(
                        user=request.user,
                        action=f"Hospital {hospital.hospital_name} issued death certificate #{cert.certificate_number} for donor {cert.donor.user.username} and started review.",
                        ip_address=request.META.get('REMOTE_ADDR')
                    )

                messages.success(request, f"Death certificate #{cert.certificate_number} issued successfully.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=True, redirect_url='/dashboard/hospital/#hosp-death-certificates')
                return redirect('/dashboard/hospital/#hosp-death-certificates')
            else:
                messages.error(request, "Error issuing certificate. Please check the details.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=False, errors=cert_form.errors.get_json_data())

        elif form_type == 'add_recipient':
            recipient_form = RecipientForm(request.POST)
            if recipient_form.is_valid():
                new_recipient = recipient_form.save(commit=False)
                new_recipient.hospital = hospital
                new_recipient.save()
                messages.success(request, f"Recipient '{new_recipient.full_name}' added successfully.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=True, redirect_url='/dashboard/hospital/#hosp-recipients')
                return redirect('/dashboard/hospital/#hosp-recipients')
            else:
                messages.error(request, "Error adding recipient. Please check the details.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=False, errors=recipient_form.errors.get_json_data())

    recipient_form = RecipientForm()
    recipients = Recipient.objects.filter(hospital=hospital).order_by('-created_at')

    registered_organs = OrganRecord.objects.select_related('donor__user', 'registered_by').filter(
        Q(registered_by=hospital) | Q(donor__assigned_hospital=hospital)
    ).distinct().order_by('-created_at')
    received_organs = OrganRecord.objects.select_related('registered_by', 'donor__user').filter(
        recipient_hospital=hospital, status__in=['Matched', 'Transplanted']
    ).order_by('-created_at')
    available_organs = OrganRecord.objects.select_related('registered_by', 'donor__user').filter(
        status__in=['Available', 'Blockchain Verified']
    ).exclude(registered_by=hospital).order_by('-created_at')
    unclaimed_organs = OrganRecord.objects.none()
    status_history = OrganStatusHistory.objects.all().order_by('-timestamp')

    # Hospitals should only see donor cases assigned to them.
    all_donors = DonorProfile.objects.select_related('user').filter(assigned_hospital=hospital, user__is_active=True)
    
    # Pending donor requests
    pending_donors = all_donors.filter(approval_status='Pending')
    
    # Rejected donor requests
    rejected_donors = all_donors.filter(approval_status='Rejected')

    # Assigned donors for this hospital
    assigned_donors = all_donors
    
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

    transplants = Transplant.objects.select_related('donor__user', 'recipient', 'hospital').filter(
        hospital=hospital
    ).order_by('-created_at')
    blockchain_transactions = BlockchainTransaction.objects.filter(hospital=hospital).order_by('-timestamp')
    issued_certificates = DeathCertificate.objects.filter(issued_by=hospital).select_related('donor__user').order_by('-issued_at')

    return render(request, 'core/hospital_dashboard.html', {
        'registered_organs': registered_organs,
        'received_organs': received_organs,
        'available_organs': available_organs,
        'unclaimed_organs': unclaimed_organs,
        'status_history': status_history,
        'all_donors': all_donors,
        'pending_donors': pending_donors,
        'rejected_donors': rejected_donors,
        'assigned_donors': assigned_donors,
        'transplants': transplants,
        'blockchain_transactions': blockchain_transactions,
        'cert_form': cert_form,
        'issued_certificates': issued_certificates,
        'recipients': recipients,
        'recipient_form': recipient_form,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'theme_form': ThemeSettingsForm(instance=request.user),
        'hospital_profile_form': hospital_profile_form,
        'search_organ': search_organ,
        'search_location': search_location,
        # Pipeline counts for status bar
        'pipeline_registered':    registered_organs.filter(status='Pending').count(),
        'pipeline_under_review':  registered_organs.filter(status='Under Testing').count(),
        'pipeline_verified':      registered_organs.filter(status__in=['Approved', 'Eligible', 'Not Eligible']).count(),
        'pipeline_submitted':     registered_organs.filter(status='Eligible').count(),
        'pipeline_blockchain':    registered_organs.filter(status__in=['Available', 'Matched']).count(),
        'pipeline_completed':     registered_organs.filter(status__in=['Transplanted', 'Case Closed', 'Rejected']).count(),
    })

# register_organ workflow removed and integrated into hospital_accept_donor


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

    if request.method == 'POST':
        admin_action = request.POST.get('admin_action')

        if admin_action == 'add_hospital':
            hospital_form = AdminHospitalManagementForm(request.POST, request.FILES)
            if hospital_form.is_valid():
                hospital_user = hospital_form.save()
                messages.success(request, f"Hospital {hospital_user.hospitalprofile.hospital_name} added successfully.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=True)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Unable to add hospital. Please correct the highlighted details.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=False, errors=hospital_form.errors.get_json_data())

        elif admin_action == 'update_user':
            user_id = request.POST.get('user_id')
            success = False
            if user_id:
                success = _update_user_from_admin_post(request, user_id)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=success)
            return redirect('admin_dashboard')

        elif admin_action == 'approve_user':
            user_id = request.POST.get('user_id')
            success = False
            if user_id:
                user = get_object_or_404(User, pk=user_id)
                with transaction.atomic():
                    user.is_approved = True
                    user.save()
                    if hasattr(user, 'donorprofile'):
                        donor = user.donorprofile
                        donor.approval_status = 'Approved'
                        donor.save()
                        # Keep one local organ workflow record for the assigned hospital.
                        organ, created = OrganRecord.objects.get_or_create(
                            donor=donor,
                            defaults={
                                'organ_type': donor.pledged_organ or 'Kidney',
                                'blood_group': donor.blood_group,
                                'status': 'Pending',
                                'registered_by': donor.assigned_hospital,
                            }
                        )
                        if not created and not organ.blockchain_tx_hash:
                            organ.registered_by = organ.registered_by or donor.assigned_hospital
                            organ.save(update_fields=['registered_by'])
                        # Create Status History
                        OrganStatusHistory.objects.create(
                            organ_record=organ,
                            previous_status=None,
                            new_status=organ.status,
                            updated_by=request.user
                        )
                        # Create AuditLog
                        AuditLog.objects.create(
                            user=request.user,
                            action=f"Admin approved donor account {user.username} (Pledge: {organ.organ_type}) for hospital verification.",
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                        messages.success(request, f"Donor {user.get_full_name() or user.username} has been approved for hospital verification.")
                    else:
                        messages.success(request, f"User {user.username} approved.")
                    success = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=success)
            return redirect('admin_dashboard')

        elif admin_action == 'reject_user':
            user_id = request.POST.get('user_id')
            success = False
            if user_id:
                user = get_object_or_404(User, pk=user_id)
                with transaction.atomic():
                    user.is_approved = False
                    user.save()
                    if hasattr(user, 'donorprofile'):
                        donor = user.donorprofile
                        donor.approval_status = 'Rejected'
                        donor.save()
                        messages.success(request, f"Donor {user.get_full_name() or user.username} has been rejected.")
                    else:
                        messages.success(request, f"User {user.username} rejected.")
                    success = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=success)
            return redirect('admin_dashboard')

        elif admin_action == 'update_admin_profile':
            admin_form = AdminProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if admin_form.is_valid():
                password_changed = bool(admin_form.cleaned_data.get('new_password'))
                admin_form.save()
                if password_changed:
                    update_session_auth_hash(request, request.user)
                messages.success(request, "Your profile has been updated successfully.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=True)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Error updating profile. Please check the details.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return ajax_response(request, success=False, errors=admin_form.errors.get_json_data())

        elif admin_action == 'update_organ_status':
            organ_id = request.POST.get('organ_id')
            success = False
            if organ_id:
                success = _update_organ_status_from_admin_post(request, organ_id)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=success)
            return redirect('admin_dashboard')

        elif admin_action == 'delete_feedback':
            fb_id = request.POST.get('feedback_id')
            if fb_id:
                fb = get_object_or_404(Feedback, pk=fb_id)
                fb.delete()
                messages.success(request, "Feedback deleted.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True)
            return redirect('admin_dashboard')

    organs = OrganRecord.objects.all().order_by('-created_at')
    hospitals = HospitalProfile.objects.all()
    donors = DonorProfile.objects.select_related('user').all().order_by('user__username')
    users = User.objects.all().order_by('username')
    # User Management section: only show regular users (not hospital, not donor, not admin)
    plain_users = User.objects.filter(is_superuser=False, is_hospital=False).order_by('username')
    pending_users = User.objects.filter(is_approved=False).exclude(donorprofile__approval_status='Rejected').order_by('date_joined')
    all_recipients = Recipient.objects.select_related('hospital').all().order_by('-created_at')
    all_death_certs = DeathCertificate.objects.select_related('donor__user', 'issued_by').all().order_by('-issued_at')
    feedbacks = Feedback.objects.select_related('user').all().order_by('-submitted_at')
    
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()


    transplants = Transplant.objects.all().order_by('-created_at')
    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    blockchain_txs = BlockchainTransaction.objects.all().order_by('-timestamp')
    status_history = OrganStatusHistory.objects.all().order_by('-timestamp')

    donors_count = DonorProfile.objects.count()
    pending_donors_count = DonorProfile.objects.filter(approval_status='Pending').count()
    approved_donors_count = DonorProfile.objects.filter(approval_status__in=['Approved', 'Eligible']).count()
    rejected_donors_count = DonorProfile.objects.filter(approval_status='Rejected').count()
    
    hospitals_count = hospitals.count()
    organs_count = organs.count()
    matches_count = organs.filter(status='Matched').count()
    transplants_count = organs.filter(status='Transplanted').count()
    available_count = organs.filter(status='Available').count()
    admins_count = users.filter(is_superuser=True).count()
    other_users_count = plain_users.count()
    blockchain_tx_count = blockchain_txs.count()
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
        'status_history': status_history,
        'all_recipients': all_recipients,
        'all_death_certs': all_death_certs,

        'transplants': transplants,
        'audit_logs': audit_logs,
        'blockchain_txs': blockchain_txs,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'theme_form': ThemeSettingsForm(instance=request.user),
        'hospital_management_form': hospital_form,
        'admin_profile_form': AdminProfileUpdateForm(instance=request.user),

        'stats': {
            'donors': donors_count,
            'pending_donors': pending_donors_count,
            'approved_donors': approved_donors_count,
            'rejected_donors': rejected_donors_count,
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
            'submitted_organs': organs.filter(status='Eligible').count(),
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
        return False

    if User.objects.filter(username=username).exclude(pk=account.pk).exists():
        messages.error(request, f"Username {username} is already in use.")
        return False

    if account == request.user and not is_active:
        messages.error(request, "You cannot block your own admin account.")
        return False

    if role == 'hospital' and not hasattr(account, 'hospitalprofile'):
        messages.error(request, "Only users with a hospital profile can be changed to Hospital role.")
        return False

    if role == 'donor' and not hasattr(account, 'donorprofile'):
        messages.error(request, "Only users with a donor profile can be changed to Donor role.")
        return False

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
    return True


def _update_organ_status_from_admin_post(request, organ_id):
    organ = get_object_or_404(OrganRecord, pk=organ_id)
    status = request.POST.get('status')
    if status not in {'Available', 'Matched', 'Transplanted'}:
        messages.error(request, "Invalid organ status selected.")
        return False

    organ.status = status
    if status == 'Available':
        organ.recipient_hospital = None
    organ.save(update_fields=['status', 'recipient_hospital'])

    AuditLog.objects.create(
        user=request.user,
        action=f"Admin manually changed organ #{organ.blockchain_id} ({organ.organ_type}) status to {status}.",
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f"Organ #{organ.blockchain_id} status changed to {status}.")
    return True


@user_passes_test(lambda u: u.is_superuser)
def delete_hospital(request, hospital_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')

    hospital = get_object_or_404(HospitalProfile, pk=hospital_id)
    hospital_name = hospital.hospital_name
    hospital.user.delete()
    messages.success(request, f"Hospital {hospital_name} deleted successfully.")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=True)
    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def admin_update_user(request, user_id):
    if request.method == 'POST':
        success = _update_user_from_admin_post(request, user_id)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=success)
    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def admin_update_organ_status(request, organ_id):
    if request.method == 'POST':
        success = _update_organ_status_from_admin_post(request, organ_id)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=success)
    return redirect('admin_dashboard')


@login_required
def hospital_update_organ_status(request, organ_id):
    if not hasattr(request.user, 'hospitalprofile'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')

    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')

    hospital = request.user.hospitalprofile
    organ = get_object_or_404(OrganRecord, pk=organ_id)
    
    if organ.registered_by != hospital and organ.donor.assigned_hospital != hospital:
        messages.error(request, "You can only update donors assigned to your hospital.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')
        
    has_blockchain_record = bool(organ.blockchain_id or organ.blockchain_tx_hash)
    if has_blockchain_record or organ.status in BLOCKCHAIN_LOCKED_STATUSES:
        messages.error(request, "Blockchain-approved donors are read-only and cannot be edited.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')

    organ_type = request.POST.get('organ_type', '').strip()
    blood_group = request.POST.get('blood_group', '').strip()
    new_status = request.POST.get('status', '').strip()
    medical_remarks = request.POST.get('medical_remarks', '').strip()
    valid_organs = {choice[0] for choice in ORGAN_TYPE_CHOICES}
    valid_blood_groups = {choice[0] for choice in BLOOD_GROUP_CHOICES}

    if organ_type and organ_type not in valid_organs:
        messages.error(request, "Invalid organ type selected.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')

    if blood_group and blood_group not in valid_blood_groups:
        messages.error(request, "Invalid blood group selected.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')

    if new_status and new_status not in HOSPITAL_DONOR_STATUSES:
        messages.error(request, "Invalid donor status selected.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('hospital_dashboard')

    old_status = organ.status
    update_fields = []
    if organ_type and organ.organ_type != organ_type:
        organ.organ_type = organ_type
        update_fields.append('organ_type')
    if blood_group and organ.blood_group != blood_group:
        organ.blood_group = blood_group
        update_fields.append('blood_group')
    if medical_remarks != (organ.medical_remarks or ''):
        organ.medical_remarks = medical_remarks
        update_fields.append('medical_remarks')
    if new_status and organ.status != new_status:
        actual_status = 'Waiting For Blockchain Approval' if new_status == 'Eligible' else new_status
        organ.status = actual_status
        update_fields.append('status')
        organ.donor.approval_status = actual_status
        organ.donor.assigned_hospital = hospital
        organ.donor.is_deceased = new_status in {'Deceased', 'Death but Eligible Transplant', 'Death but Ineligible Transplant'}
        organ.donor.save(update_fields=['approval_status', 'assigned_hospital', 'is_deceased'])
    if organ.registered_by_id is None:
        organ.registered_by = hospital
        update_fields.append('registered_by')

    if update_fields:
        organ.save(update_fields=update_fields)
    if old_status != organ.status:
        OrganStatusHistory.objects.create(
            organ_record=organ,
            previous_status=old_status,
            new_status=organ.status,
            updated_by=request.user
        )
        AuditLog.objects.create(
            user=request.user,
            action=f"Hospital updated donor {organ.donor.user.username} status from {old_status} to {organ.status}.",
            ip_address=request.META.get('REMOTE_ADDR')
        )

    messages.success(request, "Donor medical verification updated successfully.")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=True)
    return redirect('hospital_dashboard')


@login_required
def update_profile_picture(request):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')

    form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile picture updated successfully.")
        success = True
        errors = None
    else:
        messages.error(request, "Please upload a valid image file for the profile picture.")
        success = False
        errors = form.errors.get_json_data()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success, errors=errors)

    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'hospitalprofile'):
        return redirect('hospital_dashboard')
    if hasattr(request.user, 'donorprofile'):
        return redirect('donor_dashboard')
    return redirect('home')

@login_required
def update_theme(request):
    success = False
    if request.method == 'POST':
        form = ThemeSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Theme settings updated successfully.")
            success = True
        else:
            messages.error(request, "Error updating theme settings.")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)

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
    success = False
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            fb.sentiment = _analyze_sentiment(fb.message, fb.rating)
            fb.save()
            messages.success(request, "Thank you for your feedback!")
            success = True
        else:
            messages.error(request, "Please correct the errors in your feedback.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)

    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'hospitalprofile'):
        return redirect('hospital_dashboard')
    return redirect('donor_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    success = False
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            messages.error(request, "Cannot delete your own account.")
        else:
            if hasattr(user, 'donorprofile'):
                donor = user.donorprofile
                organs = OrganRecord.objects.filter(donor=donor)
                
                # Check 1: No blockchain transaction exists
                has_blockchain_tx = organs.filter(blockchain_id__isnull=False).exists() or \
                                    organs.filter(blockchain_tx_hash__isnull=False).exclude(blockchain_tx_hash='').exists()
                
                # Check 2: No recipient has been matched
                has_matched = organs.filter(status='Matched').exists()
                
                # Check 3: No transplant has been completed
                has_transplant = Transplant.objects.filter(donor=donor).exists() or organs.filter(status='Transplanted').exists()
                
                if has_blockchain_tx or has_matched or has_transplant:
                    messages.error(request, f"Cannot delete donor {user.username}: records exist on blockchain or have been matched/transplanted.")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return ajax_response(request, success=False)
                    return redirect('admin_dashboard')
                
                # Physical file cleanup for user profile images
                if user.profile_picture:
                    try:
                        user.profile_picture.delete(save=False)
                    except Exception:
                        pass
                if user.background_image:
                    try:
                        user.background_image.delete(save=False)
                    except Exception:
                        pass
            
            username = user.username
            user.delete()
            messages.success(request, f"User {username} deleted successfully.")
            success = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_approve_organ(request, organ_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    organ = get_object_or_404(OrganRecord, id=organ_id)
    if organ.blockchain_id or organ.blockchain_tx_hash:
        messages.error(request, "This organ is already registered on the blockchain.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    success = False
    old_status = organ.status
    try:
        donor = organ.donor
        hospital = organ.registered_by
        doctor_name = organ.status

        
        blockchain_receipt = register_organ_on_chain(
            donor_id=donor.user.id,
            donor_name=donor.user.get_full_name() or donor.user.username,
            organ_type=organ.organ_type,
            hospital_name=hospital.hospital_name if hospital else "Unknown",
            doctor_name=doctor_name,
            sender_address=hospital.blockchain_wallet_address if hospital else None,
        )
        
        if blockchain_receipt is not None:
            with transaction.atomic():
                if isinstance(blockchain_receipt, dict):
                    organ.blockchain_id = blockchain_receipt['blockchain_id']
                    organ.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                    organ.blockchain_block_number = blockchain_receipt['block_number']
                    organ.blockchain_timestamp = blockchain_receipt['timestamp']
                else:
                    organ.blockchain_id = blockchain_receipt
                
                organ.status = 'Blockchain Verified'
                organ.save()
                donor.approval_status = 'Blockchain Verified'
                donor.save(update_fields=['approval_status'])
                
                # Log status history
                OrganStatusHistory.objects.create(
                    organ_record=organ,
                    previous_status=old_status,
                    new_status='Blockchain Verified',
                    updated_by=request.user
                )
                
                # Create AuditLog
                AuditLog.objects.create(
                    user=request.user,
                    action=f"Admin approved organ submission #{organ.id} and registered organ #{organ.blockchain_id} ({organ.organ_type}) on blockchain.",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                # Create BlockchainTransaction record
                if organ.blockchain_tx_hash:
                    BlockchainTransaction.objects.create(
                        donor=donor,
                        hospital=hospital,
                        organ_type=organ.organ_type,
                        tx_hash=organ.blockchain_tx_hash,
                    )
                
                messages.success(request, f"Organ #{organ.blockchain_id} ({organ.organ_type}) has been successfully approved and registered on the blockchain.")
                success = True
        else:
            raise RuntimeError("Blockchain transaction failed to return a receipt.")
    except Exception as e:
        messages.error(request, f"Failed to approve organ: {_format_blockchain_error(e)}")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    return redirect('admin_dashboard')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_send_recipient_to_blockchain(request, recipient_id):
    """Admin-only: Register a hospital recipient on the Ganache blockchain."""
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')

    recipient = get_object_or_404(Recipient, pk=recipient_id)

    if recipient.blockchain_id or recipient.blockchain_tx_hash:
        messages.error(request, f"Recipient {recipient.full_name} is already registered on the blockchain.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('/dashboard/admin/#admin-recipients')

    success = False
    try:
        hospital = recipient.hospital
        blockchain_receipt = register_recipient_on_chain(
            recipient_id=recipient.id,
            full_name=recipient.full_name,
            blood_group=recipient.blood_group,
            organ_needed=recipient.organ_needed,
            hospital_name=hospital.hospital_name,
            sender_address=hospital.blockchain_wallet_address if hospital else None,
        )

        if blockchain_receipt is not None:
            with transaction.atomic():
                if isinstance(blockchain_receipt, dict):
                    recipient.blockchain_id = blockchain_receipt['blockchain_id']
                    recipient.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                else:
                    recipient.blockchain_id = str(blockchain_receipt)

                recipient.status = 'On Blockchain'
                recipient.save()

                # Record in BlockchainTransaction log
                if recipient.blockchain_tx_hash:
                    BlockchainTransaction.objects.create(
                        recipient=recipient,
                        hospital=hospital,
                        organ_type=recipient.organ_needed,
                        tx_hash=recipient.blockchain_tx_hash,
                    )

                AuditLog.objects.create(
                    user=request.user,
                    action=f"Admin sent recipient {recipient.full_name} (ID:{recipient.id}) to blockchain. TX: {recipient.blockchain_tx_hash}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                )

                messages.success(request, f"Recipient '{recipient.full_name}' has been registered on the blockchain. ID: {recipient.blockchain_id}")
                success = True
        else:
            raise RuntimeError("Blockchain transaction did not return a receipt.")

    except Exception as e:
        messages.error(request, f"Failed to send recipient to blockchain: {_format_blockchain_error(e)}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    return redirect('/dashboard/admin/#admin-recipients')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_reject_organ(request, organ_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    organ = get_object_or_404(OrganRecord, id=organ_id)
    if organ.status != 'Waiting For Blockchain Approval':
        messages.error(request, "Only Waiting For Blockchain Approval local donor cases can be returned or rejected by admin.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    action = request.POST.get('action')
    old_status = organ.status
    success = False
    
    with transaction.atomic():
        if action == 'return':
            organ.status = 'Under Testing'
            organ.save()
            
            # Log status history
            OrganStatusHistory.objects.create(
                organ_record=organ,
                previous_status=old_status,
                new_status='Under Testing',
                updated_by=request.user
            )
            
            AuditLog.objects.create(
                user=request.user,
                action=f"Admin returned organ submission #{organ.id} to hospital for correction.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Organ submission for donor {organ.donor.user.username} has been returned to hospital for correction.")
            success = True
        else:
            organ.status = 'Rejected'
            organ.save()
            organ.donor.approval_status = 'Rejected'
            organ.donor.save(update_fields=['approval_status'])
            
            # Log status history
            OrganStatusHistory.objects.create(
                organ_record=organ,
                previous_status=old_status,
                new_status='Rejected',
                updated_by=request.user
            )
            
            AuditLog.objects.create(
                user=request.user,
                action=f"Admin rejected organ submission #{organ.id}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Organ submission for donor {organ.donor.user.username} has been rejected.")
            success = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    return redirect('admin_dashboard')

@login_required
def delete_organ(request, organ_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')

    organ = get_object_or_404(OrganRecord, pk=organ_id)
    success = False
    
    if request.user.is_superuser:
        has_blockchain_record = bool(organ.blockchain_id or organ.blockchain_tx_hash)
        if has_blockchain_record or organ.status in BLOCKCHAIN_LOCKED_STATUSES:
            messages.error(request, "Cannot delete donors already registered on the blockchain.")
        elif organ.status not in ['Rejected', 'Not Eligible', 'Organ Failure']:
            messages.error(request, "Only rejected, not eligible, or organ failure donors can be permanently deleted by admin.")
        else:
            donor_user = organ.donor.user
            username = donor_user.username
            if donor_user.profile_picture:
                try:
                    donor_user.profile_picture.delete(save=False)
                except Exception:
                    pass
            if donor_user.background_image:
                try:
                    donor_user.background_image.delete(save=False)
                except Exception:
                    pass
            organ.delete()
            donor_user.delete()
            messages.success(request, f"Rejected donor {username} was permanently deleted from the database.")
            success = True
    elif hasattr(request.user, 'hospitalprofile'):
        messages.error(request, "Only admin can permanently delete rejected donors.")
    else:
        messages.error(request, "Access denied.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('hospital_dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_complete_transplant(request, organ_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    organ = get_object_or_404(OrganRecord, id=organ_id)
    if organ.status != 'Matched':
        messages.error(request, "Organ must be in Matched status to complete transplant.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    recipient_hospital = organ.recipient_hospital
    transplant = Transplant.objects.filter(organ=organ, match_status='Approved').first()
    
    recipient = transplant.recipient if (transplant and transplant.recipient) else None
    
    # Verify if Ganache was reset (state check)
    try:
        from .blockchain.service import get_contract
        contract = get_contract()
        on_chain_organ_count = contract.functions.organCount().call()
        on_chain_recipient_count = contract.functions.recipientCount().call()
        
        if organ.blockchain_id and int(organ.blockchain_id) > on_chain_organ_count:
            logger.info("Organ blockchain_id is out of range in complete_transplant. Clearing blockchain info to re-register.")
            organ.blockchain_id = None
            organ.blockchain_tx_hash = None
            organ.save()
            
        if recipient and recipient.blockchain_id:
            try:
                blockchain_id_str = str(recipient.blockchain_id).strip()
                if '-' in blockchain_id_str:
                    rec_id_int = int(blockchain_id_str.split('-')[-1]) - 1000
                else:
                    rec_id_int = int(blockchain_id_str)
            except Exception:
                rec_id_int = 0
            if rec_id_int > on_chain_recipient_count:
                logger.info("Recipient blockchain_id is out of range in complete_transplant. Clearing blockchain info to re-register.")
                recipient.blockchain_id = None
                recipient.blockchain_tx_hash = None
                recipient.save()
    except Exception as e:
        logger.warning("Failed to verify blockchain counts in complete_transplant: %s", e)
        
    # If recipient is not on blockchain yet, register it first!
    if recipient and not recipient.blockchain_id:
        try:
            logger.info("Recipient blockchain_id is NULL in complete_transplant. Registering recipient first.")
            blockchain_receipt = register_recipient_on_chain(
                recipient_id=recipient.id,
                full_name=recipient.full_name,
                blood_group=recipient.blood_group,
                organ_needed=recipient.organ_needed,
                hospital_name=recipient.hospital.hospital_name,
            )
            if blockchain_receipt:
                with transaction.atomic():
                    recipient.blockchain_id = blockchain_receipt['blockchain_id']
                    recipient.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                    recipient.save()
            else:
                raise RuntimeError("Blockchain transaction failed to return a receipt.")
        except Exception as e:
            messages.error(request, f"Failed to register recipient on blockchain: {_format_blockchain_error(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False)
            return redirect('admin_dashboard')

    recipient_blockchain_id = recipient.blockchain_id if recipient else None

    # If organ is not on blockchain yet, register it first!
    organ_was_just_registered = False
    if not organ.blockchain_id:
        try:
            donor = organ.donor
            hospital = organ.registered_by
            doctor_name = organ.status
            logger.info("Organ blockchain_id is NULL in complete_transplant. Registering organ first.")
            blockchain_receipt = register_organ_on_chain(
                donor_id=donor.user.id,
                donor_name=donor.user.get_full_name() or donor.user.username,
                organ_type=organ.organ_type,
                hospital_name=hospital.hospital_name,
                doctor_name=doctor_name,
                sender_address=hospital.blockchain_wallet_address,
            )
            if blockchain_receipt:
                with transaction.atomic():
                    organ.blockchain_id = blockchain_receipt['blockchain_id']
                    organ.blockchain_tx_hash = blockchain_receipt['transaction_hash']
                    organ.blockchain_block_number = blockchain_receipt['block_number']
                    organ.blockchain_timestamp = blockchain_receipt['timestamp']
                    organ.save()
                    
                    donor.approval_status = 'Accepted'
                    donor.save()
                organ_was_just_registered = True
            else:
                raise RuntimeError("Blockchain transaction failed to return a receipt.")
        except Exception as e:
            messages.error(request, f"Failed to register organ on blockchain: {_format_blockchain_error(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False)
            return redirect('admin_dashboard')

    # If the organ was just registered, it is in 'Available' status on-chain. Match it on-chain now!
    if organ_was_just_registered:
        try:
            match_organ_on_chain(
                organ_id=organ.blockchain_id,
                recipient_hospital_name=recipient_hospital.hospital_name,
                recipient_blockchain_id=recipient_blockchain_id,
                matching_admin_address=None
            )
        except Exception as e:
            messages.error(request, f"Failed to match organ on blockchain: {_format_blockchain_error(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False)
            return redirect('admin_dashboard')

    success = False
    try:
        blockchain_receipt = transplant_organ_on_chain(
            organ_id=organ.blockchain_id,
            recipient_blockchain_id=recipient_blockchain_id,
            hospital_address=recipient_hospital.blockchain_wallet_address
        )
        
        receipt_succeeded = (
            blockchain_receipt is True
            or getattr(blockchain_receipt, 'status', None) == 1
            or (isinstance(blockchain_receipt, dict) and blockchain_receipt.get('status') == 1)
        )
        
        if blockchain_receipt and receipt_succeeded:
            with transaction.atomic():
                organ.status = 'Transplanted'
                if isinstance(blockchain_receipt, dict):
                    organ.blockchain_tx_hash = blockchain_receipt.get('transaction_hash')
                    organ.blockchain_block_number = blockchain_receipt.get('block_number')
                organ.save()
                
                # Log to OrganStatusHistory
                OrganStatusHistory.objects.create(
                    organ_record=organ,
                    previous_status='Matched',
                    new_status='Transplanted',
                    updated_by=request.user
                )
                
                # Update Transplant record
                transplant = Transplant.objects.filter(organ=organ, match_status='Approved').first()
                if transplant:
                    transplant.match_status = 'Completed'
                    transplant.blockchain_tx_hash = organ.blockchain_tx_hash
                    transplant.save()
                    
                    if transplant.recipient:
                        transplant.recipient.status = 'Transplanted'
                        transplant.recipient.save()
                        
                # Create BlockchainTransaction record
                if organ.blockchain_tx_hash:
                    BlockchainTransaction.objects.create(
                        donor=organ.donor,
                        recipient=transplant.recipient if transplant else None,
                        hospital=recipient_hospital,
                        organ_type=organ.organ_type,
                        tx_hash=organ.blockchain_tx_hash
                    )
                    
                AuditLog.objects.create(
                    user=request.user,
                    action=f"Admin confirmed transplant for organ #{organ.blockchain_id} ({organ.organ_type}).",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                messages.success(request, f"Transplant for organ #{organ.blockchain_id} has been completed and recorded on the blockchain.")
                success = True
        else:
            messages.error(request, "Blockchain transplant transaction failed.")
    except Exception as e:
        messages.error(request, f"Failed to complete transplant: {_format_blockchain_error(e)}")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=success)
    return redirect('admin_dashboard')

@login_required
def hospital_transition_organ(request, organ_id):
    if not hasattr(request.user, 'hospitalprofile'):
        messages.error(request, "Access denied. Only hospitals can transition donation status.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')

    hospital = request.user.hospitalprofile
    organ = get_object_or_404(OrganRecord, pk=organ_id)

    if organ.recipient_hospital == hospital and organ.status == 'Matched':
        if request.method == 'POST':
            transplant = Transplant.objects.filter(organ=organ, match_status='Approved').first()
            recipient = transplant.recipient if transplant else None
            recipient_blockchain_id = recipient.blockchain_id if recipient else None

            try:
                # Execute completeTransplant blockchain transaction
                blockchain_receipt = transplant_organ_on_chain(
                    organ_id=organ.blockchain_id,
                    recipient_blockchain_id=recipient_blockchain_id,
                    hospital_address=hospital.blockchain_wallet_address
                )

                receipt_succeeded = (
                    blockchain_receipt is True
                    or getattr(blockchain_receipt, 'status', None) == 1
                    or (isinstance(blockchain_receipt, dict) and blockchain_receipt.get('status') == 1)
                )

                if blockchain_receipt and receipt_succeeded:
                    tx_hash = blockchain_receipt.get('transaction_hash') if isinstance(blockchain_receipt, dict) else None
                    block_number = blockchain_receipt.get('block_number') if isinstance(blockchain_receipt, dict) else None
                    from django.utils import timezone as tz

                    with transaction.atomic():
                        organ.status = 'Transplanted'
                        if tx_hash:
                            organ.blockchain_tx_hash = tx_hash
                        if block_number:
                            organ.blockchain_block_number = block_number
                        organ.blockchain_timestamp = tz.now()
                        organ.save()

                        # Recipient -> Transplanted
                        if recipient:
                            recipient.status = 'Transplanted'
                            recipient.save(update_fields=['status'])

                        # Update Transplant record -> Completed
                        if transplant:
                            transplant.match_status = 'Completed'
                            if tx_hash:
                                transplant.blockchain_tx_hash = tx_hash
                            transplant.save()

                        # Status history
                        OrganStatusHistory.objects.create(
                            organ_record=organ,
                            previous_status='Matched',
                            new_status='Transplanted',
                            updated_by=request.user,
                        )

                        # BlockchainTransaction log
                        if tx_hash and not BlockchainTransaction.objects.filter(tx_hash=tx_hash).exists():
                            BlockchainTransaction.objects.create(
                                donor=organ.donor,
                                recipient=recipient,
                                hospital=hospital,
                                organ_type=organ.organ_type,
                                tx_hash=tx_hash,
                            )

                        AuditLog.objects.create(
                            user=request.user,
                            action=f"Hospital {hospital.hospital_name} completed transplant for organ #{organ.blockchain_id} ({organ.organ_type}). TX: {tx_hash}",
                            ip_address=request.META.get('REMOTE_ADDR'),
                        )

                    success_msg = "Transplant completed successfully."
                    messages.success(request, success_msg)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': success_msg,
                            'transaction_hash': tx_hash,
                            'block_number': block_number,
                            'redirect_url': '/dashboard/hospital/#hosp-received'
                        })
                    return redirect('/dashboard/hospital/#hosp-received')
                else:
                    msg = "Blockchain transplant transaction failed."
                    messages.error(request, msg)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': msg})
                    return redirect('/dashboard/hospital/#hosp-received')
            except Exception as e:
                msg = f"Failed to complete transplant: {_format_blockchain_error(e)}"
                messages.error(request, msg)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': msg})
                return redirect('/dashboard/hospital/#hosp-received')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)
            return redirect('hospital_dashboard')

    return hospital_update_organ_status(request, organ_id)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def match_organ(request, organ_id):
    """Fallback / legacy match_organ view restricted to superusers."""
    messages.error(request, "Access denied. Only administrators can match organs.")
    return redirect('admin_dashboard')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_match_organ(request, organ_id):
    """Admin: Match an organ with a recipient — ONE blockchain tx (matchOrgan only), status → Matched."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method != 'POST':
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)
        return redirect('admin_dashboard')

    organ = get_object_or_404(OrganRecord, pk=organ_id)
    recipient_id = request.POST.get('recipient_id')

    if not recipient_id:
        msg = 'Please select a recipient.'
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg})
        messages.error(request, msg)
        return redirect('admin_dashboard')

    recipient = get_object_or_404(Recipient, pk=recipient_id)

    # ── Validate compatibility ────────────────────────────────────────────
    if organ.organ_type.lower() != recipient.organ_needed.lower():
        msg = f"Incompatible organ type: Organ is {organ.organ_type}, recipient needs {recipient.organ_needed}."
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg})
        messages.error(request, msg)
        return redirect('admin_dashboard')

    if organ.blood_group != recipient.blood_group:
        msg = f"Incompatible blood group: Organ is {organ.blood_group}, recipient is {recipient.blood_group}."
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg})
        messages.error(request, msg)
        return redirect('admin_dashboard')

    # ── Auto-heal stale blockchain IDs if Ganache was reset ──────────────
    try:
        from .blockchain.service import get_contract
        contract = get_contract()
        on_chain_organ_count = contract.functions.organCount().call()
        on_chain_recipient_count = contract.functions.recipientCount().call()

        if organ.blockchain_id and int(organ.blockchain_id) > on_chain_organ_count:
            logger.info("Organ blockchain_id out of range — clearing to re-register.")
            organ.blockchain_id = None
            organ.blockchain_tx_hash = None
            organ.blockchain_block_number = None
            organ.save(update_fields=['blockchain_id', 'blockchain_tx_hash', 'blockchain_block_number'])

        if recipient.blockchain_id:
            import re as _re
            _rnum = int(_re.sub(r'\D', '', str(recipient.blockchain_id)) or '0')
            if _rnum > on_chain_recipient_count:
                logger.info("Recipient blockchain_id out of range — clearing to re-register.")
                recipient.blockchain_id = None
                recipient.blockchain_tx_hash = None
                recipient.save(update_fields=['blockchain_id', 'blockchain_tx_hash'])
    except Exception as _e:
        logger.warning("Failed to verify blockchain state in admin_match_organ: %s", _e)

    # ── Register recipient on blockchain if missing ───────────────────────
    if not recipient.blockchain_id:
        try:
            logger.info("Registering recipient on blockchain before matching.")
            bc_rec = register_recipient_on_chain(
                recipient_id=recipient.id,
                full_name=recipient.full_name,
                blood_group=recipient.blood_group,
                organ_needed=recipient.organ_needed,
                hospital_name=recipient.hospital.hospital_name,
            )
            if not bc_rec:
                raise RuntimeError("register_recipient_on_chain returned None.")
            recipient.blockchain_id = bc_rec['blockchain_id']
            recipient.blockchain_tx_hash = bc_rec['transaction_hash']
            recipient.save(update_fields=['blockchain_id', 'blockchain_tx_hash'])
        except Exception as e:
            msg = f"Failed to register recipient on blockchain: {_format_blockchain_error(e)}"
            logger.error(msg)
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg})
            messages.error(request, msg)
            return redirect('admin_dashboard')

    # ── Register organ on blockchain if missing ───────────────────────────
    if not organ.blockchain_id:
        try:
            donor = organ.donor
            hospital = organ.registered_by
            logger.info("Registering organ on blockchain before matching.")
            bc_org = register_organ_on_chain(
                donor_id=donor.user.id,
                donor_name=donor.user.get_full_name() or donor.user.username,
                organ_type=organ.organ_type,
                hospital_name=hospital.hospital_name if hospital else 'Unknown',
                doctor_name=organ.status,
                sender_address=hospital.blockchain_wallet_address if hospital else None,
            )
            if not bc_org:
                raise RuntimeError("register_organ_on_chain returned None.")
            organ.blockchain_id = bc_org['blockchain_id']
            organ.blockchain_tx_hash = bc_org['transaction_hash']
            organ.blockchain_block_number = bc_org.get('block_number')
            organ.blockchain_timestamp = bc_org.get('timestamp')
            organ.save(update_fields=['blockchain_id', 'blockchain_tx_hash',
                                      'blockchain_block_number', 'blockchain_timestamp'])
        except Exception as e:
            msg = f"Failed to register organ on blockchain: {_format_blockchain_error(e)}"
            logger.error(msg)
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg})
            messages.error(request, msg)
            return redirect('admin_dashboard')

    # ── matchOrgan blockchain transaction (ONLY this one — no transplant here) ──
    try:
        match_receipt = match_organ_on_chain(
            organ_id=organ.blockchain_id,
            recipient_hospital_name=recipient.hospital.hospital_name,
            recipient_blockchain_id=recipient.blockchain_id,
        )
        if not match_receipt:
            raise RuntimeError("match_organ_on_chain returned None.")
    except Exception as e:
        msg = f"Blockchain match transaction failed: {_format_blockchain_error(e)}"
        logger.error(msg)
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg})
        messages.error(request, msg)
        return redirect('admin_dashboard')

    # ── Extract tx details ────────────────────────────────────────────────
    tx_hash = match_receipt.get('transaction_hash') if isinstance(match_receipt, dict) else None
    block_number = match_receipt.get('block_number') if isinstance(match_receipt, dict) else None

    # ── Atomically update database: status → Matched ─────────────────────
    try:
        from django.utils import timezone as tz
        with transaction.atomic():
            prev_status = organ.status

            organ.status = 'Matched'
            organ.recipient_hospital = recipient.hospital
            if tx_hash:
                organ.blockchain_tx_hash = tx_hash
            if block_number:
                organ.blockchain_block_number = block_number
            organ.blockchain_timestamp = tz.now()
            organ.save()

            recipient.status = 'Matched'
            recipient.save(update_fields=['status'])

            # Create Transplant record (match_status=Approved so hospital can complete it)
            transplant_obj, _ = Transplant.objects.get_or_create(
                organ=organ,
                defaults={
                    'donor': organ.donor,
                    'recipient': recipient,
                    'hospital': recipient.hospital,
                    'match_status': 'Approved',
                }
            )
            transplant_obj.match_status = 'Approved'
            transplant_obj.recipient = recipient
            transplant_obj.hospital = recipient.hospital
            if tx_hash:
                transplant_obj.blockchain_tx_hash = tx_hash
            transplant_obj.save()

            OrganStatusHistory.objects.create(
                organ_record=organ,
                previous_status=prev_status,
                new_status='Matched',
                updated_by=request.user,
            )

            if tx_hash and not BlockchainTransaction.objects.filter(tx_hash=tx_hash).exists():
                BlockchainTransaction.objects.create(
                    donor=organ.donor,
                    recipient=recipient,
                    hospital=recipient.hospital,
                    organ_type=organ.organ_type,
                    tx_hash=tx_hash,
                )

            AuditLog.objects.create(
                user=request.user,
                action=(f"Admin matched organ #{organ.blockchain_id} ({organ.organ_type}) "
                        f"to {recipient.full_name} at {recipient.hospital.hospital_name}. TX: {tx_hash}"),
                ip_address=request.META.get('REMOTE_ADDR'),
            )
    except Exception as e:
        msg = f"Database update failed after blockchain match: {str(e)}"
        logger.error(msg)
        if is_ajax:
            return JsonResponse({'success': False, 'message': msg})
        messages.error(request, msg)
        return redirect('admin_dashboard')

    # ── Success ───────────────────────────────────────────────────────────
    success_msg = "✅ Organ matched successfully and recorded on Blockchain."
    messages.success(request, success_msg)

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'transaction_hash': tx_hash,
            'block_number': block_number,
            'redirect_url': '/dashboard/admin/#admin-ledger',
        })
    return redirect('admin_dashboard')













@login_required
def hospital_edit_recipient(request, recipient_id):
    if not hasattr(request.user, 'hospitalprofile'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')
    hospital = request.user.hospitalprofile
    recipient = get_object_or_404(Recipient, pk=recipient_id, hospital=hospital)
    
    if recipient.blockchain_id or recipient.blockchain_tx_hash:
        messages.error(request, "Registered recipients cannot be edited.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('/dashboard/hospital/#hosp-recipients')
        
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Recipient '{recipient.full_name}' updated successfully.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=True, redirect_url='/dashboard/hospital/#hosp-recipients')
            return redirect('/dashboard/hospital/#hosp-recipients')
        else:
            messages.error(request, "Error updating recipient. Please check details.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(request, success=False, errors=form.errors.get_json_data())
                
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=False)
    return redirect('/dashboard/hospital/#hosp-recipients')


@login_required
def hospital_delete_recipient(request, recipient_id):
    if not hasattr(request.user, 'hospitalprofile'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('home')
    hospital = request.user.hospitalprofile
    recipient = get_object_or_404(Recipient, pk=recipient_id, hospital=hospital)
    
    if recipient.blockchain_id or recipient.blockchain_tx_hash:
        messages.error(request, "Registered recipients cannot be deleted.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('/dashboard/hospital/#hosp-recipients')
        
    if request.method == 'POST':
        name = recipient.full_name
        recipient.delete()
        messages.success(request, f"Recipient '{name}' deleted successfully.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=True, redirect_url='/dashboard/hospital/#hosp-recipients')
        return redirect('/dashboard/hospital/#hosp-recipients')
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=False)
    return redirect('/dashboard/hospital/#hosp-recipients')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_recipient(request, recipient_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('admin_dashboard')
        
    recipient = get_object_or_404(Recipient, pk=recipient_id)
    if recipient.blockchain_id or recipient.blockchain_tx_hash:
        messages.error(request, "Registered recipients cannot be deleted.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(request, success=False)
        return redirect('/dashboard/admin/#admin-recipients')
        
    name = recipient.full_name
    recipient.delete()
    messages.success(request, f"Recipient '{name}' deleted permanently.")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return ajax_response(request, success=True, redirect_url='/dashboard/admin/#admin-recipients')
    return redirect('/dashboard/admin/#admin-recipients')


