# ADR-0002: Organize New Runtime Code by Ownership

- Status: Accepted
- Date: 2026-08-27

## Context

The bootstrap establishes that `game/` owns the Godot project, but it does not
say where future features, reusable parts, application scenes, and assets
belong. A single global script directory is easy to start with but makes
feature ownership and safe deletion progressively harder to see.

## Decision

Keep `game/` as the project root and use the following target layout for new
runtime work:

```text
game/
  assets/                 # Cross-feature art, audio, fonts, and static data
  scenes/
    app/                  # Application composition and full-screen flow scenes
    shared/               # Reusable scenes with no feature dependency
  features/
    <feature-name>/       # One feature's scenes, scripts, resources, and assets
      components/         # Feature-private reusable scene pieces
  shared/
    scripts/              # Reusable, feature-neutral code
    resources/            # Reusable, feature-neutral Resources
  services/               # Implementations intended for Autoload registration
  tests/                  # Godot tests mirroring app, feature, or shared owners
```

`features/<feature-name>/` is the default home for new gameplay work. A feature
may contain its own scenes, GDScript, `Resource` definitions, components, and
assets. Feature-private files stay there; only a second real consumer justifies
promotion to `scenes/shared/`, `shared/`, or `assets/`.

`scenes/app/` owns composition and application flow, not gameplay rules.
`scenes/shared/` and `shared/` may not depend on a feature. The global
`assets/` directory is only for cross-feature assets; assets used by one feature
stay with that feature.

The existing `scenes/bootstrap.tscn` and `src/bootstrap.gd` remain in place.
The layout is a forward-looking convention, not a reason to move tested files
or create empty directories.

## Consequences

- A feature can usually be located, reviewed, tested, and removed from one
  directory.
- Reusable code has an explicit promotion path instead of accumulating in an
  undifferentiated global script folder.
- New shared abstractions require evidence of reuse, which avoids a premature
  framework.
- A later, authorized migration may relocate the bootstrap to `scenes/app/`;
  this ADR does not alter the active main scene or source paths.
