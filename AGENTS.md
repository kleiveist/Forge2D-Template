<!-- AUTO-GENERATED:backlink START -->
[← Back](README.md)
<!-- AUTO-GENERATED:backlink END -->
# Forge2D Template Repository Rules

Forge2D Template is a general 2D Godot template with small, repository-local Python
tooling. Start with `docs/index.md`, then read the relevant plans, decisions,
reports, configuration, and tests before changing their component.

- Complex template work requires a living ExecPlan under
  `docs/forge2d-template/plans/`; complex game work uses
  `docs/developer/plans/`. Both follow `.agent/PLANS.md`.
- Add or update tests and relevant documentation whenever behavior changes.
- Run the fastest relevant checks first and report only checks actually run.
- Never use destructive Git commands, commit secrets, or add an unreviewed
  dependency. Record each dependency's purpose, maintenance risk, license, and
  considered alternative before adoption.
- Keep generated caches, local binaries, and machine-specific paths out of Git.
- `g2d check` is the standard repository gate. Report only checks actually run.

Keep this file concise; detailed guidance belongs in the documentation it links.
