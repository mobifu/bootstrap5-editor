---
trigger: always_on
description: Strikte Konventionen für Pytest, Mocking, Typisierung und Test-Abdeckung
---
# Testing Guardrails & Quality Standards

1. Framework & Struktur:
   - Verwende ausschließlich `pytest` mit `pytest-mock` und `pytest-cov`.
   - Testdateien liegen unter `tests/` und spiegeln die Modulstruktur wider (z. B. `src/services/api.py` -> `tests/services/test_api.py`).
   - Jede Testfunktion und Fixture muss vollständig typisiert sein (`mypy --strict` Konformität).

2. Mocking-Grenzen:
   - Mocke AUSSCHLIESSLICH an System- und I/O-Grenzen: Externe HTTP-Requests, Datenbanken, Sockets, Subprozesse, Threading/Sleep.
   - Dateisystem-I/O: Niemals `unittest.mock.mock_open` nutzen. Verwende immer die native Pytest-Fixture `tmp_path`.
   - Interne Logik, Datenumwandlungen, kryptographische Operationen, Hashes und CSV-Parsing werden NIEMALS gemockt, sondern real ausgeführt.

3. Test-Design & Vollständigkeit:
   - Schreibe für jede Funktion mindestens:
     * Happy Path: Erwartetes Verhalten bei validen Daten.
     * Edge Cases: Leere Payloads, None-Werte, maximale Grenzwerte, Sonderzeichen.
     * Failure Path: Netzwerk-Timeouts, korrupte Daten, falsche Passwörter / manipulierte Chiffrate.
   - Nutze `pytest.mark.parametrize` für wiederkehrende Validierungsprüfungen anstelle von redundanten Testfunktionen.
   - Validiere bei Exceptions explizit die Fehlermeldung: `with pytest.raises(ExpectedError, match="..."):`.

4. Coverage-Vorgabe:
   - Eine Mindest-Testabdeckung von 90% ist für jedes getestete Modul zwingend einzuhalten.
