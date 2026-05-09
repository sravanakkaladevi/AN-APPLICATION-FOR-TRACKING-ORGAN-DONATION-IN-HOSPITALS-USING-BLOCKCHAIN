from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api_views

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
    path('dashboard/admin/user/<int:user_id>/update/', views.admin_update_user, name='admin_update_user'),
    path('dashboard/admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/admin/organ/<int:organ_id>/status/', views.admin_update_organ_status, name='admin_update_organ_status'),
    path('dashboard/hospital/organ/<int:organ_id>/status/', views.hospital_update_organ_status, name='hospital_update_organ_status'),
    path('register-organ/', views.register_organ, name='register_organ'),
    path('match-organ/<int:organ_id>/', views.match_organ, name='match_organ'),
    path('update-theme/', views.update_theme, name='update_theme'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('admin/death-certificate/', views.issue_death_certificate, name='issue_death_certificate'),
    
    # Blockchain API Endpoints
    path('api/blockchain/register-donor/', api_views.api_register_donor, name='api_register_donor'),
    path('api/blockchain/get-donor/', api_views.api_get_donor, name='api_get_donor'),
    path('api/blockchain/verify/', api_views.api_verify_transaction, name='api_verify_transaction'),
]
