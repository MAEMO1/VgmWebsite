#!/usr/bin/env python3
"""
Test script for email service configuration
"""

import os
import sys
from services.email_service import send_password_reset_email, send_email

def test_email_config():
    """Test email configuration"""
    print("Testing email configuration...")
    
    # Check environment variables
    required_vars = ['SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_SENDER']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test email sending (only if SMTP is configured)
    test_email = os.getenv('TEST_EMAIL')
    if test_email:
        print(f"Testing email sending to {test_email}...")
        
        # Test basic email
        success = send_email(
            subject="VGM Email Test",
            to_email=test_email,
            body="This is a test email from VGM Website to verify email configuration."
        )
        
        if success:
            print("✅ Test email sent successfully")
        else:
            print("❌ Failed to send test email")
            return False
        
        # Test password reset email
        reset_url = "http://localhost:3000/nl/forgot-password?token=test-token"
        success = send_password_reset_email(test_email, reset_url, 'nl')
        
        if success:
            print("✅ Password reset email sent successfully")
        else:
            print("❌ Failed to send password reset email")
            return False
    else:
        print("ℹ️  Set TEST_EMAIL environment variable to test actual email sending")
    
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_email_config()
    sys.exit(0 if success else 1)
