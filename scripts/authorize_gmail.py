"""Authorize only the owner's Gmail sender and write a local Render env file."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-json", type=Path, required=True)
    parser.add_argument("--sender", required=True)
    parser.add_argument("--output", type=Path, default=Path(".env.gmail.local"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists. Choose a new output path.")
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(args.client_json), scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    credentials = flow.run_local_server(
        port=0, access_type="offline", prompt="consent",
        authorization_prompt_message="Authorize the sender account in the browser.",
        success_message="Kilele mail authorization complete. You can close this tab.",
    )
    if not credentials.refresh_token:
        raise RuntimeError("Google did not issue a refresh token. Authorize again with offline access.")
    values = {
        "GMAIL_CLIENT_ID": credentials.client_id,
        "GMAIL_CLIENT_SECRET": credentials.client_secret,
        "GMAIL_REFRESH_TOKEN": credentials.refresh_token,
        "FROM_EMAIL": args.sender,
    }
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write("\n".join(f"{key}={json.dumps(value)}" for key, value in values.items()) + "\n")
    print(f"Private configuration written to {args.output.resolve()}. Import it into Render environment settings.")


if __name__ == "__main__":
    main()
