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
- [x] 2026-08-27: Completed local Python, package-artifact, and CI-YAML
  validation; real Godot execution remains for CI because no editor is installed
  in this audit environment.

## Surprises & Discoveries

- The local audit environment has neither Godot nor pytest, so the integration
  command can be inspected but not executed locally.

## Decision Log

- 2026-08-27: Keep the Godot test dependency-free by using a repository-owned
  `SceneTree` test runner instead of adding a third-party framework.
- 2026-08-27: Test the built wheel rather than only an editable installation so
  packaging and console-script defects cannot be hidden by the checkout source.

## Validation

| Command / check | Result |
| --- | --- |
| Temporary-wheel install, `g2d --help`, and `g2d version` | Passed; import resolved from the isolated environment's `site-packages` |
| Temporary wheel plus `pytest tools/tests -q` | Passed; 57 tests |
| `python -m unittest discover -s tools/tests` | Passed; 57 tests |
| Python source compilation | Passed |
| CI YAML parsing and `git diff --check` | Passed |
| Godot integration test | Not run locally; Godot is unavailable and CI runs it on all configured platforms |

## Recovery / Idempotence

All changes are source and CI configuration changes. The CI wheelhouse and
artifact virtual environment exist only inside a job and can be recreated.

## Outcomes & Retrospective

The release gate now fails for a missing integration test runner and for failing
Doctor, Python-test, or Godot-test steps. CI verifies both the source-tree gate
and the console script generated from the built wheel.
