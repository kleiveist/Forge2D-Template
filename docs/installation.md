# Cross-Platform Installation

`g2d install` validates and prepares a Forge2D Template checkout on Linux,
Windows, and macOS. It can use an already installed operating-system package
manager for missing system requirements, but all Python project packages remain
inside the checkout's `.venv`.

## Recommended Flow

Inspect the complete plan first:

```text
python tools/control.py install --dry-run
```

Then run it interactively, or accept installer-owned confirmations for
unattended setup:

```text
python tools/control.py install
python tools/control.py install --yes
```

Use `python3` when the command is not named `python`. On Windows, the Python
launcher can select the minimum supported interpreter explicitly:

```text
py -3.11 tools/control.py install --dry-run
py -3.11 tools/control.py install --yes
```

Activation is optional. Repository commands can continue to use
`python tools/control.py`; the release gate automatically prefers `.venv` for
its Python tests.

## What the Installer Checks

The preflight reads `config/toolchain.toml` and checks:

- the running Python version against `python.minimum_version`;
- availability of the standard-library `venv` module and `ensurepip`, without
  installing anything into system Python;
- a working pip inside an existing `.venv`, or the ability to create one;
- Godot discovery and its required major version;
- installation of every runtime and development requirement declared in the
  toolchain configuration;
- dependency consistency through `.venv`'s `python -m pip check`; and
- each declared Python distribution through `.venv`'s `python -m pip show`.

The normal, non-dry-run command finishes by printing the full Doctor report.

## Package-Manager Paths

The installer never installs a package manager. It uses one only when already
available and prints every command before executing it.

| Platform | Detected manager | Automatic system packages |
| --- | --- | --- |
| Debian/Ubuntu family | APT (`apt-get`) | `python3-venv`; `godot` only when `apt-cache` proves the candidate is the required Godot major |
| Arch family | Pacman | `python` when bootstrap support is missing; `godot` |
| Windows | Winget | `Python.Python.<minimum>` when needed; exact package ID `GodotEngine.GodotEngine` |
| macOS | Homebrew | `python@<minimum>` when needed; cask `godot` |

APT receives extra scrutiny because repository contents vary by distribution
release. Debian 13 publishes Godot 3 packages, and Ubuntu 24.04 publishes
`godot3`; neither satisfies this Godot 4 project. The installer queries
`apt-cache policy godot`, parses the selected candidate major, and refuses
ambiguous or incompatible packages instead of silently installing Godot 3. See
the official [Debian package record](https://packages.debian.org/trixie/source/godot) and
[Ubuntu package search](https://packages.ubuntu.com/godot).

The other automated Godot identifiers are documented by their package sources:

- [Arch Linux `godot`](https://archlinux.org/packages/extra/x86_64/godot/)
- [Winget `GodotEngine.GodotEngine` manifest](https://github.com/microsoft/winget-pkgs/tree/master/manifests/g/GodotEngine/GodotEngine)
- [Homebrew `godot` cask](https://formulae.brew.sh/cask/godot)

## Safety and Confirmation Rules

`--dry-run` performs only read-only detection and version probes. It does not
run APT, Pacman, Winget, Homebrew, `venv`, or pip installation commands; it does
not create `.venv`; and it never prompts. Exit code 0 means the installer built
a valid local plan. A manual Godot step may remain when no safe package-manager
route exists. Invalid configuration, an unsupported Python without a usable
upgrade path, or missing `venv` support without a remediation path returns 1.

Without `--yes`, all system package-manager commands require one explicit
installer confirmation. Replacing an existing `.venv` whose pip is broken has a
separate confirmation. A negative answer leaves that resource untouched.

With `--yes`, those confirmations are accepted automatically. APT receives
`--yes`, Pacman receives `--noconfirm`, and Winget receives its package/source
agreement flags. Homebrew does not need an acceptance flag for these commands.
Privilege boundaries remain in force: sudo may ask for a password, Windows may
show UAC, and organization policies may still block an install.

Every pip command begins with the `.venv` interpreter, for example:

```text
.venv/bin/python -m pip install -e /path/to/Forge2D-Template
```

On Windows the equivalent interpreter is `.venv\Scripts\python.exe`. The
installer does not call `pip` through the system interpreter and never uses
`--break-system-packages`.

## Failures and Recovery

Expected failures are reported as an installation cause followed by concrete
next steps and the command that failed. Common cases are:

- **Python is too old:** install the configured minimum with the detected
  package manager, open a new terminal when required, and re-run the installer
  with that interpreter. A running process cannot switch Python versions.
- **`venv` or `ensurepip` is unavailable:** on APT systems install
  `python3-venv`; elsewhere repair or reinstall the selected Python. Do not work
  around this by installing project packages into system Python.
- **Existing `.venv` has no pip:** confirm its recreation or re-run with
  `--yes`. Only the repository-local environment is cleared.
- **Godot is missing after setup:** install a trusted Godot 4 build, ensure
  `godot4` or `godot` is on `PATH`, then run
  `python tools/control.py doctor`.
- **A package-manager command fails:** review the displayed stderr, network and
  repository configuration, then run the displayed package-manager command
  manually if appropriate.
- **A Python package fails:** check package-index access and the requirements in
  `config/toolchain.toml`; use only `.venv`'s `python -m pip` for repair.

The installer does not directly download executables, add repositories or taps,
modify shell profiles, bypass package-manager agreements, or promise Godot's
tested patch version. It accepts a compatible Godot 4.x; CI and release notes
record the exact version currently validated by the repository.

## Export Templates

Godot editor installation and Godot export-template installation are separate.
The installer verifies the editor but deliberately does not download the
approximately 1.2 GB cross-platform template archive. Install templates matching
the exact editor version through **Editor > Manage Export Templates**, then use:

```text
python tools/control.py export linux --dry-run
```

The export dry-run verifies the selected release template without writing to the
checkout. See [Cross-platform exports](exporting.md) for all targets, fixed output
paths, CI artifacts, signing limitations, and recovery steps.
