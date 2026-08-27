<!-- AUTO-GENERATED:backlink START -->
[← Back](decisions.md)
<!-- AUTO-GENERATED:backlink END -->
# ADR-0003: Centralize Application Composition and Scene Navigation

- Status: Accepted
- Date: 2026-08-27

## Context

As soon as Forge2D has more than one screen or game mode, allowing every scene
to call `SceneTree.change_scene_*` produces hidden navigation paths, inconsistent
transition behavior, and no clear place to manage application-level UI.

## Decision

Adopt these scene-management roles:

| Role | Owner | Rule |
| --- | --- | --- |
| Main application scene | `scenes/app/` | Composes persistent application UI and the active full-screen scene. |
| Flow scene (menu, game mode, results) | `scenes/app/` or its owning feature | Owns one full-screen state and emits intent to navigate. |
| Feature scene | `features/<feature-name>/` | Owns feature presentation and local child scenes; it does not change the scene tree globally. |
| Reusable component | `scenes/shared/` or a feature's `components/` | Is owned and freed by its parent scene; it never selects the application route. |

The future main application scene is the composition root. It creates
run-lifetime objects, attaches persistent presentation such as an overlay when
needed, and starts the initial route. It does not contain gameplay rules.

`SceneRouter` is the sole application-wide API permitted to replace a
full-screen route. It owns route lookup, transition sequencing, the current
route, and any later back-stack policy. A screen requests navigation by emitting
a signal or calling this narrow router API; it must not call
`get_tree().change_scene_*` itself. Local child-scene creation remains the
parent scene's responsibility.

The existing bootstrap remains the configured main scene until an implementation
change is explicitly authorized. This decision defines how that future change
will work; it adds neither a router nor a new main scene now.

## Consequences

- Application flow has one inspectable owner, making transitions and error
  handling consistent.
- Gameplay scenes remain usable in focused tests because they do not need to
  replace the global scene tree.
- Navigation must be introduced with a tested router and a route contract before
  a second full-screen flow is added.
- Simple parent-to-child composition is still direct; it is not routed through a
  global manager.
