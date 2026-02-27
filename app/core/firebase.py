import json
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.config import settings


def _get_firebase_credentials():
    """
    Resolve Firebase credentials from either:
    - FIREBASE_SERVICE_ACCOUNT_JSON: raw JSON string (e.g. from GitHub Secrets), or
    - FIREBASE_SERVICE_ACCOUNT_PATH: path to service account JSON file.
    """
    json_str = (settings.FIREBASE_SERVICE_ACCOUNT_JSON or "").strip()
    if json_str:
        try:
            return credentials.Certificate(json.loads(json_str))
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON is set but not valid JSON. "
                "Use the full contents of your Firebase service account JSON file."
            ) from e

    path = (settings.FIREBASE_SERVICE_ACCOUNT_PATH or "").strip()
    if path and os.path.exists(path):
        return credentials.Certificate(path)

    raise RuntimeError(
        "Firebase credentials not configured. Set either FIREBASE_SERVICE_ACCOUNT_JSON "
        "(full JSON string, e.g. from GitHub Secrets) or FIREBASE_SERVICE_ACCOUNT_PATH "
        "(path to service account JSON file) in config or environment."
    )


def _initialize_firebase_app():
    """
    Initialize the Firebase Admin app once per process.
    """
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred = _get_firebase_credentials()

    options = {}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    return firebase_admin.initialize_app(cred, options or None)


def verify_firebase_id_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded payload.

    Raises ValueError if the token is invalid or verification fails.
    """
    try:
        _initialize_firebase_app()
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as exc:  # noqa: BLE001 - bubble up as ValueError for the API layer
        raise ValueError("Invalid Firebase ID token") from exc

