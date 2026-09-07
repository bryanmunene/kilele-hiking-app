"""Ping the free deployment often enough to avoid manual wakeups."""
from __future__ import annotations

import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


DEFAULT_FRONTEND_URL = "https://kilele-hiking-appgit-cnrnmlnmkgku6xjzrrxzcg.streamlit.app/"
DEFAULT_BACKEND_HEALTH_URL = "https://kilele-hiking-api.onrender.com/health"
USER_AGENT = "KileleKeepAwake/1.0 (+https://github.com/bryanmunene/kilele-hiking-app)"
SLEEPING_OR_ERROR_MARKERS = (
    "this app has gone to sleep",
    "yes, get this app back up",
    "error running your app",
    "this app has gone over its resource limits",
)


@dataclass(frozen=True)
class Endpoint:
    name: str
    url: str


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Unsupported URL: {url}")
    return url


def _streamlit_health_url(frontend_url: str) -> str:
    return frontend_url.rstrip("/") + "/_stcore/health"


def configured_endpoints() -> list[Endpoint]:
    frontend_url = _normalize_url(os.getenv("KILELE_FRONTEND_URL", DEFAULT_FRONTEND_URL))
    backend_url = _normalize_url(os.getenv("KILELE_BACKEND_HEALTH_URL", DEFAULT_BACKEND_HEALTH_URL))
    endpoints = [
        Endpoint("Streamlit app", frontend_url),
        Endpoint("Streamlit health", _streamlit_health_url(frontend_url)),
        Endpoint("Render backend health", backend_url),
    ]

    extra_urls = os.getenv("KEEP_AWAKE_EXTRA_URLS", "")
    for index, raw_url in enumerate(extra_urls.replace("\n", ",").split(","), start=1):
        url = _normalize_url(raw_url)
        if url:
            endpoints.append(Endpoint(f"Extra endpoint {index}", url))

    return endpoints


def fetch_url(url: str, timeout: int) -> tuple[int | None, str, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "Cache-Control": "no-cache",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(256_000).decode("utf-8", errors="ignore")
            return response.status, body, None
    except urllib.error.HTTPError as exc:
        body = exc.read(256_000).decode("utf-8", errors="ignore")
        return exc.code, body, str(exc)
    except urllib.error.URLError as exc:
        return None, "", str(exc)
    except TimeoutError as exc:
        return None, "", str(exc)


def response_is_healthy(status_code: int | None, body: str) -> bool:
    if status_code is None or status_code < 200 or status_code >= 400:
        return False
    lowered = body.lower()
    return not any(marker in lowered for marker in SLEEPING_OR_ERROR_MARKERS)


def check_endpoint(endpoint: Endpoint, attempts: int = 3, timeout: int = 60, delay: int = 20) -> bool:
    for attempt in range(1, attempts + 1):
        status_code, body, error = fetch_url(endpoint.url, timeout)
        if response_is_healthy(status_code, body):
            print(f"[OK] {endpoint.name}: HTTP {status_code}")
            return True

        message = f"[WARN] {endpoint.name}: attempt {attempt}/{attempts}"
        if status_code is not None:
            message += f" returned HTTP {status_code}"
        if error:
            message += f" ({error})"
        print(message)

        if attempt < attempts:
            time.sleep(delay)

    return False


def main() -> int:
    failures = []
    for endpoint in configured_endpoints():
        if not check_endpoint(endpoint):
            failures.append(endpoint.name)

    if failures:
        print(f"[FAIL] Unhealthy endpoints: {', '.join(failures)}")
        return 1

    print("[OK] All keep-awake endpoints responded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
