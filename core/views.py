from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import DonorRegistrationForm, HospitalRegistrationForm, OrganRegistrationForm, ProfilePictureForm, AdminHospitalManagementForm
from .models import User, DonorProfile, HospitalProfile, OrganRecord
from .blockchain.service import register_organ_on_chain, match_organ_on_chain

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
    return render(request, 'core/donor_dashboard.html', {
        'organs': organs,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
    })

@login_required
def hospital_dashboard(request):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')
    hospital = request.user.hospitalprofile
    registered_organs = hospital.registered_organs.all()
    received_organs = hospital.received_organs.all()
    available_organs = OrganRecord.objects.filter(status='Available').exclude(registered_by=hospital)
    return render(request, 'core/hospital_dashboard.html', {
        'registered_organs': registered_organs,
        'received_organs': received_organs,
        'available_organs': available_organs,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
    })

@login_required
def register_organ(request):
    if not hasattr(request.user, 'hospitalprofile'):
        return redirect('home')
        
    if request.method == 'POST':
        form = OrganRegistrationForm(request.POST)
        if form.is_valid():
            organ = form.save(commit=False)
            
            # Automatically pull the blood group from the Donor's fixed profile
            organ.blood_group = organ.donor.blood_group
            
            # Interact with Blockchain (this might fail if blockchain is not up)
            try:
                donor_hash = str(organ.donor.user.id) # simple hash for now
                blockchain_id = register_organ_on_chain(donor_hash, organ.organ_type, organ.blood_group)
                if blockchain_id is not None:
                    organ.blockchain_id = blockchain_id
                    organ.registered_by = request.user.hospitalprofile
                    organ.save()
                    return redirect('hospital_dashboard')
                else:
                    form.add_error(None, "Blockchain transaction failed to return an ID.")
            except Exception as e:
                form.add_error(None, f"Blockchain error: {str(e)}")
    else:
        form = OrganRegistrationForm()
    
    return render(request, 'core/register_organ.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    if request.method == 'POST' and request.POST.get('admin_action') == 'add_hospital':
        hospital_form = AdminHospitalManagementForm(request.POST, request.FILES)
        if hospital_form.is_valid():
            hospital_user = hospital_form.save()
            messages.success(request, f"Hospital {hospital_user.hospitalprofile.hospital_name} added successfully.")
            return redirect('admin_dashboard')
        messages.error(request, "Unable to add hospital. Please correct the highlighted details.")
    else:
        hospital_form = AdminHospitalManagementForm()

    organs = OrganRecord.objects.all().order_by('-created_at')
    hospitals = HospitalProfile.objects.all()
    donors = DonorProfile.objects.select_related('user').all().order_by('user__username')
    users = User.objects.all().order_by('username')
    donors_count = DonorProfile.objects.count()
    hospitals_count = hospitals.count()
    organs_count = organs.count()
    matches_count = organs.filter(status='Matched').count()
    transplants_count = organs.filter(status='Transplanted').count()
    available_count = organs.filter(status='Available').count()
    
    context = {
        'organs': organs, 
        'hospitals': hospitals,
        'donors': donors,
        'users': users,
        'profile_picture_form': ProfilePictureForm(instance=request.user),
        'hospital_management_form': hospital_form,
        'stats': {
            'donors': donors_count,
            'hospitals': hospitals_count,
            'organs': organs_count,
            'matches': matches_count,
            'transplants': transplants_count,
            'available': available_count,
        },
        'chart_data': {
            'available': available_count,
            'matched': matches_count,
            'transplanted': transplants_count,
        },
    }
    return render(request, 'core/admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_hospital(request, hospital_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    hospital = get_object_or_404(HospitalProfile, pk=hospital_id)
    hospital_name = hospital.hospital_name
    hospital.user.delete()
    messages.success(request, f"Hospital {hospital_name} deleted successfully.")
    return redirect('admin_dashboard')


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
                    # In real-world, we'd pass proper Ethereum addresses
                    success = match_organ_on_chain(organ.blockchain_id, str(recipient.user.id), None)
                    if success:
                        organ.status = 'Matched'
                        organ.recipient_hospital = recipient
                        organ.save()
                        messages.success(request, f"Organ #{organ.blockchain_id} successfully matched to {recipient.hospital_name} on the blockchain.")
                    else:
                        messages.error(request, "Blockchain smart contract matching failed.")
                except Exception as e:
                    messages.error(request, f"Blockchain error: {str(e)}")
            else:
                messages.error(request, "No eligible recipient hospitals found in the network.")
        redirect_name = 'hospital_dashboard' if hasattr(request.user, 'hospitalprofile') else 'admin_dashboard'
        return redirect(redirect_name)
    return redirect('hospital_dashboard' if hasattr(request.user, 'hospitalprofile') else 'admin_dashboard')
