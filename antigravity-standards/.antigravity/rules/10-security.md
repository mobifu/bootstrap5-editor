---
trigger: always_on
description: Kryptographische Standards und Secret-Handling
---
# Security & Cryptography Guardrails

1. Ciphers: Verwende ausschließlich AES-256-GCM oder ChaCha20-Poly1305 via `cryptography`. Veraltete Verfahren (DES, ECB, unauthentifiziertes CBC) sind verboten.
2. Keys & Salts: Passwörter nur über Argon2id oder PBKDF2-HMAC-SHA256 mit mindestens 16-Byte-Salts (`secrets.token_bytes`) ableiten.
3. Nonces: Jeder Chiffriervorgang erfordert einen frischen 12-Byte-IV. Niemals Nonces wiederverwenden.
4. Logging: Niemals Keys, Hashes, Payloads oder Secrets im Klartext loggen oder in Exception-Strings ausgeben.
