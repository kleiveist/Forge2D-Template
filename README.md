<!-- AUTO-GENERATED:docs-index START -->

## 📄 Files
- 📝 [Forge2D Template Repository Rules](AGENTS.md)
- 📝 [Changelog](CHANGELOG.md)
- 📝 [Contributing Guide](CONTRIBUTING.md)
- 📝 [Security Policy](SECURITY.md)

## Documentation

- 📚 [Documentation hub](docs/index.md)

<!-- AUTO-GENERATED:docs-index END -->
# Forge2D Template

[![CI](https://github.com/kleiveist/Forge2D-Template/actions/workflows/ci.yml/badge.svg)](https://github.com/kleiveist/Forge2D-Template/actions/workflows/ci.yml)

Forge2D Template is a minimal Godot 4 2D game template with repository-local
Python tooling for setup, checks, exports, and releases.

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
repository-local `.venv`. See [Installation](docs/forge2d-template/tooling/installation.md) for supported
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
  [Python](docs/forge2d-template/tooling/python-style-guide.md) and
  [GDScript](docs/forge2d-template/tooling/gdscript-style-guide.md) standards
  without changing files.
- `python tools/control.py check` runs Doctor, source style, Python tests, and
  the Godot headless integration test.
- The project defines keyboard/controller `ui_*`, `gameplay_move_*`, and
  `app_pause` actions plus an optional coordinate-free touch adapter. See the
  [semantic input baseline](docs/forge2d-template/tooling/input.md) for mappings,
  remapping, deadzones, contexts, and accessibility.
- `python tools/control.py export {linux,windows,macos}` creates a validated
  release artifact below ignored `artifacts/exports/`. Start with `--dry-run` and
  see [Cross-platform exports](docs/forge2d-template/tooling/exporting.md) for
  templates, CI, and signing.
- Maintainers use `python tools/control.py release prepare --dry-run` only after
  downloading all three artifacts from the exact successful protected-main CI
  run. See [Publishing a GitHub release](docs/forge2d-template/tooling/releasing.md)
  for the immutable-tag gate, checksums, publication, independent verification,
  and recovery.
- The GitHub `main` branch accepts changes only through pull requests and requires
  every CI job to pass. See [Main branch protection](docs/forge2d-template/tooling/branch-protection.md)
  for the enforced policy and manual setup steps for forks.
- GitHub description and topics follow the versioned
  [repository metadata contract](docs/forge2d-template/tooling/repository-metadata.md).
  No homepage is configured until a maintained canonical destination exists;
  repositories created from this template must replace Forge2D-specific
  metadata and URLs.
- `python tools/control.py godot4 test` runs the dedicated test runner at
  `game/tests/bootstrap_integration_test.gd`. It loads the production bootstrap
  scene without an application test-mode shortcut and verifies its node contract.
- CI builds and validates a wheel, runs the installed `g2d` entry point, and
  produces a short-lived native release artifact on Linux, Windows, and macOS.
- Godot 4.7.2 is the version verified for `v0.1.0`.
- This repository does not currently assume a specific game runtime workflow.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.
It documents safe setup, focused changes, required validation, protected-main
review, commit subjects, dependency review, and the active GitHub templates.
All code changes must follow the mandatory
[Python coding standard](docs/forge2d-template/tooling/python-style-guide.md) and
[GDScript coding standard](docs/forge2d-template/tooling/gdscript-style-guide.md).
Run the focused tests for the changed component first, then
`python tools/control.py style`, and finish with `python tools/control.py check`
before requesting review. Objective rules are CI-enforced; reviewers also verify
naming, documentation, error handling, logging, and test quality.

Never report a suspected vulnerability in a public issue. Use the private GitHub
route and coordinated-disclosure process in [SECURITY.md](SECURITY.md). External
blank issues are deliberately disabled; focused bug and feature forms are
available through the repository issue chooser.
