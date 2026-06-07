
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()
from api.models import User, Wallet
merchants = User.objects.filter(role='merchant')
for m in merchants:
    wallet, created = Wallet.objects.get_or_create(user=m)
    wallet.balance = 1000
    wallet.save()
    print(f'Updated wallet for {m.email} to 1000F')
