"""Tests for field-level encryption at rest."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken

from nepal_fintech.config import settings
from nepal_fintech.encryption import decrypt, encrypt, generate_key


def test_generate_key() -> None:
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) == 44  # Standard Fernet base64 key length


def test_encrypt_decrypt_roundtrip() -> None:
    plaintext = '{"salary": 2500000, "bank": "Nabil Bank"}'
    ciphertext = encrypt(plaintext)

    assert ciphertext != plaintext
    assert isinstance(ciphertext, str)

    decrypted = decrypt(ciphertext)
    assert decrypted == plaintext


def test_decrypt_invalid_ciphertext_fails() -> None:
    with pytest.raises(InvalidToken):
        decrypt("not-a-valid-ciphertext")


def test_different_encryptions_produce_different_ciphertexts() -> None:
    text = "sensitive_nepal_land_data"
    c1 = encrypt(text)
    c2 = encrypt(text)
    # Fernet includes an initialization vector and timestamp, so ciphertexts vary
    assert c1 != c2
    assert decrypt(c1) == text
    assert decrypt(c2) == text
