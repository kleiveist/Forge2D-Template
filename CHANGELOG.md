<!-- AUTO-GENERATED:backlink START -->
[← Back](README.md)
<!-- AUTO-GENERATED:backlink END -->
# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

No changes yet.

## Forge2D-Template v0.1.0 - 2026-08-28

### Added

- Initial repository bootstrap for the Godot project, Python CLI, tests, and
  documentation.
- `Forge2D-Template` developer onboarding command with an emoji-guided command
  overview.
- `python tools/control.py check` release gate for Doctor, source style, Python
  tests, and the Godot headless integration test.
- GitHub Actions CI for Python 3.11 and 3.14 on Ubuntu, Windows, macOS, Debian,
  and Arch Linux with Godot 4.7.2 validation.
- Minimal runtime composition with an application root, named scene router,
  neutral template-home route, scoped Autoload, and headless integration tests.
- MIT license.
- Mandatory repository-wide Python and GDScript coding standards now define
  formatting, naming, typing, documentation, error, logging, and test rules.
- `g2d style` provides dependency-free, actionable source validation and is part
  of the cross-platform `g2d check` release gate.
- Reviewed Linux, Windows, and macOS Godot presets plus `g2d export` provide
  fixed repository-local outputs, a side-effect-free dry-run, and actionable
  template, process, and artifact failures.
- Native CI jobs verify official export-template checksums, produce non-empty
  platform exports, and retain validated workflow artifacts for seven days.
- `g2d release prepare` verifies downloaded main-branch CI exports, gives them
  versioned public names, and creates a deterministic SHA-256 checksum document.

### Changed

- `g2d install` now validates Python, venv/pip bootstrap support, Godot 4, and
  declared Python packages; uses APT, Pacman, Winget, or Homebrew when safe; and
  confines all pip changes to the repository-local `.venv`.
- Installer dry runs are side-effect free, unattended confirmation is available
  through `--yes`, and expected failures include recovery steps.
- Native Linux, Windows, and macOS CI jobs verify the installer dry run without
  creating `.venv`.
- GitHub `main` branch protection now requires pull requests, an up-to-date
  successful eight-job CI matrix, linear history, and resolved conversations;
  administrators cannot bypass the rule or force-push/delete the branch.
- Public project identity is now Forge2D Template / `Forge2D-Template` /
  `forge2d-template`.
