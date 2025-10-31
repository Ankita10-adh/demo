import hashlib
import hmac
import base64

def generate_esewa_signature(data_dict, secret_key):
    """
    Generate HMAC SHA256 signature for eSewa payment.
    """
    signed_data = []
    for key in data_dict['signed_field_names'].split(','):
        signed_data.append(f"{key}={data_dict.get(key,'')}")
    message = ','.join(signed_data)
    
    digest = hmac.new(
        secret_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    signature = base64.b64encode(digest).decode()
    return signature
