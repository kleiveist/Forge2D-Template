extends Control
class_name Forge2DBootstrap

const TEST_MODE_ARGUMENT := "--test-mode"
const EXIT_SUCCESS := 0


func _ready() -> void:
	if OS.get_cmdline_user_args().has(TEST_MODE_ARGUMENT):
		print("Forge2D bootstrap smoke test: ready")
		get_tree().quit(EXIT_SUCCESS)
