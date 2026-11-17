"""AES-256-GCM encrypt/decrypt for users' stored AI keys.

Format: base64(iv[12 bytes] || ciphertext || tag[16 bytes]) — this matches
what the Web Crypto API's `crypto.subtle.encrypt({name: "AES-GCM"}, ...)`
produces in the `save-llm-key` Deno Edge Function, so a value written by
the Edge Function can be decrypted here, and vice versa.

COOKIE_ENCRYPTION_KEY is a base64-encoded 32-byte key (generate with
`openssl rand -base64 32`). Only the service role (this code, run inside
GitHub Actions) ever sees the decryption key or the plaintext.
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import settings

IV_LENGTH = 12


def _get_key() -> bytes:
    if not settings.COOKIE_ENCRYPTION_KEY:
        raise RuntimeError("COOKIE_ENCRYPTION_KEY not set")
    key = base64.b64decode(settings.COOKIE_ENCRYPTION_KEY)
    if len(key) != 32:
        raise RuntimeError("COOKIE_ENCRYPTION_KEY must decode to 32 bytes for AES-256")
    return key


V2_PREFIX = "v2:"


def encrypt_cookie(plaintext: str, aad: str | None = None) -> str:
    """With `aad` (the owner's user id) the value is bound to that user and cannot be
    copied to another row. Output is then "v2:" + base64; without it, the legacy format."""
    key = _get_key()
    iv = os.urandom(IV_LENGTH)
    ciphertext = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), aad.encode() if aad else None)
    body = base64.b64encode(iv + ciphertext).decode("ascii")
    return V2_PREFIX + body if aad else body


def is_legacy(token: str) -> bool:
    return not token.startswith(V2_PREFIX)


def decrypt_cookie(token: str, aad: str | None = None) -> str:
    """v2 values require the matching `aad`; legacy (unprefixed) values are still readable."""
    key = _get_key()
    if token.startswith(V2_PREFIX):
        if not aad:
            raise ValueError("aad is required for v2 values")
        raw = base64.b64decode(token[len(V2_PREFIX):])
        associated = aad.encode()
    else:
        raw = base64.b64decode(token)
        associated = None
    iv, ciphertext = raw[:IV_LENGTH], raw[IV_LENGTH:]
    return AESGCM(key).decrypt(iv, ciphertext, associated).decode("utf-8")
