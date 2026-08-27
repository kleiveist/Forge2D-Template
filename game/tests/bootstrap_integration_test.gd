extends SceneTree

const EXPECTED_MESSAGE := "Forge2D Template\nRepository bootstrap"

var failures: PackedStringArray = []


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var main_scene_path := str(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(not main_scene_path.is_empty(), "project configures a main scene")
	if main_scene_path.is_empty():
		_finish()
		return

	var main_scene := load(main_scene_path) as PackedScene
	_expect(main_scene != null, "configured main scene can be loaded")
	if main_scene == null:
		_finish()
		return

	var bootstrap := main_scene.instantiate()
	root.add_child(bootstrap)
	await process_frame

	_expect(bootstrap is Control, "main scene is a Control")
	_expect(bootstrap.get_parent() == root, "main scene remains attached after ready")
	var bootstrap_script: Script = bootstrap.get_script()
	_expect(bootstrap_script != null, "main scene has an attached script")
	if bootstrap_script != null:
		_expect(
			bootstrap_script.resource_path == "res://src/bootstrap.gd",
			"main scene uses the bootstrap script",
		)

	var background := bootstrap.get_node_or_null("Background") as ColorRect
	_expect(background != null, "main scene has a Background ColorRect")

	var content := bootstrap.get_node_or_null("Content") as CenterContainer
	_expect(content != null, "main scene has a Content CenterContainer")

	var message := bootstrap.get_node_or_null("Content/Message") as Label
	_expect(message != null, "main scene has a Message Label")
	if message != null:
		_expect(message.text == EXPECTED_MESSAGE, "message text matches the bootstrap contract")

	bootstrap.queue_free()
	await process_frame
	_finish()


func _expect(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)


func _finish() -> void:
	if failures.is_empty():
		print("Forge2D bootstrap integration test: passed")
		quit(0)
		return

	for failure in failures:
		push_error("Bootstrap integration test failed: %s" % failure)
	quit(1)
