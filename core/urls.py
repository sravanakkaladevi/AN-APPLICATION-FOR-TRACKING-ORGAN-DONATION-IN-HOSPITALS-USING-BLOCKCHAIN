from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/hospital/', views.register_hospital, name='register_hospital'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/donor/', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('dashboard/admin/hospital/<int:hospital_id>/delete/', views.delete_hospital, name='delete_hospital'),
    path('register-organ/', views.register_organ, name='register_organ'),
    path('match-organ/<int:organ_id>/', views.match_organ, name='match_organ'),
]
