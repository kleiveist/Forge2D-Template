# Forge2D

Forge2D is a minimal Godot 4 + Python repository template with repository-local
tooling entry points.

## Quick start

```text
git clone <repository-url>
cd Forge2D
python tools/control.py doctor
python tools/control.py install
python tools/control.py Forge2D run
```

## Useful commands

```text
python tools/control.py --help
python tools/control.py doctor
python tools/control.py install
python tools/control.py install --dry-run
python tools/control.py install --yes
python tools/control.py godot4
python tools/control.py godot4 run
python tools/control.py godot4 test
python tools/control.py forge2d run
python tools/control.py Forge2D run
```

## Notes

- `python tools/control.py` is the repository-local primary entry point.
- The old global scripts (`g2d`, `Forge2D`) are optional compatibility entry
  points when installed.
- Do not manually `source .venv/bin/activate` for repository setup. The tooling can
  operate directly from `python tools/control.py`.
- On Arch Linux, Godot 4 is typically installed with `sudo pacman -S --needed godot`.
- This repository does not currently assume a specific game runtime workflow.
