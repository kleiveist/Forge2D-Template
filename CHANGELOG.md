<!-- AUTO-GENERATED:backlink START -->
[← Back](README.md)
<!-- AUTO-GENERATED:backlink END -->
# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

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

## Forge2D-Template v0.1.0 - 2026-08-26

### Added

- Initial repository bootstrap for the Godot project, Python CLI, tests, and
  documentation.
- `Forge2D-Template` developer onboarding command with an emoji-guided command
  overview.
- `python tools/control.py check` release gate for Doctor, Python tests, and the
  Godot headless smoke test.
- GitHub Actions CI for Python tests and Godot 4.7.2 headless smoke validation.
- MIT license.

### Changed

- Public project identity is now Forge2D Template / `Forge2D-Template` /
  `forge2d-template`.
