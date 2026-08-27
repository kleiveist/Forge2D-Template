# M05 Runtime Architecture ExecPlan

This document is a living execution plan for defining the first extensible
runtime architecture of Forge2D Template.

## Purpose / Big Picture

Forge2D Template needs a small, comprehensible shape before gameplay systems
are added. The architecture defined by this plan gives future work a stable
place for feature code, reusable code, application scenes, and process-wide
services. It also makes scene transitions and dependencies explicit, so adding
a feature does not require a repository-wide redesign.

## Current State

The Godot project currently has one bootstrap scene at
`game/scenes/bootstrap.tscn` and its script at `game/src/bootstrap.gd`. It has
no `[autoload]` configuration and no gameplay system. The repository already
has an accepted top-level layout ADR, a Godot headless integration test, and
`g2d check` as its standard validation gate.

## Scope and Non-Goals

In scope are a documented target folder layout, scene-management rules,
autoload and global-service boundaries, dependency rules, four ADRs, and
documentation-index updates.

Out of scope are moving the bootstrap files, editing `project.godot`, adding an
autoload implementation, changing the main scene, adding assets or
dependencies, and implementing any gameplay, persistence, audio, settings, or
navigation behavior.

## Concrete Steps

1. Record this plan before changing architecture documentation.
2. Add an ADR for the target `game/` folder layout and ownership boundaries.
3. Add an ADR for application composition and scene navigation.
4. Add an ADR for narrowly scoped autoload services and their lifecycle.
5. Add an ADR for one-way dependencies and cross-boundary communication.
6. Add the plan and ADRs to the documentation index.
7. Run a whitespace diff check and the standard `g2d check` gate; record only
   the commands actually run.

## Progress

- [x] 2026-08-27: Inspected the repository rules, plan standard, current Godot
  bootstrap, existing ADR, and GitHub repository state.
- [x] 2026-08-27: Added the architecture decisions and documentation-index
  entries without changing runtime or gameplay files.
- [x] 2026-08-27: Ran and recorded documentation and repository validation.

## Surprises & Discoveries

- The current bootstrap script intentionally remains in `game/src/`, while the
  target layout co-locates future feature scenes and scripts. This plan does
  not move a stable, tested bootstrap only to satisfy a convention.
- No runtime autoload exists today. The ADRs therefore distinguish the target
  registration policy from an implementation and do not add an empty
  `project.godot` section.

## Decision Log

- 2026-08-27: Use feature-owned folders for new gameplay work, application
  composition scenes for application flow, and a small shared boundary rather
  than a global `src/` hierarchy.
- 2026-08-27: Make `SceneRouter` the only initially justified autoload; add
  durable settings, save, and audio services only when their owning capability
  is implemented and tested.
- 2026-08-27: Keep run-lifetime state scoped to an application session instead
  of a process-lifetime `GameState` singleton.

## Validation

Executed from `/workspace`:

| Command | Result |
| --- | --- |
| `git -c safe.directory=/workspace diff --check` | Passed. |
| ADR heading and documentation-index scan with `rg` | Passed; all four ADRs have Context, Decision, and Consequences sections and are linked from `docs/README.md`. |
| `g2d check` | Could not run: `g2d` is not on `PATH` (exit 127). |
| `python tools/control.py check` | Could not run: `python` is not on `PATH` (exit 127). |
| `python3 tools/control.py check` | Ran and failed because Godot 4 and `pytest` are unavailable; Doctor also reported no `.venv`. |

The validation failures are environment prerequisites, not architecture-document
failures. No runtime or gameplay file was changed by this milestone.

## Recovery / Idempotence

This milestone changes Markdown documentation only. Reapplying the agreed
folder and dependency conventions requires no generated state or external
service. If interrupted, inspect `git status --short`, continue at the first
unchecked Progress item, and do not create empty runtime directories merely to
represent a future layout.

## Outcomes & Retrospective

The architecture is documented in ADR-0002 through ADR-0005. Its first runtime
implementation remains deliberately deferred until a separately scoped feature
needs it and can add tests alongside it.
