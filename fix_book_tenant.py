import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from accounts.models import User
from tenants.models import Tenant
from library.models import Book

print("\n🔍 Finding all users...")
all_users = User.objects.all()
print(f"Found {all_users.count()} users:\n")

for user in all_users:
    print(f"  📧 {user.email}")
    print(f"     Name: {user.first_name} {user.last_name}")
    print(f"     Role: {user.role}")
    if user.tenant:
        print(f"     Tenant: {user.tenant.name} (ID: {user.tenant.id})")
    else:
        print(f"     Tenant: None")
    print()

# Find tenant admin user
admin = User.objects.filter(role='tenant_admin').first()
if admin and admin.tenant:
    print(f"\n✓ Tenant Admin found: {admin.email}")
    print(f"  Tenant: {admin.tenant.name}")
    print(f"\n📚 Moving all books to {admin.tenant.name}...")
    
    updated_count = Book.objects.all().update(tenant=admin.tenant)
    print(f"✅ Moved {updated_count} books to {admin.tenant.name}")
    
    # Verify
    books = Book.objects.filter(tenant=admin.tenant)
    print(f"\n📖 Books in {admin.tenant.name}:")
    for book in books:
        print(f"  - {book.title} by {book.author}")
else:
    print("\n⚠️  No tenant admin found!")
