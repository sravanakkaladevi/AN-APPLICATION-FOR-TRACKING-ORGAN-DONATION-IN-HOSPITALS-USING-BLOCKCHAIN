from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/hospital/', views.register_hospital, name='register_hospital'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/donor/', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('dashboard/admin/hospital/<int:hospital_id>/delete/', views.delete_hospital, name='delete_hospital'),
    path('dashboard/admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/admin/user/<int:user_id>/update/', views.admin_update_user, name='admin_update_user'),
    path('dashboard/admin/organ/<int:organ_id>/status/', views.admin_update_organ_status, name='admin_update_organ_status'),
    path('dashboard/hospital/organ/<int:organ_id>/status/', views.hospital_update_organ_status, name='hospital_update_organ_status'),
    path('dashboard/hospital/organ/<int:organ_id>/transition/', views.hospital_transition_organ, name='hospital_transition_organ'),
    path('dashboard/organ/<int:organ_id>/delete/', views.delete_organ, name='delete_organ'),
    path('dashboard/admin/organ/<int:organ_id>/approve/', views.admin_approve_organ, name='admin_approve_organ'),
    path('dashboard/admin/organ/<int:organ_id>/reject/', views.admin_reject_organ, name='admin_reject_organ'),
    path('dashboard/admin/organ/<int:organ_id>/complete/', views.admin_complete_transplant, name='admin_complete_transplant'),
    path('dashboard/admin/organ/<int:organ_id>/match/', views.admin_match_organ, name='admin_match_organ'),
    path('dashboard/admin/recipient/<int:recipient_id>/send_blockchain/', views.admin_send_recipient_to_blockchain, name='admin_send_recipient_to_blockchain'),
    path('dashboard/admin/recipient/<int:recipient_id>/delete/', views.admin_delete_recipient, name='admin_delete_recipient'),
    path('dashboard/hospital/recipient/<int:recipient_id>/edit/', views.hospital_edit_recipient, name='hospital_edit_recipient'),
    path('dashboard/hospital/recipient/<int:recipient_id>/delete/', views.hospital_delete_recipient, name='hospital_delete_recipient'),
    path('update-theme/', views.update_theme, name='update_theme'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('dashboard/hospital/organ/<int:organ_id>/match/', views.match_organ, name='match_organ'),
]
