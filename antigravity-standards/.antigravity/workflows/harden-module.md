---
name: Harden Project or Module
command: /harden
description: Härtet Code ab (Mypy Strict, Ruff, Bandit, Pytest) – mit automatischer Zielerkennung
arguments:
  - name: target_path
    description: Optionaler Pfad (Datei oder Ordner). Wenn leer, wird das Projekt automatisch analysiert.
    required: false
    default: "auto"
---
# Workflow: Code-Härtung mit automatischer Pfaderkennung

### 1. Scope-Ermittlung
Prüfe den Parameter `target_path`:
- **Falls ein Pfad angegeben wurde (nicht "auto"):** Nutze ausschließlich diesen Pfad als Scope.
- **Falls "auto":** Finde eigenständig alle relevanten Python-Quellcode-Dateien im Projekt:
  * Priorisiere Ordner wie `src/`, `app/` oder einzelne `.py`-Dateien auf Root-Ebene.
  * Schließe temporäre und virtuelle Verzeichnisse STRIKT aus: `.venv/`, `venv/`, `.env/`, `build/`, `dist/`, `.git/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`.
  * Definiere die gefundene Menge als deinen Arbeits-Scope (`<TARGET_SCOPE>`).

---

### 2. Ausführung & Gates
Führe als Senior Engineer folgende Schritte sequenziell im Terminal aus und behebe alle Befunde direkt:

1. **Linting & Formatting:**
   `ruff check --fix <TARGET_SCOPE> && ruff format <TARGET_SCOPE>`

2. **Typsicherheit (Mypy Strict):**
   `mypy --strict <TARGET_SCOPE>`
   *(Behebe alle Typfehler sauber; verwende keine unbegründeten `type: ignore` Workarounds).*

3. **Sicherheits-Scan:**
   `bandit -r <TARGET_SCOPE> -x .venv,venv,tests`
   *(Beseitige gefundene Schwachstellen).*

4. **Regressionsprüfung:**
   `pytest`
   *(Stelle sicher, dass alle vorhandenen Tests nach den Anpassungen weiterhin fehlerfrei laufen).*
