extends RefCounted

const APPLICATION_ROOT_SCENE := preload("res://scenes/app/application_root.tscn")

var failures := PackedStringArray()


func run(tree: SceneTree) -> PackedStringArray:
	await _test_successful_startup_and_shutdown(tree)
	await _test_failed_initial_route(tree)
	return failures


func _test_successful_startup_and_shutdown(tree: SceneTree) -> void:
	var scene_router := tree.root.get_node_or_null("SceneRouter")
	_expect(scene_router != null, "SceneRouter Autoload is present")
	if scene_router == null:
		return

	var application_root := APPLICATION_ROOT_SCENE.instantiate()
	var started_ids: Array[StringName] = []
	application_root.startup_succeeded.connect(
		func(route_id: StringName) -> void:
			started_ids.append(route_id)
	)
	tree.root.add_child(application_root)

	_expect(application_root.is_started(), "ApplicationRoot reports successful startup")
	_expect(
		started_ids == [&"template_home"],
		"ApplicationRoot reports its neutral initial route",
	)
	var route_host := application_root.get_node_or_null("RouteHost")
	_expect(route_host != null, "ApplicationRoot owns RouteHost")
	_expect(
		application_root.get_node_or_null("PersistentUI") is CanvasLayer,
		"ApplicationRoot owns persistent UI CanvasLayer",
	)
	_expect(
		application_root.get_node_or_null("TransitionLayer") is CanvasLayer,
		"ApplicationRoot owns transition CanvasLayer",
	)
	if route_host != null:
		_expect(route_host.get_child_count() == 1, "ApplicationRoot starts one route")
		var initial_route := route_host.get_child(0) if route_host.get_child_count() == 1 else null
		_expect(initial_route is Control, "neutral initial route is Control-based")
		if initial_route != null:
			_expect(initial_route.name == "TemplateHome", "neutral initial route is active")
	_expect(scene_router.get_route_host() == route_host, "SceneRouter uses application RouteHost")
	_expect(
		scene_router.get_current_route_id() == &"template_home",
		"SceneRouter tracks the neutral route ID",
	)

	application_root.queue_free()
	await tree.process_frame
	_expect(not scene_router.is_configured(), "ApplicationRoot shutdown clears SceneRouter")
	_expect(scene_router.get_current_route() == null, "shutdown releases active-route reference")


func _test_failed_initial_route(tree: SceneTree) -> void:
	var scene_router := tree.root.get_node_or_null("SceneRouter")
	if scene_router == null:
		return

	var application_root := APPLICATION_ROOT_SCENE.instantiate()
	application_root.initial_route_id = &"missing_route"
	var startup_failures: Array[Array] = []
	application_root.startup_failed.connect(
		func(error: Error, message: String) -> void:
			startup_failures.append([error, message])
	)
	tree.root.add_child(application_root)

	_expect(not application_root.is_started(), "invalid initial route fails startup")
	_expect(
		application_root.get_startup_error() == ERR_DOES_NOT_EXIST,
		"startup retains the initial navigation error",
	)
	_expect(startup_failures.size() == 1, "startup failure is observable exactly once")
	var route_host := application_root.get_node_or_null("RouteHost")
	if route_host != null:
		_expect(route_host.get_child_count() == 0, "failed startup leaves RouteHost empty")
	_expect(not scene_router.is_configured(), "failed startup releases SceneRouter configuration")

	application_root.queue_free()
	await tree.process_frame


func _expect(condition: bool, description: String) -> void:
	if not condition:
		failures.append("ApplicationRoot: %s" % description)
