<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M08 Documentation Architecture ExecPlan

## Purpose / Big Picture

Separate documentation about the reusable Forge2D Template from documentation a
future game will own. The root documentation hub becomes the only maintained
table of contents, while the template and five game-facing areas each have a
clear entry point.

## Current State

The existing template documentation is mixed directly below `docs/`, with
architecture, decisions, plans, reports, and tooling pages using the same level
as the documentation hub. No game-facing documentation areas exist yet.

## Scope and Non-Goals

In scope: move every existing template document below
`docs/forge2d-template/`, add empty-but-useful game documentation areas and
templates, repair links and repository rules, and validate the resulting
structure.

Out of scope: game-specific documentation, copied runtime architecture,
MkDocs, GitHub Pages, HTML, PDF, LaTeX, or any publishing pipeline. Publishing
is reserved for M09.

## Concrete Steps

1. Move the existing tooling, architecture, decisions, plans, and reports into
   `docs/forge2d-template/`.
2. Establish `docs/index.md` as the authoritative documentation hub and reduce
   `docs/README.md` to a pointer to it.
3. Create the five game-facing documentation areas with indexes and neutral
   templates; link the developer area to the inherited runtime overview.
4. Update generated index blocks, relative links, repository guidance, and
   historic path references.
5. Extend documentation-link coverage, run focused checks and `g2d check`,
   then commit and push the completed migration.

## Progress

- [x] Recorded the M08 plan and inspected the current documentation, rules,
  configuration, and link test.
- [x] Moved template documentation and established the hubs.
- [x] Added game-area indexes and neutral templates.
- [x] Repaired links and updated repository rules.
- [x] Ran focused and full dependency-free validation; review, commit, and push
  remain.

## Surprises & Discoveries

- The existing `AUTO-GENERATED:docs-index` blocks have no repository-local
  generator. They are maintained markup and must be updated with the move.
- `g2d check` already runs the Python source-hygiene test that validates links
  inside `docs/`; root-level Markdown links require explicit coverage.

## Decision Log

- 2026-08-28: Preserve the existing template overview filenames
  (`architecture.md`, `decisions.md`, `plans.md`, and `reports.md`) to minimize
  historic churn. `docs/forge2d-template/index.md` is the template entry point.
- 2026-08-28: Keep the five game areas neutral. Their templates provide shape
  without asserting facts about a game that does not exist yet.

## Validation

Executed checks:

- `python3 tools/tests/test_source_hygiene.py` — passed: 11 tests, including
  the new documentation structure and link coverage.
- `PYTHONPATH=tools/src python3 -m unittest discover -s tools/tests -v` —
  passed: 94 tests.
- `git -c safe.directory=/workspace diff HEAD --check` — passed.

`g2d check` could not be executed because `g2d` is not on `PATH`. The equivalent
`python3 tools/control.py check` was attempted and correctly failed before test
execution because this container has no `pytest` or Godot 4. The existing
ignored `.venv` cannot supply them: its `g2d` launcher has a stale machine-local
Python path. No environment packages or system software were changed solely to
make the check appear to pass.

## Recovery / Idempotence

The migration consists only of tracked Markdown moves and additions. Re-running
the checks is safe. If a move must be corrected before commit, use Git-aware
renames rather than deleting documents.

## Outcomes & Retrospective

M08 moved all existing template material below `docs/forge2d-template/` and
created a single documentation hub plus five neutral game-documentation areas.
The developer area links to the inherited runtime overview rather than copying
it. The next documentation milestone can add a publishing pipeline without
changing this information architecture.
