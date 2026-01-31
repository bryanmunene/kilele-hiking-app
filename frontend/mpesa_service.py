"""
M-Pesa Integration Service for Kilele Hiking App
Uses Safaricom Daraja API for STK Push payments
"""
import requests
import base64
from datetime import datetime
import os

# M-Pesa API Configuration (Sandbox for testing)
MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # sandbox or production
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")  # Paybill/Till number
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")  # Lipa Na M-Pesa Online Passkey
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://kilele-hiking-app.streamlit.app/mpesa/callback")

# API URLs
if MPESA_ENVIRONMENT == "production":
    AUTH_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    QUERY_URL = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
else:
    AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    QUERY_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"


def get_mpesa_access_token():
    """Generate M-Pesa access token"""
    try:
        # Create base64 encoded credentials
        credentials = f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded}"
        }
        
        response = requests.get(AUTH_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json().get("access_token")
    except Exception as e:
        print(f"M-Pesa auth error: {e}")
        return None


def generate_password(shortcode: str, passkey: str, timestamp: str):
    """Generate M-Pesa password"""
    data_to_encode = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(data_to_encode.encode()).decode()


def initiate_stk_push(phone_number: str, amount: float, account_reference: str, transaction_desc: str):
    """
    Initiate STK Push for M-Pesa payment
    
    Args:
        phone_number: Customer phone number (format: 2547XXXXXXXX)
        amount: Amount to charge (minimum 1 KES)
        account_reference: Reference for the payment (e.g., "HIKE-123")
        transaction_desc: Description of transaction
    
    Returns:
        dict: Response with checkout_request_id, merchant_request_id, or error
    """
    # Validate M-Pesa configuration
    if not all([MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY]):
        return {
            "success": False,
            "error": "M-Pesa not configured. Using demo mode.",
            "demo_mode": True
        }
    
    # Format phone number (remove + and spaces, ensure starts with 254)
    phone_number = phone_number.replace("+", "").replace(" ", "")
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]
    elif phone_number.startswith("7") or phone_number.startswith("1"):
        phone_number = "254" + phone_number
    
    # Validate phone number format
    if not phone_number.startswith("254") or len(phone_number) != 12:
        return {
            "success": False,
            "error": "Invalid phone number format. Use 254XXXXXXXXX"
        }
    
    # Get access token
    access_token = get_mpesa_access_token()
    if not access_token:
        return {
            "success": False,
            "error": "Failed to authenticate with M-Pesa"
        }
    
    # Generate timestamp and password
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = generate_password(MPESA_SHORTCODE, MPESA_PASSKEY, timestamp)
    
    # Prepare STK Push request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",  # or CustomerBuyGoodsOnline for Till
        "Amount": int(amount),  # Must be integer
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    
    try:
        response = requests.post(STK_PUSH_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("ResponseCode") == "0":
            return {
                "success": True,
                "checkout_request_id": result.get("CheckoutRequestID"),
                "merchant_request_id": result.get("MerchantRequestID"),
                "response_description": result.get("ResponseDescription"),
                "customer_message": result.get("CustomerMessage")
            }
        else:
            return {
                "success": False,
                "error": result.get("ResponseDescription", "STK Push failed")
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"M-Pesa API error: {str(e)}"
        }


def query_stk_push_status(checkout_request_id: str):
    """
    Query the status of an STK Push transaction
    
    Args:
        checkout_request_id: The CheckoutRequestID from STK Push
    
    Returns:
        dict: Payment status information
    """
    access_token = get_mpesa_access_token()
    if not access_token:
        return {
            "success": False,
            "error": "Failed to authenticate with M-Pesa"
        }
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = generate_password(MPESA_SHORTCODE, MPESA_PASSKEY, timestamp)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }
    
    try:
        response = requests.post(QUERY_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "result_code": result.get("ResultCode"),
            "result_desc": result.get("ResultDesc"),
            "data": result
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Query error: {str(e)}"
        }


def format_phone_number_display(phone: str):
    """Format phone number for display (e.g., +254 712 345 678)"""
    phone = phone.replace("+", "").replace(" ", "")
    if phone.startswith("254") and len(phone) == 12:
        return f"+254 {phone[3:6]} {phone[6:9]} {phone[9:]}"
    return phone


def validate_mpesa_amount(amount: float):
    """Validate M-Pesa payment amount (min 1 KES)"""
    if amount < 1:
        return False, "Minimum amount is KES 1"
    if amount > 150000:
        return False, "Maximum amount is KES 150,000"
    return True, ""
