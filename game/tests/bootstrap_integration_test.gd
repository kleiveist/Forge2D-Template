extends SceneTree

const EXPECTED_MESSAGE := "Forge2D Template\nRepository bootstrap"
const TEST_SUITES := [
	"res://tests/runtime/scene_router_test.gd",
	"res://tests/runtime/application_root_test.gd",
	"res://tests/runtime/input_map_test.gd",
	"res://tests/runtime/touch_action_adapter_test.gd",
]

var failures: PackedStringArray = []


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	await process_frame
	for suite_path in TEST_SUITES:
		await _run_suite(suite_path)
	await _test_bootstrap_contract()
	_finish()


func _run_suite(suite_path: String) -> void:
	var completion_sentinel := "runtime suite completes: %s" % suite_path
	failures.append(completion_sentinel)
	var suite_script := load(suite_path) as Script
	_expect(suite_script != null, "runtime suite loads: %s" % suite_path)
	if suite_script == null:
		return
	_expect(suite_script.can_instantiate(), "runtime suite parses: %s" % suite_path)
	if not suite_script.can_instantiate():
		return
	var suite: Variant = suite_script.new()
	var suite_failures: PackedStringArray = await suite.run(self)
	var sentinel_index := failures.find(completion_sentinel)
	if sentinel_index >= 0:
		failures.remove_at(sentinel_index)
	failures.append_array(suite_failures)


func _test_bootstrap_contract() -> void:
	var main_scene_path := str(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(not main_scene_path.is_empty(), "project configures a main scene")
	if main_scene_path.is_empty():
		return

	var main_scene := load(main_scene_path) as PackedScene
	_expect(main_scene != null, "configured main scene can be loaded")
	if main_scene == null:
		return

	var bootstrap := main_scene.instantiate()
	var composition_failures: Array[Array] = []
	bootstrap.composition_failed.connect(
		func(error: Error, message: String) -> void:
			composition_failures.append([error, message])
	)
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

	_expect(composition_failures.is_empty(), "Bootstrap reports no composition failure")
	_expect(bootstrap.get_child_count() == 1, "Bootstrap creates exactly one child")

	var application_root := bootstrap.get_node_or_null("ApplicationRoot")
	_expect(application_root != null, "Bootstrap creates ApplicationRoot")
	if application_root != null:
		var application_script: Script = application_root.get_script()
		_expect(application_script != null, "ApplicationRoot has an attached script")
		if application_script != null:
			_expect(
				application_script.resource_path == "res://scenes/app/application_root.gd",
				"Bootstrap uses the production ApplicationRoot",
			)
		_expect(application_root.is_started(), "ApplicationRoot completes startup")
		_expect(
			application_root.get_node_or_null("PersistentUI") is CanvasLayer,
			"ApplicationRoot has persistent UI CanvasLayer",
		)
		_expect(
			application_root.get_node_or_null("TransitionLayer") is CanvasLayer,
			"ApplicationRoot has transition CanvasLayer",
		)

	var route_host := bootstrap.get_node_or_null("ApplicationRoot/RouteHost")
	_expect(route_host != null, "ApplicationRoot owns RouteHost")
	if route_host != null:
		_expect(route_host.get_child_count() == 1, "RouteHost owns one active route")

	var message := bootstrap.get_node_or_null(
		"ApplicationRoot/RouteHost/TemplateHome/Content/Message"
	) as Label
	_expect(message != null, "neutral initial route has a Message Label")
	if message != null:
		_expect(message.text == EXPECTED_MESSAGE, "message text matches the route contract")

	bootstrap.queue_free()
	await process_frame
	var scene_router := root.get_node_or_null("SceneRouter")
	_expect(scene_router != null, "SceneRouter is registered as an Autoload")
	if scene_router != null:
		_expect(not scene_router.is_configured(), "Bootstrap shutdown clears SceneRouter")
		_expect(scene_router.get_current_route() == null, "shutdown releases route reference")


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
