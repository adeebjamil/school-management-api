from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to identify tenant from subdomain or domain
    and inject tenant_id into the request
    """
    
    def process_request(self, request):
        # Get the host from the request
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Skip tenant resolution for super admin paths
        if request.path.startswith('/super-admin/'):
            request.tenant = None
            request.tenant_id = None
            return
        
        # Try to extract tenant from subdomain
        # Format: school_slug.domain.com or localhost
        parts = host.split('.')
        
        # First, try to get tenant from query param or header (works for all environments)
        tenant_id = request.GET.get('tenant_id') or request.headers.get('X-Tenant-ID')
        
        if tenant_id:
            # Tenant ID provided directly
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                request.tenant = tenant
                request.tenant_id = tenant.id
                return
            except Tenant.DoesNotExist:
                pass
        
        # Fallback: Try to extract tenant from subdomain
        if len(parts) >= 2 and parts[0] not in ['www', 'localhost', '127']:
            # It's a subdomain (e.g., school1.domain.com)
            tenant_slug = parts[0]
            try:
                tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
                request.tenant = tenant
                request.tenant_id = tenant.id
                return
            except Tenant.DoesNotExist:
                pass
        
        # No tenant found
        request.tenant = None
        request.tenant_id = None
    
    def process_response(self, request, response):
        return response
