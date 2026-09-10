"""Supervise both processes; a failure exits the service so Render can restart it."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def main():
    port = int(os.getenv("PORT", "8000"))
    website_port = int(os.getenv("STREAMLIT_PORT", "8501"))
    host = urlparse(os.getenv("FRONTEND_URL", f"http://127.0.0.1:{port}")).hostname
    children = []
    def shutdown(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, shutdown)
    try:
        # Finish schema initialization before Streamlit can start a second migration.
        migration = subprocess.run([sys.executable, "-c", "from database import init_database; init_database()"], cwd=ROOT / "backend")
        if migration.returncode:
            return migration.returncode
        children.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "hosted:app",
            "--host", "0.0.0.0", "--port", str(port), "--ws-max-size", str(16 * 1024 * 1024)], cwd=ROOT / "backend"))
        env = {**os.environ, "API_BASE_URL": f"http://127.0.0.1:{port}"}
        children.append(subprocess.Popen([sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.address", "127.0.0.1", "--server.port", str(website_port),
            "--server.headless", "true", "--browser.gatherUsageStats", "false",
            "--server.fileWatcherType", "none", "--server.maxUploadSize", "10",
            "--browser.serverAddress", host, "--server.enableXsrfProtection", "true"],
            cwd=ROOT / "frontend", env=env))
        while all(child.poll() is None for child in children):
            time.sleep(1)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
