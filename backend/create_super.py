import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organ_donation_project.settings')
django.setup()

from core.models import User

# Define superuser details
username = 'sravan'
password = '8309484956'
email = 'sravan@example.com'

# Check and create superuser
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' successfully created!")
else:
    # If the user exists but isn't a superuser, or needs password updated:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print(f"Superuser '{username}' updated successfully!")
