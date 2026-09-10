"""Authorized one-time setup. Secrets never appear in stdout or git-tracked files."""
import base64
import subprocess
from pathlib import Path
import requests
from cryptography.fernet import Fernet
from dotenv import dotenv_values
from nacl.public import PublicKey, SealedBox

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "bryanmunene/kilele-hiking-app"


def github_session():
    import os
    process = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\nusername=bryanmunene\n\n",
        text=True, capture_output=True, cwd=ROOT, timeout=120,
        env={**os.environ, "GCM_INTERACTIVE": "never", "GIT_TERMINAL_PROMPT": "0"})
    credential = dict(line.split("=", 1) for line in process.stdout.splitlines() if "=" in line)
    token = credential.get("password")
    if not token:
        raise RuntimeError("GitHub sign-in is required.")
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"})
    return session


def configure():
    values = dotenv_values(ROOT / ".env.local")
    database_url = values.get("DATABASE_URL_UNPOOLED") or values.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Local Neon connection configuration is missing.")
    session = github_session()
    base = f"https://api.github.com/repos/{REPOSITORY}/actions/secrets"
    response = session.get(base + "/public-key", timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"GitHub secret access unavailable ({response.status_code}).")
    public_key = response.json()
    key_file = ROOT / ".env.backup.local"
    existing = session.get(base + "/BACKUP_ENCRYPTION_KEY", timeout=30)
    if existing.status_code == 200 and not key_file.exists():
        raise RuntimeError("A backup key already exists on GitHub. Recover it instead of rotating it.")
    if not key_file.exists():
        key_file.write_text("BACKUP_ENCRYPTION_KEY=" + Fernet.generate_key().decode() + "\n", encoding="ascii")
    encryption_key = dotenv_values(key_file)["BACKUP_ENCRYPTION_KEY"]
    box = SealedBox(PublicKey(base64.b64decode(public_key["key"])))
    for name, value in {"BACKUP_DATABASE_URL": database_url, "BACKUP_ENCRYPTION_KEY": encryption_key}.items():
        encrypted = base64.b64encode(box.encrypt(value.encode())).decode()
        response = session.put(base + "/" + name, json={"key_id": public_key["key_id"], "encrypted_value": encrypted}, timeout=30)
        if response.status_code not in {201, 204}:
            raise RuntimeError(f"Could not configure {name} ({response.status_code}).")
        print(name + " configured securely.")


if __name__ == "__main__":
    try:
        configure()
    except Exception as exc:
        print(f"Backup secret setup failed ({type(exc).__name__}). Check GitHub authorization and local configuration.")
        raise SystemExit(1)
