from django.contrib import admin
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate

admin.site.register(User)
admin.site.register(DonorProfile)
admin.site.register(HospitalProfile)
admin.site.register(OrganRecord)
admin.site.register(Feedback)
admin.site.register(DeathCertificate)
