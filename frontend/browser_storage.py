"""Small Streamlit v2 component for safe browser-local persistence."""

import hashlib

import streamlit as st


_STORAGE_JS = """
export default function(component) {
    const { data, setStateValue } = component;
    const storageKey = data.key;

    try {
        if (data.action === "set") {
            localStorage.setItem(storageKey, data.value);
        } else if (data.action === "remove") {
            localStorage.removeItem(storageKey);
        } else if (data.action === "get") {
            setStateValue("value", localStorage.getItem(storageKey) || "");
        }
    } catch (error) {
        if (data.action === "get") {
            setStateValue("value", "");
        }
    }
}
"""

_browser_storage = st.components.v2.component(
    "kilele_browser_storage",
    js=_STORAGE_JS,
)


def _instance_key(action: str, key: str, instance: str = "") -> str:
    digest = hashlib.sha256(f"{key}:{instance}".encode("utf-8")).hexdigest()[:12]
    return f"kilele_storage_{action}_{digest}"


def _no_op() -> None:
    """State-change callback required by Streamlit component state."""


def save_to_browser(key: str, value: str) -> None:
    """Save a string to localStorage."""
    _browser_storage(
        key=_instance_key("set", key),
        data={"action": "set", "key": key, "value": value},
        height=0,
    )


def load_from_browser(key: str, instance: str = "") -> str | None:
    """Load a string from localStorage after the component's first rerun."""
    result = _browser_storage(
        key=_instance_key("get", key, instance),
        data={"action": "get", "key": key},
        default={"value": None},
        height=0,
        on_value_change=_no_op,
    )
    return result.value


def clear_from_browser(key: str) -> None:
    """Remove a localStorage value."""
    _browser_storage(
        key=_instance_key("remove", key),
        data={"action": "remove", "key": key},
        height=0,
    )


def save_token_to_browser(token: str) -> None:
    save_to_browser("kilele_session_token", token)


def load_token_from_browser() -> str | None:
    return load_from_browser("kilele_session_token")


def clear_token_from_browser() -> None:
    clear_from_browser("kilele_session_token")


def restore_session_from_browser() -> None:
    """Place a remembered token into session state when available."""
    if st.session_state.get("authenticated"):
        return

    token = load_token_from_browser()
    if token:
        st.session_state.session_token = token
