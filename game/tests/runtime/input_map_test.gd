extends RefCounted

const REQUIRED_ACTIONS: Dictionary[StringName, float] = {
	&"ui_up": 0.5,
	&"ui_down": 0.5,
	&"ui_left": 0.5,
	&"ui_right": 0.5,
	&"ui_accept": 0.5,
	&"ui_cancel": 0.5,
	&"gameplay_move_up": 0.2,
	&"gameplay_move_down": 0.2,
	&"gameplay_move_left": 0.2,
	&"gameplay_move_right": 0.2,
	&"app_pause": 0.5,
}
const DIRECTION_ACTIONS: Array[StringName] = [
	&"ui_up",
	&"ui_down",
	&"ui_left",
	&"ui_right",
	&"gameplay_move_up",
	&"gameplay_move_down",
	&"gameplay_move_left",
	&"gameplay_move_right",
]
const BUTTON_ACTIONS: Array[StringName] = [
	&"ui_accept",
	&"ui_cancel",
	&"app_pause",
]

var failures: PackedStringArray = []


func run(_tree: SceneTree) -> PackedStringArray:
	for action in REQUIRED_ACTIONS:
		_expect(InputMap.has_action(action), "InputMap defines '%s'" % action)
		if not InputMap.has_action(action):
			continue
		_expect(
			is_equal_approx(InputMap.action_get_deadzone(action), REQUIRED_ACTIONS[action]),
			"InputMap configures the reviewed deadzone for '%s'" % action,
		)
		_expect(
			not InputMap.action_get_events(action).is_empty(),
			"InputMap configures device events for '%s'" % action,
		)

	for action in DIRECTION_ACTIONS:
		_expect(_has_keyboard_event(action), "'%s' has a keyboard mapping" % action)
		_expect(_has_button_event(action), "'%s' has a D-pad mapping" % action)
		_expect(_has_axis_event(action), "'%s' has an analog-axis mapping" % action)
	for action in BUTTON_ACTIONS:
		_expect(_has_keyboard_event(action), "'%s' has a keyboard mapping" % action)
		_expect(_has_button_event(action), "'%s' has a controller mapping" % action)
	return failures


func _has_keyboard_event(action: StringName) -> bool:
	for event in InputMap.action_get_events(action):
		if event is InputEventKey:
			return true
	return false


func _has_button_event(action: StringName) -> bool:
	for event in InputMap.action_get_events(action):
		if event is InputEventJoypadButton:
			return true
	return false


func _has_axis_event(action: StringName) -> bool:
	for event in InputMap.action_get_events(action):
		if event is InputEventJoypadMotion:
			return true
	return false


func _expect(condition: bool, description: String) -> void:
	if not condition:
		failures.append("InputMap: %s" % description)
