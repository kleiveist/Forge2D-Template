<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M07 Main Branch Protection ExecPlan

## Purpose / Big Picture

Protect GitHub's `main` branch so every change arrives through a pull request and
the complete Linux, Windows, and macOS CI matrix succeeds before merge. Preserve
the exact external settings in repository documentation and a credential-free
policy payload so forks can reproduce them safely.

## Current State

The previous installer CI repair is green in all eight jobs. The repository had
no branch protection rule, and `kleiveist` is its only collaborator. The `main`
rule is now active through the GitHub API while policy documentation and its
local validation are being completed on `chore/main-branch-protection`.

## Scope and Non-Goals

In scope are classic GitHub branch protection for the exact `main` branch,
strict GitHub Actions checks, pull-request-only changes, admin enforcement,
linear history, conversation resolution, force-push/deletion prevention, a
reviewable JSON policy, tests, and manual setup documentation. Organization
rulesets, merge queues, deployments, signed commits, and Code Owners are out of
scope because this is a personal, single-collaborator repository without those
supporting workflows. No dependency is added.

## Concrete Steps

1. Inspect repository permissions, collaborators, existing protection, and the
   successful check-run names and provider.
2. Create a topic branch before repository changes and apply a no-bypass `main`
   protection rule through the authenticated GitHub API.
3. Record the exact API payload plus manual GitHub UI instructions, maintenance
   sequencing, and the solo-reviewer limitation.
4. Add repository tests for the policy's required checks and safety controls,
   then run focused tests and the standard `g2d check` gate.
5. Commit with an emoji-prefixed English message, push the topic branch, open a
   pull request, and inspect CI no more frequently than once every three minutes.
6. Repeat fixes on the topic branch until all pull-request jobs pass, then audit
   the live protection rule and repository state.

## Progress

- [x] 2026-08-28: Confirmed installer repair workflow `33161920298` passed all
  eight jobs.
- [x] 2026-08-28: Confirmed `main` was unprotected, identified one collaborator,
  and captured all eight successful GitHub Actions contexts and app ID `15368`.
- [x] 2026-08-28: Created `chore/main-branch-protection` and applied strict,
  no-bypass protection to `main` through the GitHub API.
- [x] 2026-08-28: Added the reviewable policy payload, manual GitHub setup and
  maintenance guide, documentation indexes, and policy unit tests.
- [x] 2026-08-28: Passed focused tests, all 93 Python tests, and the standard
  release gate with checksum-verified Godot 4.7.2.
- [ ] Pass the pull-request CI loop.
- [ ] Audit final GitHub protection and clean worktree state.

## Surprises & Discoveries

- 2026-08-28: Requiring one approval while only the pull-request author can
  review would make every pull request unmergeable when admin bypass is disabled.
- 2026-08-28: The CI workflow exposes eight matrix job contexts rather than one
  aggregate check, so every context is part of the current protection contract.

## Decision Log

- 2026-08-28: Require a pull request but zero approvals until an independent
  reviewer exists; document one approval as the next manual hardening step.
- 2026-08-28: Require all eight checks in strict mode and bind them to GitHub
  Actions app ID `15368`, preventing another status provider from satisfying the
  rule under the same name.
- 2026-08-28: Enforce the rule for administrators, require linear history and
  resolved conversations, and disallow force pushes and deletion.
- 2026-08-28: Keep the exact API payload under `.github/` but leave credentials
  and execution outside Git so external state changes remain explicit.

## Validation

| Command / check | Result |
| --- | --- |
| GitHub Actions workflow `33161920298` | Passed; all 8 jobs |
| Pre-change protection query | Confirmed `main` returned `404 Branch not protected` |
| Protection API update | Passed; strict checks, PR rule, admin enforcement, linear history, conversation resolution, force-push/deletion prevention returned enabled |
| `.venv/bin/python -m pytest tools/tests/test_branch_protection.py tools/tests/test_source_hygiene.py -q` | Passed; 13 tests |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 93 tests |
| `g2d check` with checksum-verified Godot 4.7.2 | Passed; Doctor 12/12, 93 tests, real headless integration |
| Pull-request CI | Pending; poll no more frequently than every 3 minutes |
| Final protection audit | Pending |

## Recovery / Idempotence

Reapplying `.github/branch-protection-main.json` is idempotent and replaces the
managed `main` protection settings with the reviewed values. Administrators can
recover from a renamed or removed check by restoring the old CI context or
updating the required-check list through GitHub before attempting another merge.
Removing protection is intentionally not part of normal recovery.

## Outcomes & Retrospective

Pending pull-request CI and final server-side audit.
