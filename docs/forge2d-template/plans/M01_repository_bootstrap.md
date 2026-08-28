<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M01 Repository Bootstrap ExecPlan

This document is a living execution plan. Keep it synchronized with the work so
that a contributor who has only this worktree and this file can understand the
intent, reproduce the implementation, and finish or recover the milestone.

## Purpose / Big Picture

Forge2D needs a smallest viable repository foundation before gameplay or broad
tooling architecture is designed. After this milestone, a fresh checkout can run
and test a dependency-free Python command-line foundation, inspect an honest
environment report, and—when a compatible Godot 4 editor is available—start a
neutral bootstrap scene headlessly without editor interaction.

## Current State

The workspace started empty and was not a Git repository. No existing files,
rules, documentation index, lockfiles, CI workflows, milestone reports, or local
changes existed. Implementation used a local repository on
`feat/m01-repository-bootstrap` without a remote. After M01 validation, the
maintainer explicitly requested a commit and sync; `origin` now points to the
private `kleiveist/Forge2D-Template` repository and the baseline is on remote
`main`.

The observed local tools at the start are Python 3.11.2 and Git 2.39.5. Neither
`godot4` nor `godot` is on `PATH`. The system Python has no `pip` or `setuptools`,
so unit tests must remain runnable with the standard library and packaging smoke
validation must not be reported unless an isolated build frontend is available.

## Scope and Non-Goals

In scope are repository policies and metadata, centralized project and toolchain
configuration, an installable `g2dtool` Python package with the `g2d` entry point,
deterministic unit tests, a minimal Godot 4 bootstrap scene, a documentation
index, one repository-layout ADR, and the M01 report. All Python source and tests
live under the single `tools/` boundary.

Out of scope are gameplay design, a final runtime architecture, save systems,
asset pipelines, release builds, installers, broad demos, runtime AI, external
Godot add-ons, and merges. Remote creation, commits, and pushes were outside the
original milestone contract, then separately authorized by the maintainer after
validation. The license was deferred during M01 and selected as MIT for the
v0.1.0 public template release.

## Milestones

1. Establish the repository metadata and centralized configuration.
2. Implement and test the minimal Python package and CLI.
3. Add the Godot 4 bootstrap scene and test-mode shutdown path.
4. Finalize contributor rules, documentation, and the milestone report.
5. Run fast checks followed by the complete locally available validation set.

## Concrete Steps

All commands are run from the repository root, `/workspace`.

1. Add `.editorconfig`, `.gitattributes`, `.gitignore`, `README.md`,
   `CHANGELOG.md`, `config/project.toml`, and `config/toolchain.toml`.
2. Add `pyproject.toml` and a small package under `tools/src/g2dtool`.
   Implement repository discovery, configuration validation, `version`, and an
   honest `doctor` command using only the Python standard library at runtime.
3. Add `unittest` coverage under `tools/tests`, with injected or patched test
   doubles for external executables.
4. Add `game/project.godot`, `game/scenes/bootstrap.tscn`, and
   `game/src/bootstrap.gd`. The user argument `--test-mode` must terminate with
   exit code zero after the scene reaches `_ready()`.
5. Add the concise root `AGENTS.md`, the reusable `.agent/PLANS.md` standard,
   `docs/README.md`, the layout ADR, and the M01 report.
6. Run TOML parsing, unit tests, CLI commands, source scans, Godot smoke testing
   when available, `git diff --check`, and final status inspection.

## Progress

- [x] 2026-08-26: Inventoried the empty workspace and available toolchain.
- [x] 2026-08-26: Initialized a local repository without a remote and created
  `feat/m01-repository-bootstrap`.
- [x] 2026-08-26: Created this ExecPlan before implementation.
- [x] 2026-08-26: Added repository metadata, centralized configuration, and
  baseline documentation.
- [x] 2026-08-26: Implemented the Python CLI and deterministic tests.
- [x] 2026-08-26: Implemented the Godot bootstrap project and static consistency
  tests.
- [x] 2026-08-26: Finalized repository rules, the ExecPlan standard, and the M01
  report.
- [x] 2026-08-26: Executed every locally available validation and documented the
  unavailable Godot and packaging smoke checks without treating them as success.
- [x] 2026-08-26: Created the requested baseline commit and synchronized it to
  private remote `origin/main` without rewriting history.

## Surprises & Discoveries

- The workspace was completely empty rather than an already initialized Git
  checkout. The user explicitly chose a zero-start local repository and no clone.
- Git considers `/workspace` dubiously owned because the directory owner is
  `node` while commands run as `root`. Validation therefore uses the per-command
  option `git -c safe.directory=/workspace`; no global Git setting or ownership
  is changed.
- Godot was unavailable during M01, so its smoke command was documented for
  later rather than reported as executed successfully.
- The system Python lacks both `pip` and `setuptools`. Runtime and tests will use
  only the standard library; install/build validation remains a separate check.
- The first Python test run exposed a fault in the negative-test helper: it
  created an exception assertion without invoking the loader. After correcting
  the helper, all 15 Python tests passed; the Godot consistency tests later
  increased the suite to 18 passing tests.
- The maintainer subsequently required all Python source and tests to share a
  top-level `tools/` boundary, replacing the initially requested `tooling/` and
  `tests/tooling/` split before final validation.
- A temporary packaging environment could not be created because this Debian
  Python lacks `ensurepip`, `pip`, and setuptools. No global packages were added;
  source-mode CLI checks and packaging metadata validation were used, while the
  installation smoke remains explicitly deferred.
- Git HTTPS did not initially consume the existing `gh` login. The first push
  failed before transfer; retrying with the authenticated `gh` credential helper
  scoped to that one command succeeded without changing global Git settings.

## Decision Log

- 2026-08-26: Use `forge2d-template` as the stable template identifier and
  `Forge2D Template` as the display name for public release.
- 2026-08-26: Require Python 3.11 or newer so configuration parsing can use
  standard-library `tomllib` with no runtime dependency.
- 2026-08-26: Target Godot major version 4; M03 later verified Godot 4.7.2 for
  v0.1.0.
- 2026-08-26: Use standard-library `argparse` and `unittest`; no runtime or test
  dependencies are justified for M01.
- 2026-08-26: Select the MIT License for public v0.1.0 release.
- 2026-08-26: Following explicit maintainer direction, keep every Python file,
  including tests, under `tools/` and update packaging and documentation paths
  before final validation.
- 2026-08-26: Publish under `kleiveist/Forge2D-Template` after the explicit
  template naming and MIT license decision.

## Validation

Executed fast checks:

    python3 -c "import pathlib, tomllib; ..."
    PYTHONPATH=tools/src python3 -m unittest discover -s tools/tests -v
    PYTHONPATH=tools/src python3 -m g2dtool --help
    PYTHONPATH=tools/src python3 -m g2dtool version
    PYTHONPATH=tools/src python3 -m g2dtool doctor

TOML parsing, 18 unit tests, CLI help, and version returned zero. The real doctor
returned one because Godot is missing, which is its documented requirement
status. Error-path doubles, Python AST parsing, packaging metadata, absolute user
paths, secrets, binary data, trailing whitespace, generated artifacts, and cache
directories were also checked successfully.

The following Git check returned zero:

    git -c safe.directory=/workspace diff --check

The engine smoke was not run because no compatible executable was available:

    godot4 --headless --path game -- --test-mode

The install smoke was not run because the system Python lacks `ensurepip`, `pip`,
and setuptools. Exact evidence and reproduction commands are recorded in
`docs/forge2d-template/reports/M01_repository_bootstrap.md`.

After the maintainer-authorized sync, the local commit and remote `main` object
IDs were compared and matched exactly.

## Recovery / Idempotence

All repository files are declarative or deterministic source files. Re-running
the tests and CLI checks is safe. The Godot smoke command writes only ignored
engine state under `game/.godot/`; removing that generated directory is safe but
is not part of routine execution. Milestone setup does not alter global user Git
configuration. Delivery added only the explicit `origin` remote and private
GitHub repository requested by the maintainer. If interrupted, inspect
`git status --short` and resume at the first unchecked Progress item without
deleting unknown files.

## Outcomes & Retrospective

M01 delivered the intended minimal repository, dependency-free runtime CLI,
deterministic tests, and neutral Godot bootstrap without introducing gameplay or
release architecture. All 18 tests and every locally available audit pass. Godot
engine parsing and installed-entry-point checks were deferred in M01 because
their external prerequisites were absent. M03 later added the release gate and
verified Godot 4.7.2 for v0.1.0. The build-backend pin and future export workflow
remain deliberate follow-up decisions. The baseline commits are synchronized to
`origin/main`.
Detailed evidence is in
`docs/forge2d-template/reports/M01_repository_bootstrap.md`.
