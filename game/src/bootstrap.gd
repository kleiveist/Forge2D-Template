extends Control
class_name Forge2DTemplateBootstrap

signal composition_failed(error: Error, message: String)

@export var application_root_scene: PackedScene

var _application_root: Node


func _ready() -> void:
	if application_root_scene == null:
		_report_composition_failure(
			ERR_FILE_NOT_FOUND,
			"ApplicationRoot scene is not configured.",
		)
		return

	var application_root := application_root_scene.instantiate()
	if application_root == null:
		_report_composition_failure(
			ERR_CANT_CREATE,
			"ApplicationRoot scene could not be instantiated.",
		)
		return

	_application_root = application_root
	if application_root.has_signal("startup_failed"):
		application_root.connect(
			"startup_failed",
			Callable(self, "_on_application_startup_failed"),
		)
	add_child(application_root)

	if application_root.get_parent() != self:
		_report_composition_failure(
			ERR_CANT_CREATE,
			"ApplicationRoot did not attach to Bootstrap.",
		)


func get_application_root() -> Node:
	return _application_root if is_instance_valid(_application_root) else null


func _on_application_startup_failed(error: Error, message: String) -> void:
	_report_composition_failure(error, message)


func _report_composition_failure(error: Error, message: String) -> void:
	push_error("Bootstrap composition failed: %s" % message)
	composition_failed.emit(error, message)
