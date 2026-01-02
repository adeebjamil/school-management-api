import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from accounts.models import User
from tenants.models import Tenant
from library.models import Book

print("\n" + "="*60)
print("TENANT & BOOK ANALYSIS")
print("="*60 + "\n")

# Get admin user (the one logged in)
admin_user = User.objects.filter(email='adeeb.jamil1@gmail.com').first()
if admin_user:
    print(f"✓ Logged-in User: {admin_user.email}")
    print(f"  Name: {admin_user.first_name} {admin_user.last_name}")
    print(f"  Tenant: {admin_user.tenant.name}")
    print(f"  Tenant ID: {admin_user.tenant.id}")
    print()
    
    # Check books in user's tenant
    user_tenant_books = Book.objects.filter(tenant=admin_user.tenant)
    print(f"📚 Books in '{admin_user.tenant.name}': {user_tenant_books.count()}")
    for book in user_tenant_books:
        print(f"  - {book.title} by {book.author}")
    print()

# Get all tenants and their books
print("\n" + "="*60)
print("ALL TENANTS & BOOKS")
print("="*60 + "\n")
for tenant in Tenant.objects.all():
    books = Book.objects.filter(tenant=tenant)
    print(f"🏢 {tenant.name} (ID: {tenant.id})")
    print(f"   Books: {books.count()}")
    for book in books:
        print(f"   - {book.title} by {book.author}")
    print()

# Check if books are in wrong tenant
print("\n" + "="*60)
print("SOLUTION")
print("="*60 + "\n")

if admin_user:
    other_tenant_books = Book.objects.exclude(tenant=admin_user.tenant)
    if other_tenant_books.exists():
        print(f"⚠️  Found {other_tenant_books.count()} books in OTHER tenants!")
        print(f"\n   Should I move them to '{admin_user.tenant.name}'? (Y/N)")
        print(f"\n   Run this command to fix:")
        print(f"   python manage.py shell")
        print(f"   >>> from library.models import Book")
        print(f"   >>> from tenants.models import Tenant")
        print(f"   >>> tenant = Tenant.objects.get(name='Sunshine High School')")
        print(f"   >>> Book.objects.all().update(tenant=tenant)")
    else:
        print("✓ All books are in the correct tenant!")
