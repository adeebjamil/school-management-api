from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone
from .models import User, SuperAdminSession, TenantAdminCreationLog, AuditLog, PasswordResetOTP
from tenants.models import Tenant
from .serializers import (
    LoginSerializer, SuperAdminLoginSerializer, UserSerializer,
    CreateTenantAdminSerializer, SuperAdminSessionSerializer,
    TenantAdminCreationLogSerializer, AuditLogSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer
)
from .email_utils import send_otp_email, send_password_reset_success_email


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(user, action, model_name, description, request, tenant=None, object_id=None):
    """Helper function to create audit logs"""
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        description=description,
        ip_address=get_client_ip(request),
        tenant=tenant
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def super_admin_login(request):
    """Super Admin login with hardcoded credentials"""
    serializer = SuperAdminLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    # Check against hardcoded credentials from settings
    if email != settings.SUPER_ADMIN_EMAIL or password != settings.SUPER_ADMIN_PASSWORD:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get or create super admin user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
    
    # Create session record
    session = SuperAdminSession.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Create audit log
    create_audit_log(user, 'login', 'SuperAdminSession', 'Super Admin logged in', request)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'session_id': str(session.id)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def tenant_login(request):
    """Login for Tenant Admin, Students, Teachers, Parents"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    
    # Verify tenant context
    tenant_id = getattr(request, 'tenant_id', None)
    if user.role != 'super_admin' and (not tenant_id or str(user.tenant_id) != str(tenant_id)):
        return Response({'error': 'Invalid tenant context'}, status=status.HTTP_403_FORBIDDEN)
    
    # Create audit log
    create_audit_log(user, 'login', 'User', f'{user.role} logged in', request, tenant=user.tenant)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['tenant_id'] = str(user.tenant_id) if user.tenant_id else None
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user"""
    user = request.user
    
    # If super admin, mark session as inactive
    if user.role == 'super_admin':
        SuperAdminSession.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logout_time=timezone.now()
        )
    
    # Create audit log
    create_audit_log(user, 'logout', 'User', f'{user.role} logged out', request, tenant=user.tenant)
    
    return Response({'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tenant_admin(request):
    """Super Admin creates a Tenant Admin"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Only Super Admin can create Tenant Admins'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateTenantAdminSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify tenant exists
    try:
        tenant = Tenant.objects.get(id=serializer.validated_data['tenant_id'])
    except Tenant.DoesNotExist:
        return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if email already exists
    if User.objects.filter(email=serializer.validated_data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create tenant admin user
    tenant_admin = User.objects.create_user(
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password'],
        first_name=serializer.validated_data['first_name'],
        last_name=serializer.validated_data['last_name'],
        phone=serializer.validated_data.get('phone', ''),
        role='tenant_admin',
        tenant=tenant
    )
    
    # Create log entry
    TenantAdminCreationLog.objects.create(
        super_admin=request.user,
        tenant_admin=tenant_admin,
        tenant=tenant,
        ip_address=get_client_ip(request)
    )
    
    # Create audit log
    create_audit_log(
        request.user, 'create', 'User', 
        f'Created Tenant Admin for {tenant.name}',
        request, object_id=tenant_admin.id
    )
    
    return Response({
        'message': 'Tenant Admin created successfully',
        'user': UserSerializer(tenant_admin).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get or update current user profile"""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    
    elif request.method == 'PUT':
        user = request.user
        data = request.data
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        user.save()
        
        # Create audit log
        create_audit_log(user, 'update', 'User', 'Updated profile', request, tenant=user.tenant)
        
        return Response(UserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_sessions(request):
    """Get Super Admin sessions (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    sessions = SuperAdminSession.objects.all()[:50]
    return Response(SuperAdminSessionSerializer(sessions, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_admin_logs(request):
    """Get Tenant Admin creation logs (Super Admin only)"""
    if request.user.role != 'super_admin':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    logs = TenantAdminCreationLog.objects.all()[:50]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    old_password = serializer.validated_data['old_password']
    new_password = serializer.validated_data['new_password']
    
    # Check if old password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate new password
    try:
        from django.contrib.auth.password_validation import validate_password
        validate_password(new_password, user)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    # Create audit log
    create_audit_log(user, 'update', 'User', 'Changed password', request, tenant=user.tenant)
    
    return Response({'message': 'Password changed successfully'})
    return Response(TenantAdminCreationLogSerializer(logs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs(request):
    """Get audit logs"""
    user = request.user
    
    if user.role == 'super_admin':
        # Super admin can see all logs
        logs = AuditLog.objects.all()[:100]
    elif user.role == 'tenant_admin':
        # Tenant admin can see their tenant's logs
        logs = AuditLog.objects.filter(tenant=user.tenant)[:100]
    else:
        # Others can only see their own logs
        logs = AuditLog.objects.filter(user=user)[:50]
    
    return Response(AuditLogSerializer(logs, many=True).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send OTP to user's email for password reset"""
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email, is_active=True)
        
        # Generate OTP
        otp_code = PasswordResetOTP.generate_otp()
        
        # Invalidate any existing unused OTPs for this email
        PasswordResetOTP.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Create new OTP
        otp_obj = PasswordResetOTP.objects.create(
            email=email,
            otp=otp_code,
            ip_address=get_client_ip(request)
        )
        
        # Send email
        email_sent = send_otp_email(email, otp_code, user.first_name)
        
        if not email_sent:
            return Response(
                {'error': 'Failed to send OTP email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'OTP sent successfully to your email',
            'expires_in_minutes': settings.OTP_EXPIRY_MINUTES
        })
        
    except User.DoesNotExist:
        # For security, return same message even if user doesn't exist
        return Response({
            'message': 'If the email exists, an OTP has been sent'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP code"""
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    
    try:
        # Find the OTP
        otp_obj = PasswordResetOTP.objects.filter(
            email=email,
            otp=otp_code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response(
                {'error': 'Invalid OTP code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP is still valid
        if not otp_obj.is_valid():
            return Response(
                {'error': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': 'OTP verified successfully',
            'verified': True
        })
        
    except Exception as e:
        return Response(
            {'error': 'Error verifying OTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using verified OTP"""
    serializer = ResetPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    try:
        # Verify user exists
        user = User.objects.get(email=email, is_active=True)
        
        # Find and verify OTP
        otp_obj = PasswordResetOTP.objects.filter(
            email=email,
            otp=otp_code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response(
                {'error': 'Invalid OTP code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP is still valid
        if not otp_obj.is_valid():
            return Response(
                {'error': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Create audit log
        create_audit_log(
            user, 'update', 'User',
            'Password reset via OTP',
            request,
            tenant=user.tenant
        )
        
        # Send confirmation email
        send_password_reset_success_email(email, user.first_name)
        
        return Response({
            'message': 'Password reset successfully. You can now login with your new password.'
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Error resetting password'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

