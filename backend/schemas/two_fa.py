from pydantic import BaseModel

class TwoFASetupRequest(BaseModel):
    """Request to enable 2FA"""
    password: str  # User must confirm with password

class TwoFASetupResponse(BaseModel):
    """Response with QR code data for 2FA setup"""
    secret: str
    qr_code_url: str
    manual_entry_key: str

class TwoFAVerifyRequest(BaseModel):
    """Request to verify 2FA token"""
    token: str

class TwoFALoginRequest(BaseModel):
    """Login with 2FA token"""
    username: str
    password: str
    two_fa_token: str

class TwoFADisableRequest(BaseModel):
    """Request to disable 2FA"""
    password: str
    two_fa_token: str
