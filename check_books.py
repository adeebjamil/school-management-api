import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from library.models import Book
from tenants.models import Tenant

# Get first tenant
tenant = Tenant.objects.first()
print(f'Tenant: {tenant}')
print(f'Tenant ID: {tenant.id if tenant else "None"}')
print()

# Get all books
all_books = Book.objects.all()
print(f'Total books in DB: {all_books.count()}')
print()

if tenant:
    # Get books for this tenant
    tenant_books = Book.objects.filter(tenant=tenant)
    print(f'Books for tenant {tenant.name}: {tenant_books.count()}')
    
    for book in tenant_books:
        print(f'  - {book.title} by {book.author}')
        print(f'    ISBN: {book.isbn}')
        print(f'    Copies: {book.available_copies}/{book.total_copies}')
        print()
else:
    print('No tenant found!')
