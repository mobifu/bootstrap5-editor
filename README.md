<div align="center">

# 🚀 Bootstrap 5 & 3 Low-Code Editor

**Erstelle professionelle, responsive Bootstrap-Layouts in Minuten – ganz ohne HTML-Vorkenntnisse, 100% offline & sicher.**

[![Release](https://img.shields.io/github/v/release/mobifu/bootstrap5-editor?style=for-the-badge&color=blue)](https://github.com/mobifu/bootstrap5-editor/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg?style=for-the-badge)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?style=for-the-badge&logo=python)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)](https://github.com/mobifu/bootstrap5-editor/releases)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/mobifu/bootstrap5-editor/release.yml?style=for-the-badge&label=Build%20%26%20Sign)](https://github.com/mobifu/bootstrap5-editor/actions)

<br/>

<img src="docs/images/info_boostrap_editor.png" alt="Bootstrap Editor Vorschau" width="850" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">

<br/>

[📥 **Download Executable (Releases)**](https://github.com/mobifu/bootstrap5-editor/releases) • [✨ **Features**](#-highlights--features) • [⚡ **Schnellstart**](#-schnellstart) • [🛡️ **Sicherheit**](#-sicherheitsarchitektur) • [📜 **Lizenz**](#-lizenz)

</div>

---

## 💡 Warum Bootstrap Editor?

Die meisten Web-Baukästen erzeugen unübersichtlichen Spaghetti-Code oder binden Nutzer an teure Cloud-Abos. Reine Code-Editoren wiederum überfordern Nicht-Entwickler.

**Der Bootstrap Editor schließt diese Lücke:**
- 🧩 **Visuelles Low-Code Baukastenprinzip**: Komponenten (Banner, Akkordeons, Grid-Spalten, Buttons, Cards) per Mausklick zusammenstellen.
- 🧹 **Sauberer, valider Code**: Generiert schlanken, standardkonformen HTML5-Code für **Bootstrap 5.3** und **Bootstrap 3.3.7** (ideal für z. B. JTL-Shop, WooCommerce, Shopware oder statische Webseiten).
- 🔒 **Datensouveränität & Privatsphäre**: Keine Cloud-Pflicht, kein Tracking. Alle Projektdateien bleiben lokal und werden auf Wunsch mit Militärstandard-Verschlüsselung geschützt.

---

## ✨ Highlights & Features

- **Multi-Version Support**: Volle Unterstützung für modernes **Bootstrap 5** sowie klassisches **Bootstrap 3**.
- **Live-Vorschau**: Integrierte Browser-Vorschau mit sofortiger visueller Aktualisierung bei Änderungen.
- **Vorgefertigte Komponenten**:
  - Flexible Grid-Systeme (1–4 Spalten mit individuellem Breiten- & Offset-Management)
  - Hero-Banner, Call-to-Actions & Akkordeons / FAQ-Sektionen
  - Feature-Cards, Listen, Tabellen & responsive Navigationsleisten
- **1-Klick HTML Export**: Fertigen HTML-Code direkt in die Zwischenablage kopieren oder als Datei speichern.
- **Projektverwaltung**: Projekte speichern, laden und nahtlos weiterbearbeiten.

---

## ⚡ Schnellstart

### Option 1: Für Anwender (Keine Installation nötig)

1. Lade das aktuelle Release-Paket herunter: 👉 [**BootstrapEditor Release ZIP**](https://github.com/mobifu/bootstrap5-editor/releases)
2. Entpacke die ZIP-Datei an einen beliebigen Ort.
3. Starte `BootstrapEditor.exe` mit einem Doppelklick – fertig!

### Option 2: Für Entwickler (Aus dem Quellcode)

```bash
# 1. Repository klonen
git clone https://github.com/mobifu/bootstrap5-editor.git
cd bootstrap5-editor

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Editor starten
python app.py
```

---

## 🛡️ Sicherheitsarchitektur

- **AES-256-GCM Verschlüsselung**: Projektdateien (`.enc`) werden nach OWASP-Empfehlung mit PBKDF2HMAC (SHA-256, 600.000 Iterationen) und kryptografisch sicheren Salts & Nonces (`secrets`-Modul) verschlüsselt.
- **XSS- & Injection-Filter**: Striktes URL-Sanitizing neutralisiert schadhafte URI-Schemata (`javascript:`, `vbscript:`, `data:text/html`).
- **Path-Traversal-Schutz**: Alle internen Dateizugriffe und Vorschau-Generierungen nutzen deterministische `pathlib.Path`-Auflösungen.
- **Supply-Chain-Sicherheit**: Strikte Trennung von Produktions- (`requirements.txt`) und Entwickler-Abhängigkeiten (`requirements-dev.txt`) sowie automatisierte CVE-Prüfung via `pip-audit`.
- **Open Source Provenance**: Automatisierte CI/CD-Releases sind via **Sigstore / GitHub Artifact Attestations** kryptografisch verifiziert.

---

## 🛠️ Entwicklung & Build

### Lokale Tests & Code-Audits
```powershell
# 1. Automatisierte Tests (46 Unit- & Controller-Tests inkl. Coverage)
python -m pytest

# 2. Codebase Audit (Ruff Linter & Formatter)
python -m ruff check .

# 3. Security Audit (Bandit Static Analysis)
python -m bandit -r . -x ./.venv,./build,./dist,./build_staging,./test_*.py -ll

# 4. Dependency Vulnerability Audit (pip-audit)
python -m pip_audit -r requirements.txt
```

### CI/CD Pipeline
- **Continuous Integration (`.github/workflows/ci.yml`)**: Jeder Push und Pull-Request auf `main`/`master` durchläuft automatisch Ruff-Linting, Bandit-Sicherheitsscan, Dependency-Audit (`pip-audit`) und die Pytest-Suite.
- **Release Automation (`.github/workflows/release.yml`)**: Bei getaggten Versionen (`v*`) wird der Windows-Build erstellt, optional code-signiert, mit Sigstore Provenance versehen und auf GitHub Releases veröffentlicht.

### Windows Executable bauen
```powershell
# Standard-Build via PyInstaller (mit optimierter _internal Ordnerstruktur)
python build_exe.py

# Optional: Kompilierung mit Nuitka C-Compiler
python build_exe.py --nuitka
```

---

## 🗺️ Roadmap

- [ ] **Windows-Installer (.exe / Setup-Wizard)**: Umwandlung in eine installierbare Setup-Datei mit Startmenü-Eintrag und Deinstallationsroutine (via Inno Setup / NSIS).
- [ ] **Live-Vorschau Templates & Showcase**: Interaktiver Showcase via GitHub Pages.

---

## 📜 Lizenz

Dieses Projekt ist unter der **GNU General Public License v3.0 (GPLv3)** lizenziert. Weitere Details findest du in der [LICENSE](LICENSE)-Datei.
