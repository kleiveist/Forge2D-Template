# M05 Game Architecture Baseline Report

- Date: 2026-08-27
- Status: Complete; local release gate and all 8 remote CI jobs passed

M05 turns ADR-0002 through ADR-0005 into a running, genre-neutral Godot
application shell. Bootstrap remains the project entry point and creates one
`ApplicationRoot`. The application owns one route host and separate persistent
UI and transition CanvasLayers. The sole Autoload, `SceneRouter`, activates the
neutral `template_home` route from a typed Resource definition.

## Delivered runtime

```text
Bootstrap
└── ApplicationRoot
    ├── RouteHost
    │   └── TemplateHome
    ├── PersistentUI (CanvasLayer)
    └── TransitionLayer (CanvasLayer)

SceneTree root
└── SceneRouter (Autoload)
```

`RouteTable` owns ordered typed `RouteEntry` Resources with a `StringName` ID
and `PackedScene`. It reports null entries, empty and duplicate IDs, and missing
scenes. `SceneRouter` validates configuration, rejects unconfigured or
re-entrant requests, attaches a replacement before releasing the previous
route, preserves the active route on failure, and detaches and frees the active
route during explicit teardown before clearing application references.

The application route host and tests accept plain `Node`, `Node2D`, and
`Control` roots. No camera, physics, gameplay, session, persistence, settings,
audio, input binding, global event bus, service locator, mutable game state, or
placeholder service was added.

## Architecture decisions

ADR-0002 through ADR-0005 required no amendment. Their folder ownership,
centralized navigation, scoped-Autoload, and one-way dependency rules match the
implementation.

M05 selected an ordered array of typed `RouteEntry` Resources rather than a
Dictionary. A Dictionary cannot retain duplicate definitions for validation;
entries make duplicate-ID errors observable and keep editor-authored route
definitions explicit.

Re-entrant navigation and transition-time unconfiguration return `ERR_BUSY`.
An active configuration cannot be replaced implicitly; it returns
`ERR_ALREADY_IN_USE`. These choices keep one transition and one application
owner deterministic. Explicit unconfiguration empties a still-live route host,
so that same host can be configured and used again without retaining a stale
route.

## Tests

The dependency-free Godot runner still emits the release gate's exact marker
only after all focused suites complete. The new suites cover route-table
validation, pre-configuration rejection, safe replacement, one-time cleanup,
unknown IDs, uninstantiable scenes, re-entrant requests, repeated configuration,
explicit teardown and immediate reuse of the same live host, host exit,
application startup/shutdown, failed initial routing, and all three supported
route-root families.

Python assertions verify the main scene, composition nodes, sole Autoload,
required Resources and fixtures, delegated runner, prohibited global scene
changes, physical input codes, fixed viewport constants, forbidden singleton
patterns, cross-feature imports, relative documentation links, and Mermaid fence
balance.

## Validation evidence

An official Godot 4.7.2 Linux binary was downloaded outside the repository,
verified against its published SHA-512 manifest, and exposed as a temporary
`godot4` on `PATH`. No binary or generated Godot/Python cache is tracked.

| Command / check | Observed result |
| --- | --- |
| `git -c safe.directory=/workspace diff --check` | Passed. |
| `.venv/bin/python -m pytest tools/tests/test_godot_project.py tools/tests/test_source_hygiene.py -q` | Passed; 18 tests. |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 71 tests. |
| `python3 -m unittest discover -s tools/tests -v` | Passed; 71 tests. |
| `python3 tools/control.py godot4 test` with verified Godot on `PATH` | Passed on 4.7.2 and emitted `Forge2D bootstrap integration test: passed`. |
| `python3 tools/control.py check` with verified Godot on `PATH` | Passed; Doctor 12/12, 71 Python tests, and marker-validated Godot test. |
| `.venv/bin/g2d check` with verified Godot on `PATH` | Passed; installed CLI repeated the full gate. |
| `godot4 --headless --path game --quit-after 2` | Passed; production Bootstrap and initial route started without parser/runtime errors. |
| Display-backed `python3 tools/control.py godot4 run` | Not run because no display is available. |
| [GitHub Actions run 33106404896](https://github.com/kleiveist/Forge2D-Template/actions/runs/33106404896) for M05 baseline commit `13306f6` | Passed; 8/8 supported matrix jobs succeeded. |

Two environment iterations did not count as passes: the first repository
installer attempt failed because Debian lacked `python3-venv`; after the standard
system component was installed, the installer and Doctor passed. A preliminary
gate invoked with `GODOT4_BIN` failed 8 of 71 tooling tests because test doubles
inherited that discovery variable. Repeating the gate with the verified binary
as a temporary `godot4` on `PATH`, matching CI, passed all steps. No production
or test assertion was weakened to obtain the passing result.

The supported CI matrix—Ubuntu, Windows, and macOS on Python 3.11/3.14 plus
Debian 13 and Arch Linux—was confirmed by the linked run: all 8 jobs completed
successfully.

## Deliberate omissions

M05 leaves settings, save data, audio, localization, input remapping, pause UI,
transitions visuals, sessions, cameras, physics, gameplay features, export
packaging, and route history for capability-driven milestones. M06 can add the
first real feature directly as a route or route-owned child without changing the
core ownership model.
