import base64
import json
import secrets

from cryptography.exceptions import InvalidKey, InvalidTag
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

GCM_MAGIC_HEADER = b"GCM1"


def _derive_gcm_key(password: str, salt: bytes) -> bytes:
    """
    Leitet einen 256-Bit (32 Bytes) Schlüssel aus dem Passwort ab (PBKDF2HMAC).
    Erfüllt OWASP-Empfehlung mit 600.000 Iterationen und SHA-256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return kdf.derive(password.encode("utf-8"))


def _derive_fernet_key(password: str, salt: bytes) -> bytes:
    """Legacy KDF für Abwärtskompatibilität zu älteren Fernet-Dateien."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def encrypt_project(data_dict: dict, password: str) -> bytes:
    """
    Konvertiert das Projekt-Dictionary in JSON und verschlüsselt es mit AES-256-GCM.
    Format: MAGIC (4 Bytes: 'GCM1') + SALT (16 Bytes) + NONCE (12 Bytes) + CIPHERTEXT & TAG
    """
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = _derive_gcm_key(password, salt)
    aesgcm = AESGCM(key)

    json_data = json.dumps(data_dict).encode("utf-8")
    encrypted_data = aesgcm.encrypt(nonce, json_data, None)

    return GCM_MAGIC_HEADER + salt + nonce + encrypted_data


def decrypt_project(encrypted_content: bytes, password: str) -> dict:
    """
    Entschlüsselt das Projekt unter Unterstützung von AES-256-GCM und Legacy-Fernet.
    """
    if len(encrypted_content) < 16:
        raise ValueError("Die Datei ist zu klein, um gültig zu sein.")

    # AES-256-GCM Format (Standard ab v1.1+)
    if encrypted_content.startswith(GCM_MAGIC_HEADER):
        min_gcm_len = len(GCM_MAGIC_HEADER) + 16 + 12 + 16  # Magic + Salt + Nonce + Tag
        if len(encrypted_content) < min_gcm_len:
            raise ValueError("Die Datei ist zu klein, um gültig zu sein.")

        offset = len(GCM_MAGIC_HEADER)
        salt = encrypted_content[offset : offset + 16]
        offset += 16
        nonce = encrypted_content[offset : offset + 12]
        offset += 12
        ciphertext = encrypted_content[offset:]

        key = _derive_gcm_key(password, salt)
        aesgcm = AESGCM(key)

        try:
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(decrypted_data.decode("utf-8"))
        except InvalidTag as err:
            raise ValueError("Falsches Passwort oder beschädigte Datei.") from err
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            raise ValueError("Entschlüsselte Daten sind kein gültiges JSON-Format.") from err
        except Exception as err:
            raise ValueError("Fehler bei der Entschlüsselung. Bitte Passwort und Datei prüfen.") from err

    # Legacy-Fallback: Fernet (AES-128-CBC + HMAC)
    salt = encrypted_content[:16]
    actual_encrypted_data = encrypted_content[16:]

    key = _derive_fernet_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(actual_encrypted_data)
        return json.loads(decrypted_data.decode("utf-8"))
    except (InvalidKey, InvalidToken) as err:
        raise ValueError("Falsches Passwort oder beschädigte Datei.") from err
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise ValueError("Entschlüsselte Daten sind kein gültiges JSON-Format.") from err
    except Exception as err:
        raise ValueError("Fehler bei der Entschlüsselung. Bitte Passwort und Datei prüfen.") from err
