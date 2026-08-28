<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M13 Repository Metadata ExecPlan

## Purpose / Big Picture

Make Forge2D Template discoverable on GitHub with concise, accurate metadata
that matches the README and can be audited after server-side changes. Owners of
repositories created from the template should also know which identity and
security URLs must be customized rather than inherited as stale Forge2D claims.

## Current State

At the start of Issue #7, the public canonical repository was already marked as
a template and used `main` as its default branch, but its GitHub description was
`null`, its topic set was empty, and its homepage was `null`. The checkout had no
versioned desired-metadata contract or focused customization guide. Draft PR #9
contains completed Issues #2, #3, #5, and #6 plus repository-side preparation
for Issue #4.
The live repository now matches the reviewed contract exactly: description and
seven topics are set, homepage remains `null`, and template/public/`main` state
is unchanged.
GitHub Actions run `33175228882` passed all eight required jobs for
implementation commit `1635354` after a controlled rerun recovered one stalled
runner cleanup.
While finalizing the issue, protected `main` advanced through PR #10 with the
M08 documentation architecture. This branch now integrates that commit without
rewriting its published history: Forge2D-owned pages live below
`docs/forge2d-template/`, and the later milestones are renumbered M09 through
M13 so M08 remains the documentation architecture milestone.

## Scope and Non-Goals

In scope are a concise description, seven focused topics, an explicit no-homepage
decision, a versioned metadata contract, dependency-free tests, a template-user
customization guide, README/documentation/release references, live GitHub API
updates and verification, local gates, and the complete pull-request CI matrix.

Out of scope are a new website, GitHub Pages, social preview artwork, sponsoring,
discussions, repository renaming or transfer, visibility/default-branch changes,
feature toggles, search-engine promises, analytics, promotional topics, new
dependencies, and changing the existing template-repository flag.

## Concrete Steps

1. Audit Issue #7, README/project identity, documentation/test conventions,
   current GitHub topic rules, and live repository metadata.
2. Add `.github/repository-metadata.json` as the reviewed description, null
   homepage, and exact topic contract.
3. Document canonical values, rationale, manual/API audit, topic limits, and the
   metadata/security/branch-protection changes required in downstream projects.
4. Add dependency-free tests for contract shape, concise README consistency,
   topic uniqueness/format/limits, intentional homepage omission, and entry-point
   links.
5. Update README, documentation indices, changelog, release notes, and plan index.
6. Run focused tests, source style, all Python tests, the complete `g2d check`,
   release preparation dry-run, and Git hygiene checks.
7. Update the live description and replace all topics through GitHub's API while
   leaving homepage/template/default branch untouched; verify exact values from
   a fresh API response.
8. Commit with an emoji-prefixed English subject, push to draft PR #9, wait at
   least three minutes before every Actions inspection, and iterate until all
   eight required jobs are green.
9. Record remote evidence, add `Closes #7` to the PR, and comment on Issue #7.
   Then begin Issue #8 automatically under the user's explicit instruction that
   no additional `J` confirmation is required while they are away.

## Progress

- [x] 2026-08-28: Received explicit approval to begin Issue #7 and confirmed a
  clean, synchronized `feat/release-readiness` branch.
- [x] 2026-08-28: Audited the issue, repository identity, current GitHub topic
  constraints, API behavior, and live metadata values.
- [x] 2026-08-28: Added the metadata contract, six focused tests, customization
  guide, README/documentation/release updates, and entry-point links.
- [x] 2026-08-28: Passed 16 focused metadata/link checks, source style for 44
  files, 170 Python tests, the real Godot 4.7.2 suite, and the complete local
  repository gate.
- [x] 2026-08-28: Applied the exact description and seven topics through the
  GitHub API, then verified homepage `null`, template `true`, visibility
  `public`, and default branch `main` remained unchanged.
- [x] 2026-08-28: Passed all eight pull-request CI jobs in run `33175228882`
  for implementation commit `1635354`.
- [x] 2026-08-28: Integrated protected `main` commit `7e398ec` without a
  force-push, retained its documentation architecture, migrated Forge2D-owned
  additions into the new hierarchy, and passed 52 focused integration tests.
- [x] 2026-08-28: Re-ran the complete post-merge local gate: Doctor 12/12,
  style for 44 files, 171 Python tests, Godot 4.7.2 integration, release
  preparation dry-run, and Git whitespace checks all passed.

## Surprises & Discoveries

- 2026-08-28: The repository was already correctly public, template-enabled,
  and based on `main`; Issue #7 needs no unrelated feature or identity mutation.
- 2026-08-28: GitHub topics are always public and have explicit lowercase,
  hyphen, 50-character, and 20-topic constraints. Seven focused discovery terms
  leave ample room without adding synonymous or speculative tags.
- 2026-08-28: A homepage pointing back to the repository adds no maintained
  destination and falsely implies a separate project site. An explicit `null`
  is more accurate until a canonical external destination exists.
- 2026-08-28: The first CI attempt completed seven jobs but a macOS runner hung
  beyond the 35-minute job limit in GitHub's `Post Check out repository` cleanup
  after repository steps had finished. Cancelling the stalled attempt and
  rerunning the unchanged commit produced eight green jobs, confirming an
  infrastructure cleanup fault rather than a repository failure.
- 2026-08-28: Protected `main` advanced during Issue #7 through documentation
  architecture PR #10. A normal merge was safer than rebasing the already
  published issue branch; preserving M08 required renumbering this branch's five
  later ExecPlans and migrating their pages into the new ownership hierarchy.

## Decision Log

- 2026-08-28: Use `Minimal Godot 4 2D game template with repository-local
  Python tooling for setup, checks, exports, and releases.` as the canonical
  description. It is concise, factual, and consistent with the README workflow.
- 2026-08-28: Use exactly `2d-game`, `game-development`, `game-template`,
  `gdscript`, `godot`, `godot-4`, and `python`, sorted for deterministic review.
- 2026-08-28: Leave homepage unset and preserve `is_template: true`, public
  visibility, and default branch `main`.
- 2026-08-28: Store desired metadata as JSON under `.github/` rather than add an
  application command. Standard-library tests can validate it, while GitHub's
  API remains the source of truth for live state.
- 2026-08-28: Add no dependency. Python `json`, `re`, existing repository tests,
  and direct GitHub API verification cover the contract without supply-chain
  expansion.
- 2026-08-28: Integrate concurrent protected-main work with a merge commit rather
  than rewrite the shared branch, and treat the M08 documentation architecture
  as authoritative for all paths and milestone numbering.

## Validation

| Command / check | Result |
| --- | --- |
| `.venv/bin/python -m pytest tools/tests/test_repository_metadata.py tools/tests/test_source_hygiene.py -q` | Passed; 16 tests |
| `python tools/control.py style` | Passed; 44 source files |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 170 tests |
| `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 44/44, 170 tests, Godot integration |
| `python tools/control.py release prepare --dry-run` | Passed; existing v0.1.0 assets verified, no changes |
| `git diff --check` | Passed |
| Fresh GitHub repository API response | Passed; exact description/topics, homepage `null`, template `true`, public, `main` |
| Pull-request CI run `33175228882` for commit `1635354` | Passed on controlled rerun; all eight Linux, Windows, and macOS jobs |
| Focused post-merge documentation, style, release, community, and metadata tests | Passed; 52 tests |
| Post-merge `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 44/44, 171 tests, Godot integration |
| Post-merge `python tools/control.py release prepare --dry-run` | Passed; existing v0.1.0 assets verified, no changes |
| Post-merge `git diff --cached --check` and `git diff --check` | Passed |

## Recovery / Idempotence

Description updates replace one string and the topics endpoint replaces the
complete set, so reapplying the reviewed values is idempotent. The homepage is
not mutated. If an API call partially succeeds, compare the fresh response with
the JSON contract and reapply only the divergent field. Do not use repository
transfer, rename, visibility, template, or branch APIs as recovery for metadata
drift. Versioned documentation can be reverted normally; coordinate any live
rollback with the reviewed replacement values.

## Outcomes & Retrospective

The local and live metadata baseline is complete without new dependencies or an
invented homepage. GitHub now describes and classifies the canonical repository
accurately, the versioned contract makes drift reviewable, and downstream owners
have an explicit checklist for replacing identity, URLs, and server-side policy.
Pull-request run `33175228882` provides the final implementation evidence with
all eight jobs green for commit `1635354`.
