extends Node
class_name Forge2DTouchActionAdapter

## Translates optional touch UI signals into existing semantic InputMap actions.
##
## Presentation code owns touch coordinates and gestures. This adapter owns only
## synthetic action presses and releases them when disabled or removed from the
## tree so a route transition cannot leave an action stuck.

var _input_enabled := true
var _pressed_actions: Dictionary[StringName, bool] = {}


func _exit_tree() -> void:
	release_all_actions()


## Enables or disables new synthetic presses. Disabling releases owned actions.
func set_input_enabled(enabled: bool) -> void:
	if _input_enabled == enabled:
		return
	_input_enabled = enabled
	if not _input_enabled:
		release_all_actions()


## Reports whether this adapter currently accepts new synthetic presses.
func is_input_enabled() -> bool:
	return _input_enabled


## Presses a configured semantic action with strength clamped to `[0.0, 1.0]`.
func press_action(action: StringName, strength: float = 1.0) -> Error:
	var validation_error := _validate_action(action)
	if validation_error != OK:
		return validation_error
	if not _input_enabled:
		return ERR_UNAVAILABLE

	var normalized_strength := clampf(strength, 0.0, 1.0)
	if is_zero_approx(normalized_strength):
		return release_action(action)
	Input.action_press(action, normalized_strength)
	_pressed_actions[action] = true
	return OK


## Releases a configured semantic action and forgets adapter ownership.
func release_action(action: StringName) -> Error:
	var validation_error := _validate_action(action)
	if validation_error != OK:
		return validation_error
	Input.action_release(action)
	_pressed_actions.erase(action)
	return OK


## Releases every synthetic action currently owned by this adapter.
func release_all_actions() -> void:
	for action in _pressed_actions:
		Input.action_release(action)
	_pressed_actions.clear()


func _validate_action(action: StringName) -> Error:
	if action == &"":
		return ERR_INVALID_PARAMETER
	if not InputMap.has_action(action):
		return ERR_DOES_NOT_EXIST
	return OK
