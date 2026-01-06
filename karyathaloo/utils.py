import hashlib
import uuid
from decimal import Decimal

def generate_tx_code():
    """Generates a unique transaction code."""
    return str(uuid.uuid4()).replace('-', '')

def generate_esewa_checksum(tx_code: str, amount: Decimal, scd: str) -> str:
    """
    Generates the MD5 checksum required by eSewa for payment initiation.
    The sequence is: txCode + amount + scd
    
    Args:
        tx_code: The unique transaction code (oid).
        amount: The payment amount (amt).
        scd: The merchant code (scd).
    
    Returns:
        The hex digest of the MD5 hash.
    """
    # Ensure amount is converted to a string format eSewa expects
    amount_str = str(amount.quantize(Decimal('0.00')))
    
    data_to_hash = f"{tx_code}{amount_str}{scd}"
    
    # Generate MD5 hash
    checksum = hashlib.md5(data_to_hash.encode('utf-8')).hexdigest()
    return checksum

import random
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import EmailOTP

def send_otp(user):
    otp_code = str(random.randint(100000, 999999))  # 6-digit OTP
    expiry = datetime.now() + timedelta(minutes=10)  # valid for 10 mins

    # Save OTP
    EmailOTP.objects.create(user=user, otp=otp_code, expires_at=expiry)

    # Send email
    send_mail(
        subject='Your OTP for Karyathalo',
        message=f'Your OTP is {otp_code}. It will expire in 10 minutes.',
        from_email='karyathalo227@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

import hmac
import hashlib
import base64

def generate_esewa_signature(amount, tx_uuid, product_code="EPAYTEST"):
    # Updated Sandbox Secret Key
    secret_key = "8gBm/:&EnhH.1/q" 
    
    # Ensure total_amount is a string with no hidden spaces
    # Example: "total_amount=100,transaction_uuid=ABC-123,product_code=EPAYTEST"
    message = f"total_amount={amount},transaction_uuid={tx_uuid},product_code={product_code}"
    
    key = bytes(secret_key, 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    
    # Generate HMAC-SHA256
    hash_hmac = hmac.new(key, message_bytes, hashlib.sha256).digest()
    
    # Return as Base64 string
    return base64.b64encode(hash_hmac).decode("utf-8")