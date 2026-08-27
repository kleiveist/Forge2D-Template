extends Resource

@export var route_id: StringName = &""
@export var scene: PackedScene


func _init(
		p_route_id: StringName = &"",
		p_scene: PackedScene = null,
) -> void:
	route_id = p_route_id
	scene = p_scene
