extends Node

signal startup_succeeded(initial_route_id: StringName)
signal startup_failed(error: Error, message: String)

const RouteTable := preload("res://shared/resources/route_table.gd")

@export var route_table: RouteTable
@export var initial_route_id: StringName = &""

@onready var route_host: Node = $RouteHost

var _started := false
var _startup_error: Error = OK


func _ready() -> void:
	var configuration_error := SceneRouter.configure(route_host, route_table)
	if configuration_error != OK:
		_report_startup_failure(
			configuration_error,
			"SceneRouter configuration failed with error %d." % configuration_error,
		)
		return

	var navigation_error := SceneRouter.navigate(initial_route_id)
	if navigation_error != OK:
		SceneRouter.unconfigure(route_host)
		_report_startup_failure(
			navigation_error,
			"Initial route '%s' failed with error %d."
			% [initial_route_id, navigation_error],
		)
		return

	_started = true
	startup_succeeded.emit(initial_route_id)


func _exit_tree() -> void:
	if is_instance_valid(route_host):
		SceneRouter.unconfigure(route_host)


func is_started() -> bool:
	return _started


func get_startup_error() -> Error:
	return _startup_error


func _report_startup_failure(error: Error, message: String) -> void:
	_started = false
	_startup_error = error
	startup_failed.emit(error, message)
