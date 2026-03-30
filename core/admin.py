from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DonorProfile, HospitalProfile, OrganRecord

admin.site.register(User, UserAdmin)
admin.site.register(DonorProfile)
admin.site.register(HospitalProfile)
admin.site.register(OrganRecord)
