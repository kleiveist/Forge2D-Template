# M03 Release v0.1.0 ExecPlan

This document is a living execution plan for publishing Forge2D Template v0.1.0.

## Purpose / Big Picture

Forge2D Template needs a consistent public template identity, a working local
release gate, CI coverage for Python and Godot smoke checks, and a tagged GitHub
release. After this milestone, a fresh checkout should expose `g2d` as the main
tooling command while the repository and Godot project identify as Forge2D
Template.

## Current State

The repository is on `main` with remote `kleiveist/Forge2D`. The Python package
is already `g2dtool` at version `0.1.0`. Public naming still uses standalone
Forge2D in docs, CLI aliases, config, and the Godot project. `g2d check` is
planned but not implemented. Godot 4.7.2 is available locally as `godot4` for
release validation.

## Scope and Non-Goals

In scope are naming, metadata, license, dependency declaration, local check
orchestration, CI, documentation, milestone reports, release commit, repository
rename, template marking, tag, and GitHub release. The internal package name
`g2dtool` and main command `g2d` remain unchanged.

Out of scope are gameplay features, export builds, new runtime dependencies,
asset pipelines, visibility changes beyond the template setting, and history
rewrites.

## Concrete Steps

1. Add the missing ExecPlan standard and keep this M03 plan current.
2. Rename public identity to Forge2D Template / Forge2D-Template /
   `forge2d-template`.
3. Define pytest as a development dependency and ensure `install` installs it.
4. Implement `python tools/control.py check` to run Doctor, Python tests, and
   the Godot headless smoke test with a non-zero failure exit.
5. Add MIT license, CI, M02 closure, M03 report, and documentation updates.
6. Run install, doctor, check, Python tests, Godot headless smoke, project start,
   and Git hygiene checks.
7. Commit, push `main`, rename the GitHub repository, mark it as a template,
   create tag `v0.1.0`, and publish the GitHub release.

## Progress

- [x] 2026-08-26: Confirmed clean `main`, GitHub auth, and current remote.
- [x] 2026-08-26: Installed local prerequisites for `python`, pip/venv, and
  Godot 4.7.2 validation without adding generated files to Git.
- [x] 2026-08-26: Renamed public identity and aliases.
- [x] 2026-08-26: Implemented release gate.
- [x] 2026-08-26: Updated docs, CI, license, and reports.
- [x] 2026-08-26: Ran required local checks.
- [ ] Publish GitHub release.

## Surprises & Discoveries

- The container initially had `python3` but no `python`, pip, or usable `.venv`
  interpreter path. System packages were installed so the documented `python
  tools/control.py ...` commands can be verified exactly.
- `/workspace/.venv` existed as ignored generated state and pointed at the
  missing `/usr/bin/python`; release validation treats it as disposable local
  environment state but does not commit it.

## Decision Log

- 2026-08-26: Keep `g2dtool` and `g2d`; replace legacy `forge2d`/`Forge2D`
  command aliases with `forge2d-template`/`Forge2D-Template`.
- 2026-08-26: Use Godot 4.7.2 as the tested editor/runtime version for v0.1.0.

## Validation

Executed from `/workspace`:

| Command | Result |
| --- | --- |
| `python tools/control.py install` | Passed; repaired/used `.venv`, installed editable tooling and `pytest>=8,<9`, and finished with Doctor success |
| `python tools/control.py doctor` | Passed; 12 passed, 0 warnings, 0 failures |
| `.venv/bin/python -m pytest tools/tests` | Passed; 50 tests |
| `python tools/control.py check` | Passed; Doctor, Python tests, and Godot headless smoke |
| `godot4 --headless --path game -- --test-mode` | Passed with Godot 4.7.2 |
| `python tools/control.py godot4 test` | Passed with Godot 4.7.2 |
| `xvfb-run -a python tools/control.py godot4 run -- --test-mode` | Passed; normal project start path in a virtual display |
| `git diff --check` | Passed |

## Recovery / Idempotence

All source changes are text changes. Re-running `python tools/control.py install`
is intended to be idempotent. GitHub publication steps should never force-push
or rewrite history; if a remote step fails, keep the local commit and report the
single remaining command.

## Outcomes & Retrospective

To be completed after release publication.
