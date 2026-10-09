\---

trigger: always\_on

description: Grundregeln für Python-Entwicklung, Typisierung und Code-Qualität

\---

\# Python Core Standards



1\. Rolle: Handle als Senior Python Engineer.

2\. Typisierung: Alle Funktionen und Klassen müssen 100% mit Type Hints versehen sein (`mypy --strict` Konformität). Keine unbegründeten `Any`.

3\. Code-Qualität: Nutze moderne Python 3.10+ Idiome, striktes Formatting (Ruff) und Context Manager für alle I/O-Ressourcen.

4\. Terminal-Autonomie: Führe nach jeder Änderung eigenständig `ruff check --fix` und `mypy --strict` auf den betroffenen Pfaden aus.
