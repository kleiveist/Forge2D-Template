<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M11 Semantic Input Baseline ExecPlan

## Purpose / Big Picture

Provide a small, reusable Godot InputMap baseline that expresses interface,
movement, and pause intent without leaking keyboard, controller, or touch details
into runtime features. A project can consume the same action names on desktop,
controller, or optional touch UI and can later remap bindings without rewriting
gameplay code.

## Current State

At the start of Issue #5, architecture and hygiene rules prohibited physical
runtime input, but no versioned InputMap, device mappings, touch adapter, or
guide existed. Draft PR #9 now contains eleven configured semantic actions,
coordinate-free optional touch adaptation, tests, and documentation alongside
completed Issues #2/#3 and repository-side Issue #4 release preparation. Remote
CI run `33172796968` passed all eight required jobs for implementation commit
`df551ee`.

## Scope and Non-Goals

In scope are eleven actions: standard `ui_*` navigation/accept/cancel, four
semantic `gameplay_move_*` directions, `app_pause`, keyboard and any-device
controller bindings, documented deadzones, an optional coordinate-free adapter,
headless behavior tests, static mapping tests, source-hygiene coverage,
accessibility/remapping guidance, changelog/release-note updates, and all local
and remote repository gates.

Out of scope are a mandatory touch HUD, touch coordinates or gesture policy,
input-remapping UI, saved user profiles, multiplayer device assignment, mouse
look, gameplay movement code, automatic pausing, vibration, platform-specific
controller databases, and new dependencies.

## Concrete Steps

1. Audit Issue #5, M05 input rules, GDScript standards, project settings,
   headless test orchestration, hygiene checks, and current Godot 4.7.2 event
   serialization.
2. Add the eleven reviewed semantic actions to `game/project.godot` with keyboard,
   D-pad/face/start-button, and left-stick bindings plus purpose-specific
   deadzones.
3. Add a reusable optional touch adapter that accepts only action names and
   normalized strength, releases owned actions on disable/exit, and reports
   recoverable errors without handling coordinates.
4. Add headless InputMap/touch lifecycle tests and Python contracts for exact
   action names, deadzones, representative mappings, UID metadata, test-suite
   integration, and the physical-input runtime boundary.
5. Document semantics, naming, contexts, remapping, deadzones, touch wiring,
   accessibility, troubleshooting, and the no-new-dependency decision.
6. Run focused Python tests, source style, the real Godot suite, all Python
   tests, the complete `g2d check` gate, and Git hygiene checks.
7. Commit with an emoji-prefixed English subject, push to draft PR #9, wait at
   least three minutes before every Actions inspection, and iterate until all
   eight required jobs are green.
8. Record the green run, leave an evidence comment on Issue #5, mark it with
   `Closes #5` in the PR, and ask for `J` before beginning Issue #6.

## Progress

- [x] 2026-08-28: Received explicit approval to begin Issue #5 and confirmed a
  clean, synchronized `feat/release-readiness` branch.
- [x] 2026-08-28: Audited the issue, M05 architecture, GDScript standard,
  project file, headless suite, Python contracts, and physical-input hygiene.
- [x] 2026-08-28: Probed Godot 4.7.2 locally for exact key, joypad button, axis,
  and serialized InputEvent values without changing the repository project.
- [x] 2026-08-28: Added all eleven reviewed actions, keyboard/controller
  mappings, any-device controller scope, and UI/gameplay deadzones.
- [x] 2026-08-28: Added the coordinate-free touch adapter and headless tests for
  InputMap events, synthetic strength, expected failures, disable, and tree exit.
- [x] 2026-08-28: Added exact Python mapping/hygiene contracts and documented
  semantics, contexts, remapping, touch wiring, accessibility, and recovery.
- [x] 2026-08-28: Passed 154 Python tests, style for 42 source files, the real
  Godot 4.7.2 suite, and the complete local repository gate.
- [x] 2026-08-28: Passed all eight pull-request CI jobs in run `33172796968`
  for implementation commit `df551ee`.

## Surprises & Discoveries

- 2026-08-28: M05 deliberately deferred physical bindings but already reserved
  `ui_*` for interface actions and `app_*` for application intent such as pause;
  Issue #5 can extend that contract without revising the ownership model.
- 2026-08-28: Godot stores left-stick directions as signed
  `InputEventJoypadMotion.axis_value` values. Direction actions can therefore
  retain analog strength while runtime code reads only action names.
- 2026-08-28: A direct GitHub issue closure would be premature before the shared
  PR merge. The PR closing keyword records completion and lets GitHub close the
  issue when the reviewed implementation reaches protected `main`.
- 2026-08-28: A fresh headless cache cannot resolve a newly introduced global
  class name while compiling its test before import. Typing the test fixture
  through its direct preloaded script matches existing suites and removes cache
  ordering without weakening the production class.

## Decision Log

- 2026-08-28: Use `ui_up/down/left/right`, `ui_accept`, and `ui_cancel` so Godot
  Control focus navigation receives the conventional semantic actions.
- 2026-08-28: Use `gameplay_move_up/down/left/right` as a genre-neutral baseline
  capability and `app_pause` as application intent. Do not add player, camera,
  jump, attack, inventory, or other genre assumptions.
- 2026-08-28: Map arrows plus physical-position WASD for movement, arrows for UI,
  controller D-pad/left stick for both contexts, A/B for accept/cancel, and
  Start plus Escape/P for pause. Device `-1` accepts any connected controller.
- 2026-08-28: Use a `0.5` UI/button deadzone and `0.2` gameplay movement
  deadzone. UI should resist accidental focus changes; movement should retain
  useful analog range. Both remain user-remappable project policy.
- 2026-08-28: Keep touch optional and presentation-owned. `TouchScreenButton`
  can target actions directly; other touch Controls call a small adapter that
  never observes coordinates and releases synthetic presses on lifecycle exits.
- 2026-08-28: Add no dependency or addon. Godot InputMap, Input APIs, signals,
  existing headless tests, and Python standard-library contracts cover the work.

## Validation

| Command / check | Result |
| --- | --- |
| Godot 4.7.2 constant and serialization probe | Passed; exact local values recorded for implementation |
| `.venv/bin/python -m pytest tools/tests/test_godot_project.py tools/tests/test_source_hygiene.py -q` | Passed; 27 tests |
| `python tools/control.py style` | Passed; 42 source files |
| `python tools/control.py godot4 test` with verified Godot 4.7.2 | Passed; InputMap, adapter, architecture, and bootstrap suites |
| Fresh `/tmp` project copy without `.godot` cache, then headless suite | Passed; global-class and UID imports work from a clean cache |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 154 tests |
| `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 42/42, 154 tests, Godot integration |
| `python tools/control.py release prepare --dry-run` | Passed; v0.1.0 changelog and release notes remain consistent, no writes |
| `git diff --check` | Passed |
| Pull-request CI run `33172796968` for commit `df551ee` | Passed; all eight Linux, Windows, and macOS jobs |

## Recovery / Idempotence

InputMap entries and documentation are reviewed text. The touch adapter owns only
the synthetic actions it presses and releases all of them when disabled, asked,
or removed from the tree, preventing stuck input during scene changes. Tests
release shared Input state even after expected failures. Revert action bindings,
adapter, tests, and docs together if the contract is withdrawn; never weaken the
runtime physical-code hygiene rule to accommodate a feature.

## Outcomes & Retrospective

The local baseline is complete: one reviewed InputMap supplies eleven semantic
actions across keyboard and controller, while optional touch presentation can
reuse them without device-aware gameplay code. Automated contracts cover exact
mappings, deadzones, input families, error/lifecycle behavior, and the physical-
code boundary. Pull-request run `33172796968` provides the final remote evidence
with all eight jobs green for implementation commit `df551ee`.
