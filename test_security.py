import json
import re

import pytest
from cryptography.fernet import Fernet

from security import (
    GCM_MAGIC_HEADER,
    _derive_fernet_key,
    decrypt_project,
    encrypt_project,
)


def test_encrypt_decrypt_gcm_success():
    data = {"title": "Test Project", "elements": [1, 2, 3]}
    password = "SecretPassword123!"

    encrypted = encrypt_project(data, password)
    assert isinstance(encrypted, bytes)
    assert encrypted.startswith(GCM_MAGIC_HEADER)
    assert len(encrypted) > len(GCM_MAGIC_HEADER) + 16 + 12 + 16

    decrypted = decrypt_project(encrypted, password)
    assert decrypted == data


def test_decrypt_legacy_fernet_compatibility():
    data = {"title": "Legacy Project", "version": "1.0"}
    password = "LegacyPassword999!"
    import secrets

    salt = secrets.token_bytes(16)
    key = _derive_fernet_key(password, salt)
    fernet = Fernet(key)
    legacy_encrypted = salt + fernet.encrypt(json.dumps(data).encode("utf-8"))

    # Muss ohne GCM Header erfolgreich via Fernet entschlüsselt werden
    decrypted = decrypt_project(legacy_encrypted, password)
    assert decrypted == data


def test_decrypt_invalid_password():
    data = {"title": "Test Project"}
    encrypted = encrypt_project(data, "CorrectPassword")

    with pytest.raises(ValueError, match=re.escape("Falsches Passwort oder beschädigte Datei.")):
        decrypt_project(encrypted, "WrongPassword")


def test_decrypt_tampered_ciphertext_integrity():
    data = {"title": "Sensitive Data", "content": "Confidential"}
    password = "SafePassword456!"
    encrypted = bytearray(encrypt_project(data, password))

    # Letztes Byte im GCM Auth-Tag manipulieren
    encrypted[-1] ^= 0x01

    with pytest.raises(ValueError, match=re.escape("Falsches Passwort oder beschädigte Datei.")):
        decrypt_project(bytes(encrypted), password)


def test_decrypt_too_short_content():
    with pytest.raises(ValueError, match=re.escape("Die Datei ist zu klein, um gültig zu sein.")):
        decrypt_project(b"short", "password")

    with pytest.raises(ValueError, match=re.escape("Die Datei ist zu klein, um gültig zu sein.")):
        decrypt_project(GCM_MAGIC_HEADER + b"short", "password")


def test_decrypt_corrupted_json(monkeypatch):
    data = {"test": 123}
    encrypted = encrypt_project(data, "pass")

    # Mock AESGCM decrypt to return non-json bytes
    monkeypatch.setattr(
        "cryptography.hazmat.primitives.ciphers.aead.AESGCM.decrypt",
        lambda self, nonce, data, associated_data: b"not a valid json string \x80\x81",
    )

    with pytest.raises(ValueError, match=re.escape("Entschlüsselte Daten sind kein gültiges JSON-Format.")):
        decrypt_project(encrypted, "pass")


def test_decrypt_legacy_fernet_wrong_password():
    import secrets

    salt = secrets.token_bytes(16)
    key = _derive_fernet_key("CorrectPassword", salt)
    fernet = Fernet(key)
    legacy_encrypted = salt + fernet.encrypt(b'{"test": 123}')

    with pytest.raises(ValueError, match=re.escape("Falsches Passwort oder beschädigte Datei.")):
        decrypt_project(legacy_encrypted, "WrongPassword")


def test_decrypt_legacy_fernet_corrupted_json():
    import secrets

    salt = secrets.token_bytes(16)
    key = _derive_fernet_key("password", salt)
    fernet = Fernet(key)
    legacy_encrypted = salt + fernet.encrypt(b"not a valid json")

    with pytest.raises(ValueError, match=re.escape("Entschlüsselte Daten sind kein gültiges JSON-Format.")):
        decrypt_project(legacy_encrypted, "password")
