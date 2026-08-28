<!-- AUTO-GENERATED:backlink START -->
[← Back](index.md)
<!-- AUTO-GENERATED:backlink END -->
# Semantic Input Baseline

Forge2D Template defines device bindings once in `game/project.godot` and keeps
runtime code dependent on semantic Godot InputMap actions. Keyboard, controller,
remapped, and optional touch input therefore reach the same feature code without
device branches.

## Action Contract

| Action | Intent | Keyboard | Controller | Deadzone |
| --- | --- | --- | --- | ---: |
| `ui_up` | Move interface focus up | Up arrow | D-pad up or left stick up | `0.5` |
| `ui_down` | Move interface focus down | Down arrow | D-pad down or left stick down | `0.5` |
| `ui_left` | Move interface focus left | Left arrow | D-pad left or left stick left | `0.5` |
| `ui_right` | Move interface focus right | Right arrow | D-pad right or left stick right | `0.5` |
| `ui_accept` | Activate the focused interface control | Enter or Space | South/A face button | `0.5` |
| `ui_cancel` | Back out of the current interface context | Escape | East/B face button | `0.5` |
| `gameplay_move_up` | Request upward gameplay movement | Physical W or Up arrow | D-pad up or left stick up | `0.2` |
| `gameplay_move_down` | Request downward gameplay movement | Physical S or Down arrow | D-pad down or left stick down | `0.2` |
| `gameplay_move_left` | Request leftward gameplay movement | Physical A or Left arrow | D-pad left or left stick left | `0.2` |
| `gameplay_move_right` | Request rightward gameplay movement | Physical D or Right arrow | D-pad right or left stick right | `0.2` |
| `app_pause` | Request pause or resume at the application boundary | Escape or physical P | Start button | `0.5` |

Godot's standard `ui_*` names allow `Control` focus navigation to work without a
device-specific handler. `app_pause` expresses intent only; the baseline does
not pause the SceneTree. The owning application state decides whether a pause
request is currently valid.

Escape intentionally supports both `ui_cancel` and `app_pause`. A route must
activate only the handler appropriate to its current state: for example, a modal
menu handles cancel while gameplay handles pause. Do not run both policies
globally for the same frame. Projects that need independent keys can change the
events without renaming either action.

## Runtime Use

Movement code reads a normalized semantic vector and retains analog controller
strength:

```gdscript
var movement := Input.get_vector(
	&"gameplay_move_left",
	&"gameplay_move_right",
	&"gameplay_move_up",
	&"gameplay_move_down",
)
```

Interface and application code similarly asks for actions:

```gdscript
if Input.is_action_just_pressed(&"app_pause"):
	pause_requested.emit()
```

Runtime source must not inspect keycodes, joypad buttons/axes, mouse buttons, or
touch positions. `tools/tests/test_source_hygiene.py` enforces this boundary for
runtime folders. Physical constants belong only in reviewed InputMap
configuration and mapping-contract tests.

## Controller and Deadzone Policy

Every controller event uses device `-1`, so a matching event from any connected
controller can drive the baseline. Godot's logical face-button names are used;
user-facing prompts should show the detected platform's label or glyph instead
of assuming Xbox lettering.

The `0.5` interface deadzone avoids accidental focus movement from stick drift.
The `0.2` movement deadzone exposes more useful analog range. These values are
starting points, not accessibility limits. A settings feature may let users tune
them independently with `InputMap.action_set_deadzone()` and should provide a
live preview. Do not apply a second hidden deadzone in gameplay code.

## Remapping Contract

- Keep action names stable; replace their events through `InputMap`.
- Offer at least one keyboard and one controller binding per required action.
- Detect and explain conflicts instead of silently deleting another action's
  binding.
- Let users restore the reviewed defaults and cancel changes without mutation.
- Store user overrides outside the repository. Runtime `InputMap` changes are
  not persisted automatically; a future settings capability owns serialization.
- Update input prompts from the active mappings rather than hard-coded text.
- Keep UI and gameplay contexts distinct even when they share a physical event.

The baseline deliberately includes no remapping screen or save format. Those are
project-specific presentation and persistence choices.

## Optional Touch Adaptation

Touch is optional and presentation-owned. The simplest path is a
`TouchScreenButton` whose `action` property is one of the names above. Godot then
emits the same InputMap action as keyboard or controller input.

For regular `Control` buttons or a virtual stick, add
`Forge2DTouchActionAdapter` from
`game/shared/input/touch_action_adapter.gd` to the touch UI. Connect
`button_down` and `button_up` signals to semantic calls:

```gdscript
func _on_left_button_down() -> void:
	touch_action_adapter.press_action(&"gameplay_move_left")


func _on_left_button_up() -> void:
	touch_action_adapter.release_action(&"gameplay_move_left")
```

An analog presentation may pass a normalized strength for each direction. The
adapter clamps strength to `[0.0, 1.0]`, treats zero as release, rejects missing
actions, and releases every action it owns when disabled or removed from the
tree. It never accepts touch events, coordinates, or gesture policy. The owning
touch UI converts those presentation details into semantic strengths.

Touch controls should be hidden when inappropriate, respect display safe areas,
use comfortably sized targets, and allow simultaneous directional and action
presses. Do not make touch the only way to reach an interface operation.

## Accessibility Checklist

- Support full keyboard and full controller navigation without requiring a
  pointer.
- Avoid mandatory holds, rapid repetition, or multi-button chords for baseline
  actions; provide toggles or alternatives when a project adds them.
- Allow direction, accept, cancel, and pause bindings to be changed separately.
- Do not communicate an action through color, controller glyph, or vibration
  alone.
- Preserve focus visibility and predictable focus order for `ui_*` actions.
- Consider one-handed layouts and adjustable analog deadzones.
- Pause should remain reachable while gameplay is active and should not depend
  on frame-perfect timing.

## Validation and Troubleshooting

The headless `input_map_test.gd` verifies required actions, deadzones, and event
families. `touch_action_adapter_test.gd` covers press/release strength, invalid
actions, disable cleanup, and tree-exit cleanup. Python tests protect exact
representative keyboard/controller values and the coordinate-free adapter
boundary. All suites run through `g2d check` and the cross-platform CI matrix.

- If an action does not fire, check **Project > Project Settings > Input Map**
  and retain the exact semantic name.
- If stick drift triggers movement or navigation, tune the action deadzone, not
  feature movement math.
- If a synthetic action appears stuck, ensure every UI press has a release and
  that the adapter remains the owner; disabling or freeing it releases all owned
  actions.
- If Escape performs two operations, correct the active UI/gameplay context
  ownership or remap one event. Do not add a physical Escape check to runtime
  code.
