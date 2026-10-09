---
name: Security Audit
command: /audit
description: Führt einen Sicherheits-Audit auf Schwachstellen und Krypto-Hygiene durch – mit automatischer Filterung
arguments:
  - name: target_path
    description: Optionaler Pfad (Datei oder Ordner). Wenn leer, wird das Projekt automatisch analysiert.
    required: false
    default: "auto"
---
# Workflow: Sicherheits-Audit mit Ziel-Filterung

### 1. Scope-Ermittlung
Prüfe den Parameter `target_path`:
- **Falls ein Pfad angegeben wurde (nicht "auto"):** Nutze ausschließlich diesen Pfad als Scope (`<TARGET_SCOPE>`).
- **Falls "auto":** Finde eigenständig alle relevanten Produktivcode-Dateien und -Ordner:
  * Priorisiere Ordner wie `core/`, `src/`, `gui_modules/`, `licensing_module/` sowie Skripte im Root.
  * Schließe STRIKT aus: `.venv/`, `venv/`, `env/`, `build/`, `dist/`, `.git/`, `tests/`, `__pycache__/`, `*.c`, `*.so`, `*.pyd`.
  * Definiere diese Auswahl als deinen Arbeits-Scope (`<TARGET_SCOPE>`).

---

### 2. Statische Sicherheits-Analyse (Bandit)
Führe Bandit mit strengen Ausschlusskriterien im Terminal aus:
`bandit -r <TARGET_SCOPE> -x .venv,venv,tests,build,dist -ll -ii`

*Filtere und bewerte die Befunde nach Relevanz:*
- `B303` (Unsichere Hashes wie MD5/SHA1 für Passwörter)
- `B105`, `B106`, `B107` (Hardcoded Passwörter oder API-Tokens)
- `B608` (SQL- oder Query-Injections)
- `B404`, `B603` (Unsichere Subprocess-/Shell-Aufrufe)

---

### 3. Kryptographie- & Code-Hygiene (Agent-Inspektion)
Untersuche den gefilterten `<TARGET_SCOPE>` gezielt auf folgende Best Practices:
1. **AEAD & Ciphers:** Werden moderne Ciphers wie AES-256-GCM oder ChaCha20-Poly1305 genutzt? Keine veralteten Algorithmen (DES, ECB, unauthentifiziertes CBC).
2. **Key Derivation (KDF):** Werden Passwörter mit Argon2id, PBKDF2 oder bcrypt verarbeitet?
3. **Zufallswerte & IVs:** Werden Nonces/Salts aus `secrets` oder `os.urandom` generiert (niemals aus `random`)? Werden Nonces unter demselben Schlüssel strikt nur einmal verwendet?
4. **Secret-Leakage:** Werden Chiffrate, API-Keys oder Passwörter versehentlich in Logfiles oder Exceptions geschrieben?

---

### 4. Ergebnis-Report
- Falls Schwachstellen gefunden wurden:
  * Liste sie priorisiert auf (Kritisch, Hoch, Mittel) mit Angabe von Datei und Zeilennummer.
  * Liefere für jeden Punkt die konkrete Behebung.
- Falls keine Befunde vorliegen: Bestätige kurz, dass der geprüfte Scope den Sicherheitsanforderungen entspricht.
