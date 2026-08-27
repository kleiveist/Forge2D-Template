<!-- AUTO-GENERATED:backlink START -->
[← Back](reports.md)
<!-- AUTO-GENERATED:backlink END -->
# M01 Repository Bootstrap – Abschlussbericht

- Datum: 2026-08-26
- Branch: `feat/m01-repository-bootstrap`
- Status: **Milestone bestanden**

## Ziel und Ergebnis

M01 liefert aus einem leeren Workspace ein kleines, startfähiges
Repository-Fundament für Forge2D Template. Enthalten sind zentrale Konfiguration, ein
installierbares Python-Paket mit `g2d`-CLI, deterministische Tests, ein neutrales
Godot-4-Bootstrap-Projekt, Repository-Regeln, ein ExecPlan-Standard und die
Baseline-Dokumentation. Gameplay-, Release- und Installationsarchitektur wurden
nicht vorweggenommen.

Das Repository wurde für die Implementierung lokal ohne Remote initialisiert.
Nach erfolgreicher M01-Verifikation hat der Maintainer Commit und Sync separat
autorisiert. `origin/main` liegt nun im privaten GitHub-Repository
`kleiveist/Forge2D-Template`. Alle Python-Quellen und Python-Tests liegen gemäß
Maintainer-Vorgabe unter `tools/`.

## Getroffene und vertagte Entscheidungen

| Entscheidung | Status | Begründung |
| --- | --- | --- |
| Template-ID `forge2d-template`, Anzeigename `Forge2D Template` | getroffen | Stabile technische Identität bei lesbarem Produktnamen |
| Repository-Sprache Englisch | getroffen | Einheitliche Code- und Dokumentationssprache |
| Python ab 3.11 | getroffen | `tomllib` erlaubt TOML-Verarbeitung ohne Runtime-Abhängigkeit |
| `argparse` und `unittest` | getroffen | Für M01 genügen Standardbibliothek und kleine Module |
| Python-Quellen und Tests unter `tools/` | getroffen | Explizite Maintainer-Vorgabe; eine Ownership-Grenze für sämtliches Python |
| Godot-Hauptversion 4 | getroffen | Projektformat und APIs zielen ausschließlich auf Godot 4 |
| Exakte Godot-Version | vertagt | Kein kompatibler Editor war lokal verfügbar; keine Zahl wurde erfunden |
| Open-Source-Lizenz | getroffen | MIT-Lizenz für die öffentliche v0.1.0-Veröffentlichung |
| Exakte setuptools-Version | vertagt | setuptools ist nur Build-Backend; Nutzen, MIT-Lizenz, Risiko und Alternative sind in `config/toolchain.toml` dokumentiert |

Es bestehen keine Runtime- oder Testabhängigkeiten außerhalb der
Python-Standardbibliothek. `setuptools>=68` ist ausschließlich als Build-Anforderung
deklariert und wurde in diesem Workspace nicht installiert.

## Erstellte und geänderte Dateien

- Repository-Basis: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `.editorconfig`,
  `.gitattributes`, `.gitignore`, `.agent/PLANS.md`, `pyproject.toml`.
- Zentrale Policy: `config/project.toml`, `config/toolchain.toml`.
- Dokumentation: `docs/README.md`, der lebende M01-Plan, ADR-0001 und dieser
  Bericht.
- Godot: `game/project.godot`, `game/scenes/bootstrap.tscn`,
  `game/src/bootstrap.gd`.
- Python-Paket: sechs Module unter `tools/src/g2dtool/`.
- Tests: sechs Testmodule unter `tools/tests/` mit insgesamt 18 Testfällen.

Keine Lockfiles, CI-Workflows, Binärassets, Add-ons, Lizenzdateien oder
generierten Cache-Dateien wurden hinzugefügt.

## Tatsächlich ausgeführte Befehle und Ergebnisse

| Befehl oder Prüfung | Exit-Code | Ergebnis |
| --- | ---: | --- |
| `git status --short`, Branch-/Worktree- und Dateiinventur | 128 vor Initialisierung | Bestätigte einen vollständig leeren, noch nicht initialisierten Workspace |
| `git init -b main` | 0 | Lokales Repository ohne Remote erzeugt |
| `git -c safe.directory=/workspace switch -c feat/m01-repository-bootstrap` | 0 | Isolierten Task-Branch angelegt, ohne globale Git-Konfiguration zu ändern |
| `python3 --version` / `git --version` | 0 | Python 3.11.2 und Git 2.39.5 erkannt |
| TOML-Parse aller TOML-Dateien | 0 | Drei Dokumente syntaktisch valide |
| Erster Python-Testlauf mit 15 Tests | 1 | Zwei fehlerhafte Negativtests entdeckten einen Test-Helferfehler; Produktionscode war nicht betroffen |
| Wiederholung nach Korrektur | 0 | 15 von 15 Tests bestanden |
| Finale Suite nach Godot-Tests und `tools/`-Move | 0 | 18 von 18 Tests bestanden |
| Prüfung aller `*.py`-Pfade | 0 | 12 Python-Dateien, keine außerhalb `tools/` |
| Python-AST-, Packaging- und Toolchain-Audit | 0 | 12 Python-Dateien parsebar; Entry-Point korrekt; null Runtime-Abhängigkeiten; Godot-Version offen markiert |
| `PYTHONPATH=tools/src python3 -m g2dtool --help` | 0 | Hilfe stabil ausgegeben |
| `PYTHONPATH=tools/src python3 -m g2dtool version` | 0 | `g2d 0.1.0` ausgegeben |
| `PYTHONPATH=tools/src python3 -m g2dtool doctor` | 1 | Repository, Konfiguration, Python und Git erkannt; Godot korrekt als fehlend gemeldet |
| Text-, Pfad-, Secret-, Binär- und Cache-Audit | 0 | 29 Dateien sauber; keine generierten Cache-Verzeichnisse oder ausführbaren lokalen Binärtools |
| `git -c safe.directory=/workspace diff --check` | 0 | Keine Whitespace-Fehler im Git-Diff; unversionierte Dateien zusätzlich durch den Textaudit geprüft |
| `git -c safe.directory=/workspace diff --cached --check` | 0 | Der vollständige gestagte Bootstrap-Diff war sauber |
| Bedingter Godot-4-Smoke-Aufruf | 0 (Prüfskript) | Engine-Test als nicht ausgeführt gemeldet, weil weder `godot4` noch kompatibles `godot` verfügbar ist |
| Temporäres `python3 -m venv` für Installationssmoke | 1 | Debian-Python enthält kein `ensurepip`; kein globales Paket wurde nachinstalliert |
| `gh repo create kleiveist/Forge2D-Template --private` | 0 | Zielrepository für die Template-Veröffentlichung erzeugt oder umbenannt |
| Erster HTTPS-Push | 128 | Vor Transfer abgebrochen, weil Git den bestehenden `gh`-Login nicht als Credential-Helper nutzte |
| Push mit auf den Einzelaufruf begrenztem `gh`-Credential-Helper | 0 | Root-Commit ohne Force nach `origin/main` übertragen |
| Vergleich von lokalem Commit und Remote-Ref | 0 | Beide zeigten exakt auf `d1a70de8c65c778f0952abc30061b414c3e99515` |

Git meldet den Workspace wegen unterschiedlicher Container-Eigentümerschaft als
`dubious ownership`. Deshalb wurden Repository-Befehle lokal mit
`git -c safe.directory=/workspace` ausgeführt; globale Konfiguration und
Dateibesitz blieben unverändert.

## Testergebnisse und Exit-Codes

Die finale Standardbibliothek-Suite umfasst 18 erfolgreiche Tests:

- Root-Erkennung aus Unterverzeichnissen und aus einem verlinkten Worktree.
- Laden der Basiskonfiguration sowie Ablehnung falscher Schema- und absoluter
  Projektpfade.
- Stabile CLI-Codes: Hilfe 0, Version 0, Nutzungsfehler 2, Doctor-Erfolg 0,
  fehlende Voraussetzung 1.
- Doctor mit kontrollierten Doubles für vorhandenes Godot 4, fehlendes Godot und
  inkompatibles Godot 3.
- Main-Scene-, Script- und Testmodus-Konsistenz des Godot-Projekts.
- Keine hart codierten Benutzerpfade in Source und Konfiguration.

Der reale Doctor-Code 1 ist erwartetes Verhalten bei fehlendem Godot und kein
interner Fehler.

## Nicht ausgeführte Prüfungen

- Godot-Parse-/Headless-Smoke-Test: nicht ausgeführt, weil kein kompatibles
  Godot-4-Binary auf `PATH` liegt. Nachholbefehl:

      godot4 --headless --path game -- --test-mode

- Installation und Aufruf des erzeugten Console-Scripts `g2d`: nicht ausgeführt,
  weil das lokale Python weder `ensurepip`, `pip` noch setuptools bereitstellt.
  Mit einem isolierten Python inklusive Build-Werkzeugen nachholen:

      python3 -m venv .venv
      .venv/bin/python -m pip install --no-deps .
      .venv/bin/g2d --help
      .venv/bin/g2d version
      .venv/bin/g2d doctor

- Externe Formatter oder Linter: nicht ausgeführt, weil in M01 bewusst keiner
  konfiguriert wurde. AST-Parse, Unit-Tests und Textaudit bilden die lokale
  statische Baseline.
- `g2d check`: in M03 implementiert und als Standard-Gate verwendet.

## Bekannte Risiken und offene Punkte

- Die Bootstrap-Szene ist statisch konsistent, aber noch nicht durch einen echten
  Godot-Editor geparst worden.
- Die exakte Godot- und setuptools-Version muss nach verifizierter Kompatibilität
  festgeschrieben werden.
- Ohne Lizenzentscheidung erhalten Dritte keine implizite Open-Source-Erlaubnis.
- Das Build-Metadaten-Smoke bleibt offen, bis isolierte Python-Buildwerkzeuge
  verfügbar sind.
- Das GitHub-Repository bleibt privat, solange Lizenz und gewünschte Sichtbarkeit
  nicht ausdrücklich entschieden sind.

## Migration und Rückbau

Es existieren keine Vorgängerdaten oder Migrationsschritte. Sämtliche Änderungen
sind additive Textquellen. Nach einem Commit kann der Bootstrap ohne
History-Rewrite über `git revert <commit>` rückgängig gemacht werden. Lokal von
Godot erzeugtes `game/.godot/` ist ignoriert und darf als bekannte generierte
Engine-Ablage entfernt werden; unbekannte Dateien dürfen nicht gelöscht werden.

## Empfohlene atomare Commit-Nachrichten

Für den aktuellen Zero-Start als zusammenhängender Baseline-Commit:

- `feat: bootstrap Forge2D Template repository foundation`

Bei einer späteren Aufteilung wären folgende Grenzen nachvollziehbar:

- `🧰 feat: add minimal g2d CLI and tests`
- `🎮 feat: add Godot bootstrap smoke project`
- `📝 docs: define repository rules and M01 evidence`

## Abschluss

**Milestone bestanden.** Alle lokal ausführbaren verpflichtenden Checks sind
erfolgreich. Die zwei nicht verfügbaren externen Laufzeitprüfungen—Godot und der
installierte Python-Entry-Point—sind mit Grund, ehrlichem Status und
reproduzierbarem Nachholbefehl dokumentiert. Die Baseline ist im privaten
Repository `kleiveist/Forge2D-Template` auf `main` synchronisiert.
