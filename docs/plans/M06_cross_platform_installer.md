# M06 Cross-Platform Installer ExecPlan

## Purpose / Big Picture

Turn `g2d install` into a safe, mostly automatic repository bootstrap for Linux,
Windows, and macOS. A developer should be able to see every proposed change with
`--dry-run`, opt into unattended package-manager commands with `--yes`, and end
with all Python tooling isolated inside the repository's `.venv`.

## Current State

The installer can create `.venv`, install the local package and declared Python
dependencies, and optionally install Godot with Pacman on Arch Linux. It does not
validate the running Python version or bootstrap capabilities, does not support
APT, Winget, or Homebrew, and reports command failures without tailored recovery
steps. CI runs the real installer on three host platforms but does not explicitly
exercise the mutation-free installer plan on each host.

## Scope and Non-Goals

In scope are Python/venv/pip/Godot preflight checks, safe package-manager command
selection for supported platforms, `.venv`-only Python package installation,
non-mutating dry runs, confirmation behavior, actionable failures, unit tests,
cross-platform CI dry runs, and onboarding/install documentation. Downloading
executables directly, modifying system Python with pip, supporting every Linux
distribution/package manager, and replacing the existing verified Godot CI
download are out of scope. No new third-party dependency is planned.

## Concrete Steps

1. Model host/platform and package-manager detection independently from command
   execution so every supported path can be unit tested on any host.
2. Add Python version, `venv`, pip, Godot, and declared dependency preflight
   checks with explicit remediation.
3. Plan and, after confirmation, execute safe APT, Pacman, Winget, and Homebrew
   installs while reserving pip operations for `.venv`.
4. Make `--dry-run` describe all needed operations without prompts, filesystem
   writes, package-manager calls, or pip installs; make `--yes` accept only the
   installer-owned prompts.
5. Add unit coverage for Linux, Windows, macOS, confirmations, idempotence, and
   expected failure modes.
6. Add a native-host CI dry-run step on Linux, Windows, and macOS, then update
   README and detailed installation documentation.
7. Run focused tests, all available Python tests, the standard `g2d check` gate,
   and static/configuration checks that the local environment supports.

## Progress

- [x] 2026-08-28: Read repository rules, prior tooling/CI plans, configuration,
  current installer implementation, and existing tests; confirmed a clean tree.
- [x] 2026-08-28: Implemented Python/venv/pip/Godot preflight, safe package
  plans for APT/Pacman/Winget/Homebrew, local-only pip operations, dry-run and
  confirmation semantics, and actionable expected errors.
- [x] 2026-08-28: Added cross-platform and failure-path unit tests, native CI
  dry-run coverage, README, installation guide, changelog, and CLI help updates.
- [x] 2026-08-28: Passed all available local tests, the standard release gate,
  a checksum-verified real Godot integration test, and isolated wheel validation.

## Surprises & Discoveries

- 2026-08-28: The container's Git checkout has different ownership, so local Git
  inspection must use a command-scoped `safe.directory` override rather than
  changing global Git configuration.
- 2026-08-28: Debian's current system Python exposes `venv` but not `ensurepip`.
  A healthy existing `.venv` remains fully usable, so the installer must not
  request an unnecessary system repair in that state.
- 2026-08-28: Debian 13 and Ubuntu 24.04 repositories provide Godot 3 rather than
  a compatible Godot 4 editor. APT automation therefore requires a parsed
  Godot-4 candidate instead of assuming the package name is sufficient.
- 2026-08-28: Passing an explicit `GODOT4_BIN` into the entire test suite
  overrides unit-test discovery doubles. The full gate instead used a temporary
  `godot4` command on `PATH`, matching the CI discovery model.

## Decision Log

- 2026-08-28: Keep package-manager detection and command construction in the
  standard-library-only tooling package; no dependency is needed.
- 2026-08-28: Treat `.venv` as the only permitted pip target. System package
  managers may supply Python, venv support, or Godot, but system Python is never
  upgraded or modified through pip.
- 2026-08-28: APT may install `godot` only when `apt-cache policy godot` reports
  the configured required major as the selected candidate; ambiguous, missing,
  and Godot-3 candidates fall back to explicit manual guidance.
- 2026-08-28: Dry-run returns success when it can construct a safe plan even if
  a manual Godot action remains. Invalid configuration or a missing viable
  Python/venv remediation remains a failure.
- 2026-08-28: Existing broken `.venv` contents are cleared only after a dedicated
  confirmation or `--yes`; a new environment and normal local package refresh
  remain automatic installer work.

## Validation

| Command / check | Result |
| --- | --- |
| Focused installer, CLI, control, and logger tests | Passed; 39 tests |
| `python3 tools/control.py install --dry-run --yes` | Passed; read-only probes and plan, no installer mutation |
| Real `install --yes` with checksum-verified Godot 4.7.2 | Passed; `.venv` pip/packages verified and Doctor 12/12 |
| `python3 tools/control.py check` with temporary Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, 90 Python tests, real headless Godot integration test |
| `.venv/bin/python -m unittest discover -s tools/tests` | Passed; 90 tests |
| `python tools/control.py godot4 test` with temporary Godot 4.7.2 | Passed; required integration success marker emitted |
| Python source compilation | Passed for bootstrap, package, and tests |
| Temporary wheel build and isolated install | Passed; installed `g2d version`, `--help`, and installer dry-run |
| CI contract unit test | Passed; native Linux/Windows/macOS matrix contains side-effect-free installer dry-run verification |
| `git diff --check` | Passed |

The GitHub-hosted Windows and macOS jobs were not triggered locally because the
work was neither committed nor pushed. Their native dry runs will execute when
the workflow is next run on GitHub.

## Recovery / Idempotence

Source and documentation edits are reversible with ordinary file edits. Dry-run
must be side-effect free. Real setup reuses a healthy `.venv`; an unhealthy local
`.venv` may be recreated only after an explicit prompt or `--yes`, and system
package-manager commands should use their native idempotent flags where available.

## Outcomes & Retrospective

`g2d install` now provides a reviewable and mostly automatic setup path on all
three target operating systems without using system pip. Its command planning is
host-independent and unit tested, while real system mutations remain delegated
to established package managers and explicit confirmation. The main remaining
boundary is package-manager and repository availability on an individual host;
the installer reports a manual official-download path when it cannot prove a
safe automated Godot 4 route.
