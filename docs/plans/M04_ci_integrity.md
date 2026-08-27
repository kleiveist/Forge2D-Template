# M04 CI Integrity Hardening ExecPlan

## Purpose / Big Picture

Make a green CI result demonstrate real bootstrap behavior, correct gate failure
propagation, and usability of the packaged `g2d` command.

## Current State

The prior Godot smoke check asked the application to exit successfully in a
test-only branch. CI installed the package but invoked the source-tree bootstrap
instead of the installed command. Gate tests did not cover failing Doctor,
Python, or Godot child steps.

## Scope and Non-Goals

In scope are the repository test runner, gate behavior and tests, packaged CLI
validation in CI, and user-facing documentation. Gameplay features, exports,
and new dependencies are out of scope.

## Concrete Steps

1. Replace the application test-mode shutdown with a dedicated Godot integration
   test runner that instantiates and validates the production bootstrap scene.
2. Make a missing test runner a release-gate failure rather than using a fallback.
3. Add negative gate tests for Doctor, Python-test, and Godot-test failures.
4. Build a wheel in every CI job, install it into an isolated virtual environment,
   and execute the installed `g2d` entry point.
5. Run focused tests and available static validation; record environment limits.

## Progress

- [x] 2026-08-27: Replaced the in-application `--test-mode` success path with a
  dedicated integration test runner.
- [x] 2026-08-27: Added explicit missing-runner failure handling and negative
  release-gate tests.
- [x] 2026-08-27: Added wheel-install and installed-CLI validation to both CI job
  types.
- [x] 2026-08-27: Repaired the standalone Godot runner after CI run #9 exposed
  an unresolved global script class, and required its explicit success marker.
- [x] 2026-08-27: Completed local Python, package-artifact, and CI-YAML
  validation, including a real Godot 4.7.2 integration-test run.

## Surprises & Discoveries

- CI run #9 found that a script started with Godot's `--script` option cannot
  resolve the bootstrap script's global `class_name` during parsing.
- macOS returned exit code 0 after the same Godot parse error, so an exit code
  alone cannot establish that the integration test actually ran.

## Decision Log

- 2026-08-27: Keep the Godot test dependency-free by using a repository-owned
  `SceneTree` test runner instead of adding a third-party framework.
- 2026-08-27: Test the built wheel rather than only an editable installation so
  packaging and console-script defects cannot be hidden by the checkout source.
- 2026-08-27: Validate the bootstrap's attached script resource rather than its
  global class name so the standalone runner parses on every platform.
- 2026-08-27: Require the test runner's success marker in addition to exit code
  so an engine parse error cannot produce a green macOS gate.

## Validation

| Command / check | Result |
| --- | --- |
| Temporary-wheel install, `g2d --help`, and `g2d version` | Passed; import resolved from the isolated environment's `site-packages` |
| Temporary wheel plus `pytest tools/tests -q` | Passed; 60 tests |
| Isolated-wheel `g2d check` with Godot 4.7.2 on `PATH` | Passed; Doctor, 60 Python tests, marker-validated Godot integration test |
| `python -m unittest discover -s tools/tests` | Passed; 60 tests |
| Python source compilation | Passed |
| CI YAML parsing and `git diff --check` | Passed |
| Godot 4.7.2 headless integration test | Passed; production main scene loaded and emitted the required success marker |
| Gate handling of exit code 0 without marker | Passed; unit test returns failure even when stderr contains only a parse error |

## Recovery / Idempotence

All changes are source and CI configuration changes. The CI wheelhouse and
artifact virtual environment exist only inside a job and can be recreated.

## Outcomes & Retrospective

The release gate now fails for a missing integration test runner, a missing
success marker, and failing Doctor, Python-test, or Godot-test steps. CI verifies
both the source-tree gate and the console script generated from the built wheel.
