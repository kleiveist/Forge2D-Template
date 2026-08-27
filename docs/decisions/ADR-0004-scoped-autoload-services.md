<!-- AUTO-GENERATED:backlink START -->
[← Back](decisions.md)
<!-- AUTO-GENERATED:backlink END -->
# ADR-0004: Limit Autoloads to Process-Wide Infrastructure

- Status: Accepted
- Date: 2026-08-27

## Context

Godot Autoloads are convenient global singletons, but using them for gameplay
state or as a generic service registry hides dependencies and leaves stale state
between scenes. Forge2D needs explicit, stable places for the small number of
concerns that genuinely have process lifetime.

## Decision

Register an Autoload only when it has all of these properties: it is needed
across unrelated scenes, it has process lifetime, it exposes a narrow contract,
and its behavior has dedicated tests. Autoload scripts live under `game/services/`
and use a name that describes their capability.

| Service | Lifetime and responsibility | Status |
| --- | --- | --- |
| `SceneRouter` | Owns full-screen route transitions and route state. It carries no gameplay state. | First justified service when multi-scene flow is implemented. |
| `SettingsService` | Reads, validates, writes, and signals durable user preferences. | Add only with a settings capability. |
| `SaveService` | Owns serialization, slots, versioning, and I/O for durable game data. | Add only with a save/load capability. |
| `AudioService` | Owns buses, music, and sound-effect playback policy. | Add only with an audio capability. |

No Autoload is added by this decision. In particular, Forge2D will not add a
generic `ServiceLocator`, `EventBus`, or mutable `GameState` singleton.

Run-lifetime gameplay data belongs to a `RunSession` object owned by the future
main application scene. The composition root passes the required narrow context
to the active feature, and disposes it when that run ends. A feature must not
store node references in an Autoload.

## Consequences

- Global access is exceptional, named, and testable instead of becoming an
  implicit dependency everywhere.
- Settings, save data, and audio can evolve independently without pre-creating
  unused subsystems.
- A feature that needs per-run data receives it explicitly and can be tested
  without cleaning singleton state.
- Implementing any listed service requires a separately scoped change to
  `project.godot`, its script, and relevant tests.
