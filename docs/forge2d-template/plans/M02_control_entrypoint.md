<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M02 Control Entry Point

## Goal

Expose a repository-local bootstrap entry point through
`python tools/control.py` that can run diagnostics, install local tooling, and
launch or test the Godot project without manual virtual-environment activation.

## Progress

- [x] Implement `tools/control.py` bootstrap path injection.
- [x] Centralize repository path detection and tool discovery in `g2dtool`.
- [x] Implement `doctor`, `install`, and Godot command handling in CLI.
- [x] Add tests for new command paths and compatibility aliases.
- [x] Close milestone for Forge2D Template v0.1.0.

## Notes

- `g2d` remains the primary installed command.
- `forge2d-template` and `Forge2D-Template` are template run aliases; the old
  standalone `forge2d`/`Forge2D` aliases are no longer public entry points.
