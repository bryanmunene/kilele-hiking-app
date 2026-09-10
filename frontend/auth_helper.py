"""Legacy callers use the verified session-token implementation."""
from auth import restore_session_from_storage, save_token_to_browser, logout


def restore_auth():
    return restore_session_from_storage()


def save_auth(token, user=None):
    return save_token_to_browser(token)


def clear_auth():
    return logout()
