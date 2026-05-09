from django.contrib import admin
from .models import User, DonorProfile, HospitalProfile, OrganRecord, Feedback, DeathCertificate

@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ('hospital_name', 'blockchain_wallet_address', 'contact_email', 'city', 'state')
    search_fields = ('hospital_name', 'blockchain_wallet_address', 'contact_email')

admin.site.register(User)
admin.site.register(DonorProfile)
admin.site.register(OrganRecord)
admin.site.register(Feedback)
admin.site.register(DeathCertificate)
