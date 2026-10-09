---
name: Generate Test Suite
command: /test
description: Schreibt eine vollständige Pytest-Suite mit Mocking für eine Zieldatei
arguments:
  - name: target_file
    description: Relativer Pfad zum zu testenden Modul (z. B. src/services/api.py)
    required: true
---
# Workflow: Isolierte Pytest-Suite erstellen

Ziel-Modul: `{{target_file}}`

### Strikte Regeln:
1. Ändere KEINE Zeile im Produktivcode `{{target_file}}`.
2. Mocke ausschließlich externe I/O-Grenzen (Netzwerk, REST-APIs, DB, Subprozesse).
3. Für Dateisystem-Operationen zwingend `tmp_path` als Fixture nutzen – kein `mock_open`.
4. Reines Parsing, Krypto, Hashing und Berechnungen real ausführen.

### Ausführungsschritte:
1. Analysiere `{{target_file}}` und identifiziere alle Schnittstellen.
2. Erstelle oder ergänze die Testdatei unter `tests/test_<modulname>.py`.
3. Führe im Terminal aus:
   `pytest -v tests/test_<modulname>.py --cov={{target_file}} --cov-report=term-missing`
4. Iteriere und korrigiere eventuelle Fehler selbstständig, bis alle Tests grün sind und eine Coverage von mind. 90% erreicht ist.
