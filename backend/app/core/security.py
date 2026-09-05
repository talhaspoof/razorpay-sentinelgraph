import hmac
import hashlib
from app.core.config import settings

def verify_razorpay_signature(raw_body: bytes, signature_header: str, secret: str = None) -> bool:
    """
    Verifies the HMAC-SHA256 signature sent in the 'X-Razorpay-Signature' header.
    Returns True if valid, False otherwise.
    """
    if not signature_header:
        return False
        
    secret_key = secret or settings.RAZORPAY_WEBHOOK_SECRET
    computed_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature_header)
