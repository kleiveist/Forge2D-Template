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
python tools/control.py doctor
python tools/control.py install
python tools/control.py check
python tools/control.py forge2d-template run
```

## Useful commands

```text
python tools/control.py --help
python tools/control.py version
python tools/control.py doctor
python tools/control.py install
python tools/control.py install --dry-run
python tools/control.py install --yes
python tools/control.py check
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
- `python tools/control.py check` runs Doctor, Python tests, and the Godot
  headless integration test.
- `python tools/control.py godot4 test` runs the dedicated test runner at
  `game/tests/bootstrap_integration_test.gd`. It loads the production bootstrap
  scene without an application test-mode shortcut and verifies its node contract.
- CI also builds a wheel, installs it into a fresh virtual environment, and runs
  the installed `g2d` entry point.
- Godot 4.7.2 is the version verified for `v0.1.0`.
- This repository does not currently assume a specific game runtime workflow.
