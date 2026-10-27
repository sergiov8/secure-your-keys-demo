"""Reads a secret at startup. Nothing is written to disk or to .env files.

    export GOOGLE_CLOUD_PROJECT=my-startup-prod
    python -m step3_secret_manager.read_secret stripe-live-key
"""

import argparse

from google.cloud import secretmanager

from common.config import load_settings


def secret_version_name(project: str, secret_id: str, version: str = "latest") -> str:
    return f"projects/{project}/secrets/{secret_id}/versions/{version}"


def read_secret(project: str, secret_id: str, version: str = "latest") -> str:
    client = secretmanager.SecretManagerServiceClient()
    resp = client.access_secret_version(
        name=secret_version_name(project, secret_id, version)
    )
    return resp.payload.data.decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a secret from Secret Manager.")
    parser.add_argument("secret_id")
    parser.add_argument("--version", default="latest")
    args = parser.parse_args()

    value = read_secret(load_settings().project, args.secret_id, args.version)
    # Prove it worked without printing the secret.
    print(f"Read {args.secret_id} ({len(value)} characters).")


if __name__ == "__main__":
    main()
