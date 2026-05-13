import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stages.settings')
django.setup()

from stages.models import User

email = 'admin@example.com'
password = 'adminpass'
full_name = 'Admin'

if User.objects.filter(email=email).exists():
    print('superuser already exists')
else:
    User.objects.create_superuser(email=email, full_name=full_name, password=password)
    print('superuser created')
