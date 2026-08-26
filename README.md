# Forge2D

## Purpose

Forge2D is a general-purpose foundation for small 2D projects. The repository
keeps the Godot project, Python tooling, tests, documentation, and shared policy
separate so they can evolve without assuming a gameplay genre or product design.

## Bootstrap status

M01 establishes the repository layout, a neutral Godot 4 smoke scene, and the
dependency-free `g2d` Python CLI foundation. The CLI currently provides help,
version information, and an environment doctor; it does not claim gameplay,
asset-pipeline, installer, or release functionality. The open-source license
decision remains explicitly undecided.

## Developer quick start

Prerequisites are Git, Python 3.11 or newer with `venv` and `pip`, and a verified
Godot 4 editor when working with the game project. Start from a fresh checkout:

```sh
git clone https://github.com/kleiveist/Forge2D.git
cd Forge2D
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-deps -e .
```

On Windows PowerShell, activate the environment with
`.\.venv\Scripts\Activate.ps1` instead. After this one-time installation, the
shortest developer entry point is:

```console
~/Projects/Forge2D
❯ Forge2D
```

The command prints an emoji-guided overview of environment setup, repository
inspection, tests, the Godot smoke check, and the documentation entry point. The
lowercase `g2d` command remains the automation-friendly CLI:

```sh
g2d --help
g2d version
g2d doctor
python -m unittest discover -s tools/tests -v
```

The test command also works directly in a fresh checkout before the editable
installation; the test bootstrap exposes `tools/src` without changing global
Python settings.

`g2d doctor` returns exit code `1` when a required external tool such as Godot is
missing; this is a prerequisite failure, not an internal error. With a compatible
Godot 4 executable available, run the smoke scene without editor interaction:

```sh
godot4 --headless --path game -- --test-mode
```

If the executable is named `godot`, use it only after `godot --version` confirms
major version 4.

## Next milestone

M02 should define the documentation and architecture entry points from validated
Forge2D requirements before adding broader tooling or gameplay structure.
