import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from accounts.models import User
from tenants.models import Tenant
from library.models import Book

# Get all tenants
print("=== ALL TENANTS ===")
for tenant in Tenant.objects.all():
    print(f"  - {tenant.name} (ID: {tenant.id})")
    books_count = Book.objects.filter(tenant=tenant).count()
    print(f"    Books: {books_count}")
print()

# Get all users
print("=== USERS ===")
for user in User.objects.all():
    print(f"  - {user.email} ({user.first_name} {user.last_name})")
    print(f"    Tenant: {user.tenant.name if user.tenant else 'None'}")
    print(f"    Tenant ID: {user.tenant.id if user.tenant else 'None'}")
    print(f"    Role: {user.role}")
    print()

# Check books
print("=== ALL BOOKS ===")
for book in Book.objects.all():
    print(f"  - {book.title}")
    print(f"    Tenant: {book.tenant.name} (ID: {book.tenant.id})")
    print()
