<!-- AUTO-GENERATED:backlink START -->
[← Back](index.md)
<!-- AUTO-GENERATED:backlink END -->
# Mandatory GDScript Coding Standard

This standard is mandatory for every GDScript change in Forge2D Template. It
applies to production scripts and headless tests under `game/**/*.gd`. The
[official Godot GDScript style guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
is the upstream baseline; this document adds repository architecture, typing,
error, logging, and test requirements.

## Automated rules

`python tools/control.py style` checks every repository `.gd` file and reports a
path, line, column, rule code, cause, and repair direction. It is also part of
`g2d check`, so the same rules run in Linux, Windows, and macOS CI.

The checker requires:

- UTF-8 without a byte-order mark, LF line endings, a final newline, and no
  trailing whitespace;
- at most 100 characters per line after expanding tabs to four columns;
- tabs for every indentation and continuation level, never leading spaces;
- one statement per line without semicolons; and
- explicit types for every function parameter and return value, including
  `-> void`.

Generated Godot state under `.godot` is excluded and must never contain source
that belongs in version control.

## File layout and formatting

Use this order when a section exists:

1. top-level `@tool`, `extends`, and `class_name` declarations as applicable;
2. signals;
3. enums and constants;
4. exported variables, public variables, on-ready variables, then private state;
5. `_init`, Godot lifecycle callbacks, public methods, then private methods; and
6. nested classes.

Separate top-level functions with two blank lines and logical sections within a
function with one blank line. Use trailing commas in multiline calls and arrays.
Wrap long expressions with one additional tab per continuation level.

Compliant:

```gdscript
extends Node

signal route_changed(route_id: StringName)


func navigate(
		route_id: StringName,
) -> Error:
	if route_id == &"":
		return ERR_INVALID_PARAMETER
	route_changed.emit(route_id)
	return OK
```

Non-compliant:

```gdscript
extends Node
func Navigate(route_id):
    if route_id == "": return ERR_INVALID_PARAMETER;
```

## Naming and types

- Use `snake_case` for files, functions, signals, parameters, and variables;
  `PascalCase` for `class_name`, named inner classes, and preloaded scripts used
  as types; and `CONSTANT_CASE` for other constants and enum members.
- Prefix private state and methods with one underscore. Name signals as events or
  completed state changes, such as `transition_started` or `startup_failed`.
- Type all function parameters and returns. Type exported fields, public member
  state, signals, arrays, dictionaries, and resource boundaries explicitly.
  `:=` is preferred for an obvious private member or local concrete type.
- Prefer `StringName` for stable identifiers, typed resources for configuration,
  and typed collections such as `Array[StringName]`. Use `Variant` only at a
  genuinely dynamic boundary and validate it immediately.
- Do not access another feature's internals or introduce process-wide services
  outside the runtime dependency rules. Navigate through `SceneRouter` and use
  named input actions instead of physical key or controller codes.

## Documentation

- Add `##` documentation comments to reusable public classes, resources,
  signals, exported configuration, and APIs whose contract is not obvious.
- Explain ownership, lifetime, allowed failure states, units, and invariants.
  Avoid comments that merely translate the next statement into prose.
- Keep comments, identifiers, diagnostics, and test descriptions in English.
  Update a comment whenever the behavior it explains changes.

## Errors and logging

- Return a Godot `Error` for an expected recoverable failure. Validate arguments
  before mutating state and leave the object in a defined state on every exit.
- A failure signal must include enough typed context for its owner to react, such
  as the route ID, `Error`, and human-readable message.
- Report an unrecoverable composition boundary with `push_error`; use
  `push_warning` for actionable degradation. Do not log and silently continue as
  though the operation succeeded.
- Avoid repeated logging in `_process` or `_physics_process`. `print` is reserved
  for deliberate test-runner protocol output, including the CI success marker.
- Use `assert` only for developer invariants, never for invalid user content or a
  runtime condition that needs a recoverable error path.

Compliant:

```gdscript
func configure(host: Node) -> Error:
	if not is_instance_valid(host):
		return ERR_INVALID_PARAMETER
	_route_host = host
	return OK
```

Non-compliant:

```gdscript
func configure(host):
	assert(host)
	_route_host = host
	print("configured")
```

## Tests and review

- Every behavior change needs a deterministic headless regression test. Cover
  success, invalid input, lifecycle cleanup, and signal/error contracts.
- Test production scenes and scripts rather than a test-only runtime branch.
  Free created nodes and restore shared services so suites can run repeatedly.
- Tests must not depend on frame timing when a direct signal or deterministic
  await is available. Use named input actions; never embed physical device codes.
- Keep the explicit success marker in the top-level headless runner. A zero Godot
  exit without that marker is a failed repository gate.
- Reviewers enforce clear ownership, naming, documentation quality, state safety,
  intentional logging, and meaningful tests. These requirements remain binding
  even where reliable static enforcement is unavailable.

Run locally:

```text
python tools/control.py style
python tools/control.py godot4 test
python tools/control.py check
```
