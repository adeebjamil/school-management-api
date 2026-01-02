from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_otp_email(email, otp, user_name=None):
    """
    Send OTP email to user for password reset
    """
    subject = f'Password Reset OTP - {settings.APP_NAME}'
    
    # Create message
    message = f"""
Hello{f' {user_name}' if user_name else ''},

You have requested to reset your password for {settings.APP_NAME}.

Your OTP (One-Time Password) is: {otp}

This OTP is valid for {settings.OTP_EXPIRY_MINUTES} minutes.

If you did not request this password reset, please ignore this email.

Thank you,
{settings.APP_NAME} Team
    """
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #4F46E5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .otp-box {{
            background-color: #EEF2FF;
            border: 2px solid #4F46E5;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}
        .otp-code {{
            font-size: 32px;
            font-weight: bold;
            color: #4F46E5;
            letter-spacing: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }}
        .warning {{
            background-color: #FEF3C7;
            border-left: 4px solid #F59E0B;
            padding: 10px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.APP_NAME}</h1>
            <p>Password Reset Request</p>
        </div>
        <div class="content">
            <h2>Hello{f' {user_name}' if user_name else ''},</h2>
            <p>You have requested to reset your password. Please use the OTP below to complete the password reset process.</p>
            
            <div class="otp-box">
                <p style="margin: 0; font-size: 14px; color: #666;">Your OTP Code</p>
                <div class="otp-code">{otp}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">Valid for {settings.OTP_EXPIRY_MINUTES} minutes</p>
            </div>
            
            <div class="warning">
                <strong>Security Notice:</strong> If you did not request this password reset, please ignore this email. Your account is secure.
            </div>
            
            <p>Thank you,<br>{settings.APP_NAME} Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply to this email.</p>
            <p>&copy; {settings.APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False


def send_password_reset_success_email(email, user_name=None):
    """
    Send confirmation email after successful password reset
    """
    subject = f'Password Reset Successful - {settings.APP_NAME}'
    
    message = f"""
Hello{f' {user_name}' if user_name else ''},

Your password has been successfully reset for {settings.APP_NAME}.

If you did not make this change, please contact support immediately.

Thank you,
{settings.APP_NAME} Team
    """
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #10B981;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .success-icon {{
            text-align: center;
            font-size: 48px;
            color: #10B981;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }}
        .warning {{
            background-color: #FEF3C7;
            border-left: 4px solid #F59E0B;
            padding: 10px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.APP_NAME}</h1>
            <p>Password Reset Confirmation</p>
        </div>
        <div class="content">
            <div class="success-icon">✓</div>
            <h2>Hello{f' {user_name}' if user_name else ''},</h2>
            <p>Your password has been successfully reset.</p>
            <p>You can now login with your new password.</p>
            
            <div class="warning">
                <strong>Security Alert:</strong> If you did not make this change, please contact support immediately.
            </div>
            
            <p>Thank you,<br>{settings.APP_NAME} Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply to this email.</p>
            <p>&copy; {settings.APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset success email: {str(e)}")
        return False
