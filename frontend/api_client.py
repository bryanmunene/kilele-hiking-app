"""Authenticated API calls with bounded waits and user-facing failures."""
import requests
import streamlit as st
from config import settings


def api_request(method: str, path: str, **kwargs) -> dict | list:
    headers = {}
    if st.session_state.get("session_token"):
        headers["X-Session-Token"] = st.session_state.session_token
    elif st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    try:
        response = requests.request(
            method, settings.API_BASE_URL.rstrip("/") + path,
            headers=headers, timeout=(10, 60), **kwargs,
        )
        try:
            data = response.json()
        except ValueError:
            return {"error": "The service is starting. Please try again shortly."}
        if not response.ok:
            detail = data.get("detail") or data.get("message")
            return {"error": detail if isinstance(detail, str) else "The request could not be completed."}
        return data
    except requests.RequestException:
        return {"error": "The service is taking longer than expected. Please try again shortly."}
