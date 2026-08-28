<!-- AUTO-GENERATED:docs-index START -->

## 📄 Files
- 📝 [Forge2D Template Repository Rules](AGENTS.md)
- 📝 [Changelog](CHANGELOG.md)

# DOCS
- 📚 [Docs Home](docs/index.md)

## 📄 Coding Standards
- 📝 [Mandatory Python Coding Standard](docs/python-style-guide.md)
- 📝 [Mandatory GDScript Coding Standard](docs/gdscript-style-guide.md)

## 📄 Tooling
- 📝 [Cross-Platform Installation](docs/installation.md)
- 📝 [Cross-Platform Exports](docs/exporting.md)
- 📝 [Publishing a GitHub Release](docs/releasing.md)

## 📄 Releases
- 📝 [Forge2D Template v0.1.0](docs/releases/v0.1.0.md)

## 📁 Architecture
- 🗂️ [Overview](docs/architecture/architecture.md)
- 📝 [Runtime Architecture Overview](docs/architecture/runtime-overview.md)

## 📁 Decisions
- 🗂️ [Overview](docs/decisions/decisions.md)
- 📝 [ADR-0001: Separate Repository Concerns by Top-Level Directory](docs/decisions/ADR-0001-repository-layout.md)
- 📝 [ADR-0002: Organize New Runtime Code by Ownership](docs/decisions/ADR-0002-runtime-folder-layout.md)
- 📝 [ADR-0003: Centralize Application Composition and Scene Navigation](docs/decisions/ADR-0003-application-scenes-and-navigation.md)
- 📝 [ADR-0004: Limit Autoloads to Process-Wide Infrastructure](docs/decisions/ADR-0004-scoped-autoload-services.md)
- 📝 [ADR-0005: Keep Runtime Dependencies One-Way and Explicit](docs/decisions/ADR-0005-runtime-dependency-rules.md)

## 📁 Plans
- 🗂️ [Overview](docs/plans/plans.md)
- 📝 [M01 Repository Bootstrap ExecPlan](docs/plans/M01_repository_bootstrap.md)
- 📝 [M02 Control Entry Point](docs/plans/M02_control_entrypoint.md)
- 📝 [M03 Release v0.1.0 ExecPlan](docs/plans/M03_release_v0_1_0.md)
- 📝 [M04 CI Integrity Hardening ExecPlan](docs/plans/M04_ci_integrity.md)
- 📝 [M05 Game Architecture Baseline ExecPlan](docs/plans/M05_game_architecture_baseline.md)
- 📝 [M06 Cross-Platform Installer ExecPlan](docs/plans/M06_cross_platform_installer.md)
- 📝 [M07 Main Branch Protection ExecPlan](docs/plans/M07_main_branch_protection.md)
- 📝 [M08 Coding Standards ExecPlan](docs/plans/M08_coding_standards.md)
- 📝 [M09 Cross-Platform Export System ExecPlan](docs/plans/M09_export_system.md)

## 📁 Reports
- 🗂️ [Overview](docs/reports/reports.md)
- 📝 [M01 Repository Bootstrap – Abschlussbericht](docs/reports/M01_repository_bootstrap.md)
- 📝 [M02 Control Entry Point Report](docs/reports/M02_control_entrypoint.md)
- 📝 [M03 Release v0.1.0 Report](docs/reports/M03_release_v0_1_0.md)
- 📝 [M05 Game Architecture Baseline Report](docs/reports/M05_game_architecture_baseline.md)

<!-- AUTO-GENERATED:docs-index END -->
# Forge2D Template

[![CI](https://github.com/kleiveist/Forge2D-Template/actions/workflows/ci.yml/badge.svg)](https://github.com/kleiveist/Forge2D-Template/actions/workflows/ci.yml)

Forge2D Template is a minimal Godot 4 + Python repository template with
repository-local tooling entry points.

- Repository: `Forge2D-Template`
- Template ID: `forge2d-template`
- Version: `0.1.0`
- License: MIT
- Tested Godot version: `4.7.2`

## Quick start

```text
git clone <repository-url>
cd Forge2D-Template
python tools/control.py install --dry-run
python tools/control.py install --yes
python tools/control.py check
python tools/control.py forge2d-template run
```

Use `python3` on systems where Python is not exposed as `python`, or
`py -3.11` on Windows. The installer requires Python 3.11 or newer, inspects
Python `venv`/pip support and Godot 4, and keeps all Python packages inside the
repository-local `.venv`. See [Installation](docs/installation.md) for supported
package managers, confirmation behavior, and recovery steps.

## Useful commands

```text
python tools/control.py --help
python tools/control.py version
python tools/control.py doctor
python tools/control.py install
python tools/control.py install --dry-run
python tools/control.py install --yes
python tools/control.py style
python tools/control.py check
python tools/control.py export linux --dry-run
python tools/control.py export linux
python tools/control.py release prepare --dry-run
python tools/control.py godot4
python tools/control.py godot4 run
python tools/control.py godot4 test
python tools/control.py forge2d-template run
python tools/control.py Forge2D-Template run
```

## Notes

- `python tools/control.py` is the repository-local primary entry point.
- `g2d` is the main installed command. `Forge2D-Template` is an optional
  onboarding entry point when installed.
- Do not manually `source .venv/bin/activate` for repository setup. The tooling can
  operate directly from `python tools/control.py`.
- `install --dry-run` performs read-only probes and prints the package-manager,
  `.venv`, and pip commands it would use without creating `.venv` or installing
  anything. `install --yes` accepts installer prompts; operating-system privilege
  controls such as sudo passwords or Windows UAC may still apply.
- The installer never invokes system pip. Editable tooling and all dependencies
  declared in `config/toolchain.toml` are installed and verified through the
  `.venv` Python only.
- `python tools/control.py style` enforces the objective subset of the mandatory
  [Python](docs/python-style-guide.md) and
  [GDScript](docs/gdscript-style-guide.md) standards without changing files.
- `python tools/control.py check` runs Doctor, source style, Python tests, and
  the Godot headless integration test.
- `python tools/control.py export {linux,windows,macos}` creates a validated
  release artifact below ignored `artifacts/exports/`. Start with `--dry-run` and
  see [Cross-platform exports](docs/exporting.md) for templates, CI, and signing.
- Maintainers use `python tools/control.py release prepare --dry-run` only after
  downloading all three artifacts from the exact successful protected-main CI
  run. See [Publishing a GitHub release](docs/releasing.md) for the immutable-tag
  gate, checksums, publication, independent verification, and recovery.
- The GitHub `main` branch accepts changes only through pull requests and requires
  every CI job to pass. See [Main branch protection](docs/branch-protection.md)
  for the enforced policy and manual setup steps for forks.
- `python tools/control.py godot4 test` runs the dedicated test runner at
  `game/tests/bootstrap_integration_test.gd`. It loads the production bootstrap
  scene without an application test-mode shortcut and verifies its node contract.
- CI builds and validates a wheel, runs the installed `g2d` entry point, and
  produces a short-lived native release artifact on Linux, Windows, and macOS.
- Godot 4.7.2 is the version verified for `v0.1.0`.
- This repository does not currently assume a specific game runtime workflow.

## Contributing code

All code changes must follow the mandatory
[Python coding standard](docs/python-style-guide.md) and
[GDScript coding standard](docs/gdscript-style-guide.md). Run the focused tests
for the changed component first, then `python tools/control.py style`, and finish
with `python tools/control.py check` before requesting review. Objective rules are
CI-enforced; reviewers also verify naming, documentation, error handling,
logging, and test quality.
