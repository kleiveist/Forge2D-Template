# Forge2D Repository Rules

Forge2D is a general 2D Godot template with small, repository-local Python
tooling. Start with `docs/README.md`, then read the relevant plans, decisions,
reports, configuration, and tests before changing their component.

- Complex, multi-step, or architectural work requires a living ExecPlan under
  `docs/plans/` that follows `.agent/PLANS.md`.
- Add or update tests and relevant documentation whenever behavior changes.
- Run the fastest relevant checks first and report only checks actually run.
- Never use destructive Git commands, commit secrets, or add an unreviewed
  dependency. Record each dependency's purpose, maintenance risk, license, and
  considered alternative before adoption.
- Keep generated caches, local binaries, and machine-specific paths out of Git.
- `g2d check` is the planned standard repository gate. Until it is implemented,
  use the component checks linked from the current milestone plan and report.

Keep this file concise; detailed guidance belongs in the documentation it links.
