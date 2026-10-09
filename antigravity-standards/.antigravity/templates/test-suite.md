\---

description: Erstellt eine isolierte Pytest-Suite mit Mocking für ein Modul

\---

Du agierst als Senior QA Engineer. Erstelle für die angegebene Datei eine Pytest-Suite in `tests/test\_<name>.py`.



REGELN:

1\. Produktivcode niemals anfassen (keine Änderungen!).

2\. Mocking nur an externen I/O-Grenzen (Netzwerk, REST-APIs, DB, Subprozesse).

3\. Für Dateisystem-I/O zwingend die Pytest-Fixture `tmp\_path` nutzen (kein `mock\_open`).

4\. Reines Parsing, Krypto, Hashing und Business-Logik real ausführen.

5\. 100% Typisierung (`mypy --strict`).



SCHLEIFE:

\- Schreibe die Tests (Happy Path, Edge Cases, Error Cases).

\- Führe `pytest -v tests/test\_<name>.py --cov=<modul> --cov-fail-under=90` im Terminal aus.

\- Korrigiere Fehler selbstständig, bis alle Tests grün sind.
