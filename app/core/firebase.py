import base64
import json
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.config import settings


def _get_firebase_credentials():
    """
    Resolve Firebase credentials from (in order):
    - FIREBASE_SERVICE_ACCOUNT_B64: base64-encoded JSON (safe for .env / GitHub Secrets), or
    - FIREBASE_SERVICE_ACCOUNT_JSON: raw JSON string, or
    - FIREBASE_SERVICE_ACCOUNT_PATH: path to service account JSON file.
    """
    b64 = (settings.FIREBASE_SERVICE_ACCOUNT_B64 or "").strip().replace("\n", "").replace("\r", "")
    if b64:
        try:
            raw = base64.b64decode(b64).decode("utf-8")
            return credentials.Certificate(json.loads(raw))
        except (ValueError, json.JSONDecodeError) as e:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_B64 is set but not valid base64/JSON."
            ) from e

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
        "Firebase credentials not configured. Set one of: FIREBASE_SERVICE_ACCOUNT_B64 "
        "(base64-encoded JSON), FIREBASE_SERVICE_ACCOUNT_JSON (raw JSON), or "
        "FIREBASE_SERVICE_ACCOUNT_PATH (path to JSON file) in config or environment."
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


def get_firebase_status() -> dict:
    """
    Return status for debugging: which credential source is set and if config is valid.
    Does not expose secret values.
    """
    from app.core.config import settings

    b64 = (settings.FIREBASE_SERVICE_ACCOUNT_B64 or "").strip()
    json_str = (settings.FIREBASE_SERVICE_ACCOUNT_JSON or "").strip()
    path = (settings.FIREBASE_SERVICE_ACCOUNT_PATH or "").strip()

    status = {
        "firebase_configured": False,
        "has_b64": bool(b64),
        "has_json": bool(json_str),
        "has_path": bool(path),
        "path_exists": path and os.path.exists(path),
    }

    try:
        _get_firebase_credentials()
        status["firebase_configured"] = True
    except RuntimeError as e:
        status["credential_error"] = "invalid" if (b64 or json_str or (path and os.path.exists(path))) else "missing"

    return status


def is_firebase_configured() -> bool:
    """Return True if Firebase credentials are available (for status checks)."""
    return get_firebase_status()["firebase_configured"]


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

