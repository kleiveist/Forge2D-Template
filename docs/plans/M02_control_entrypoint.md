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

## Notes

- `g2d` and `Forge2D` remain legacy/global script compatibility entry points when
  installed; they are no longer required for first-run.
