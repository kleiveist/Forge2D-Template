<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M12 Community Health ExecPlan

## Purpose / Big Picture

Give code contributors, bug reporters, feature proposers, reviewers, and security
researchers clear repository-native paths that match the actual protected-main,
required-CI, local-tooling, and private-disclosure policies. A first-time
contributor should be able to choose the right route, prepare a change, validate
it, and request review without guessing or exposing sensitive information.

## Current State

At the start of Issue #6, README guidance covered local setup and code checks,
but the repository had no `CONTRIBUTING.md`, `SECURITY.md`, pull-request
template, issue forms, or issue-chooser policy. GitHub private vulnerability
reporting was disabled, so the desired private reporter route was not yet
available. Draft PR #9 contains completed Issues #2, #3, and #5 plus the
repository-side preparation for Issue #4. Private reporting is now enabled, and
CI run `33174259832` passed all eight required jobs for implementation commit
`21c3308`.

## Scope and Non-Goals

In scope are contribution and security policies, a single active pull-request
template, focused bug and feature issue forms, a deliberate issue-chooser
configuration, private vulnerability reporting for the canonical repository,
links from repository entry points, dependency-free contract tests, changelog
and release-note updates, and local/remote repository validation.

Out of scope are a code of conduct, discussion forum, support service, public
security email address, bug bounty, service-level guarantee, automatic labeling,
new GitHub Actions, new dependencies, organization-wide community defaults, and
community files for downstream forks whose owners must configure their own
private reporting route.

## Concrete Steps

1. Audit Issue #6, current setup/style/branch-protection documentation, CI jobs,
   repository tests, GitHub issue-form syntax, and the live private-reporting
   setting.
2. Add `CONTRIBUTING.md` with issue selection, safe setup, coding, focused and
   full validation, commit, pull-request, review, dependency, and documentation
   expectations.
3. Add `SECURITY.md` with supported refs, a private GitHub advisory route,
   useful report contents, response targets, coordinated disclosure, and
   downstream-fork guidance.
4. Add the pull-request template, bug form, feature form, and chooser config;
   disable external blank issues and expose the private security route.
5. Add dependency-free tests for files, schema contracts, collected fields,
   safety language, workflow accuracy, chooser policy, and relative links.
6. Link the community files from README and both documentation entry points,
   index this plan, and update release-facing documentation.
7. Run focused tests, source style, the complete `g2d check` gate, release
   preparation dry-run, and Git hygiene checks.
8. Enable private vulnerability reporting through the GitHub API, commit with
   an emoji-prefixed English subject, push to PR #9, wait at least three minutes
   before each Actions inspection, and iterate until all eight jobs are green.
9. Record remote evidence, add `Closes #6` to the PR, comment on Issue #6, and
   ask for `J` before beginning Issue #7.

## Progress

- [x] 2026-08-28: Received explicit approval to begin Issue #6 and confirmed a
  clean, synchronized `feat/release-readiness` branch.
- [x] 2026-08-28: Audited repository rules, contributor-facing setup/style/
  protection guidance, existing tests, current GitHub schemas, and the live
  private-reporting setting.
- [x] 2026-08-28: Added community policies, active PR/issue templates, chooser
  policy, dependency-free contracts, release-facing updates, and entry-point
  links.
- [x] 2026-08-28: Passed 20 focused community/link checks, source style for 43
  files, 164 Python tests, the real Godot 4.7.2 suite, and the complete local
  repository gate.
- [x] 2026-08-28: Enabled private vulnerability reporting through the GitHub
  API and verified the live setting reports `enabled: true`.
- [x] 2026-08-28: Passed all eight pull-request CI jobs in run `33174259832`
  for implementation commit `21c3308`.

## Surprises & Discoveries

- 2026-08-28: GitHub issue forms remain a public-preview schema. Keep their
  structure deliberately small and protect required fields with repository
  contracts so schema drift produces a focused review surface.
- 2026-08-28: The canonical repository had private vulnerability reporting
  disabled. A `SECURITY.md` link alone would therefore not provide the accepted
  private reporter route; the live setting must be enabled and audited too.
- 2026-08-28: GitHub still exposes blank issues to users with write access when
  `blank_issues_enabled` is false. The policy can focus external reports without
  blocking maintainers from creating an exceptional untemplated issue.
- 2026-08-28: This development container has no standalone Ruby/YAML parser.
  Installing one solely for three declarative files would violate the
  dependency-minimization decision, so focused schema contracts provide local
  validation and GitHub remains the native parser after merge to default.

## Decision Log

- 2026-08-28: Disable blank issues for external contributors. The bug and
  feature forms cover public work; the chooser links security reporters to a
  private route. Document GitHub's maintainer-only exception explicitly.
- 2026-08-28: Use no public email address or personal credential. GitHub private
  vulnerability reports keep the reporter, maintainers, discussion, and patch
  coordination inside the repository advisory workflow.
- 2026-08-28: Set response targets rather than guarantees: acknowledge within
  three business days, complete initial triage within seven business days, and
  provide weekly status while remediation is active.
- 2026-08-28: Add no YAML parser or template action. Exact dependency-free
  Python contracts plus GitHub's native parser on protected `main` cover these
  small declarative files without expanding supply-chain risk.
- 2026-08-28: Require concise emoji-prefixed English commit subjects to match
  the repository's active contribution convention.

## Validation

| Command / check | Result |
| --- | --- |
| `.venv/bin/python -m pytest tools/tests/test_community_health.py tools/tests/test_source_hygiene.py -q` | Passed; 20 tests |
| `python tools/control.py style` | Passed; 43 source files |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 164 tests |
| `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 43/43, 164 tests, Godot integration |
| `python tools/control.py release prepare --dry-run` | Passed; existing v0.1.0 assets verified, no changes |
| `git diff --check` | Passed |
| GitHub private vulnerability reporting API audit | Passed; `enabled: true` |
| Pull-request CI run `33174259832` for commit `21c3308` | Passed; all eight Linux, Windows, and macOS jobs |

## Recovery / Idempotence

The community files are versioned text and can be revised or reverted together.
Enabling private vulnerability reporting is repository metadata and is
idempotent through the GitHub API; disabling it would remove the public reporter
entry point and must be paired with an approved replacement private contact
before changing `SECURITY.md` or the issue chooser. Never move a received
vulnerability into a public issue merely to simplify recovery.

## Outcomes & Retrospective

The local community-health baseline is complete without new dependencies or a
published personal contact. Contributors receive accurate setup, coding,
validation, pull-request, review, and recovery guidance; public reports collect
focused bug or feature information; external blank issues are deliberately
disabled; and security reporters have a verified private GitHub route. Native
issue-form rendering becomes observable only after these files reach the default
branch. Pull-request run `33174259832` provides the remote implementation
evidence with all eight jobs green for commit `21c3308`.
