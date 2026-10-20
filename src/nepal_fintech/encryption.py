"""Fernet encryption helpers for securing user financial data at rest."""

from __future__ import annotations

from cryptography.fernet import Fernet

from .config import settings


def _get_fernet() -> Fernet:
    """Return a Fernet instance using the configured encryption key."""
    key = settings.encryption_key
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string and return the ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string and return the plaintext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()
