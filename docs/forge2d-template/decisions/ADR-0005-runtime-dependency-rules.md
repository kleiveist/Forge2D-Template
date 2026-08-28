<!-- AUTO-GENERATED:backlink START -->
[← Back](decisions.md)
<!-- AUTO-GENERATED:backlink END -->
# ADR-0005: Keep Runtime Dependencies One-Way and Explicit

- Status: Accepted
- Date: 2026-08-27

## Context

The planned folder layout is only useful if code has predictable dependency
directions. Unrestricted cross-feature imports, scene-tree searches, and global
event channels make a small Godot project difficult to refactor long before it
becomes large.

## Decision

Use the following permitted dependency shape. Arrows point from a consumer to a
dependency; every layer may also use Godot engine APIs.

```text
application composition (scenes/app)
              |\
              v \
features/<feature> -----> scoped services
       |
       v
shared scenes, scripts, and resources
```

| Consumer | May depend on | Must not depend on |
| --- | --- | --- |
| Application composition | Features, shared code, scoped services | Feature-private implementation details beyond its public scene/resource contract |
| A feature | Its own files, shared code, and a service's narrow public API | Another feature, application-composition internals, or a service implementation detail |
| Shared code and shared scenes | Other shared code and Godot APIs | Any feature, application scene, or service |
| A scoped service | Its own files, shared code, and Godot/platform APIs | Features, feature scenes, or application scenes |

Cross-boundary communication is explicit: parents pass required collaborators or
data to owned children; children emit typed signals outward; services expose
small methods and signals. Do not locate unrelated nodes with absolute scene
paths, store node references globally, use node groups as a command bus, or use
a catch-all global event bus. Signals that represent a feature's public intent
are named and documented by the feature.

Dependencies are promoted only in this order: feature-private first, then shared
after a second consumer exists, then a scoped service only when process lifetime
is demonstrably required. This establishes a directed acyclic dependency graph
among project-owned code.

## Consequences

- A feature can be changed without coordinating with unrelated features.
- The application shell remains a composition boundary rather than a gameplay
  implementation layer.
- Tests can instantiate features with explicit collaborators and assert public
  signals without a fully running application.
- A requested dependency that violates this table requires a new ADR or an
  explicit amendment to this one before implementation.
