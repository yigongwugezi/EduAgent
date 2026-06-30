"""JWT authentication utilities — token creation, verification, password hashing."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any

# ── Secret key ────────────────────────────────────────────────────────────
_SECRET = os.environ.get("JWT_SECRET", "eduagent-dev-secret-change-in-production").encode()

# ── Token ─────────────────────────────────────────────────────────────────

def create_token(learner_id: str, role: str, ttl_seconds: int = 900) -> str:
    """Create a simple signed JWT-like token.

    Uses HMAC-SHA256 signing with a base64url-encoded header+payload.
    Avoids external JWT dependency — sufficient for this project's scale.
    """
    import base64

    now = int(time.time())
    header = _b64url_dict({"alg": "HS256", "typ": "JWT"})
    payload = _b64url_dict({
        "sub": learner_id,
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds,
    })
    signature = _b64url_bytes(_sign(f"{header}.{payload}"))
    return f"{header}.{payload}.{signature}"


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify token signature and expiry. Returns payload dict or None."""
    import base64
    import json

    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, sig_b64 = parts

    # Verify signature
    expected_sig = _b64url_bytes(_sign(f"{header_b64}.{payload_b64}"))
    if not hmac.compare_digest(sig_b64, expected_sig):
        return None

    # Decode payload
    try:
        payload = json.loads(base64.urlsafe_b64decode(_pad(payload_b64)))
    except Exception:
        return None

    # Check expiry
    if payload.get("exp", 0) < time.time():
        return None

    return payload


def create_refresh_token(learner_id: str, ttl_seconds: int = 604800) -> str:
    """Create a long-lived refresh token (default 7 days)."""
    return create_token(learner_id, "refresh", ttl_seconds)


# ── Password ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password with salt using PBKDF2-SHA256 (stdlib only, no bcrypt dependency)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2:sha256:600000:{salt.hex()}:{dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a PBKDF2 hash."""
    try:
        _, algo, iters, salt_hex, dk_hex = hashed.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
        dk = hashlib.pbkdf2_hmac(algo, password.encode(), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except (ValueError, AttributeError):
        return False


# ── Helpers ───────────────────────────────────────────────────────────────

def _sign(message: str) -> bytes:
    return hmac.digest(_SECRET, message.encode(), "sha256")


def _b64url_dict(data: dict) -> str:
    import base64
    import json
    return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()


def _b64url_bytes(raw: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _pad(b64: str) -> str:
    return b64 + "=" * (4 - len(b64) % 4)
