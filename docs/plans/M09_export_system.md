# M09 Cross-Platform Export System ExecPlan

## Purpose / Big Picture

Provide one safe, reproducible `g2d export` workflow for Linux, Windows, and
macOS. Keep exports repository-local, make dry runs side-effect free, surface
concrete recovery guidance, and prove every target through native GitHub Actions
jobs before Issue #3 is considered implemented.

## Current State

The repository has a Godot 4.7.2 project and verified editor downloads in CI,
but it has no versioned export presets, export command, export-template setup,
or uploaded game artifacts. The topic branch and draft pull request already
contain the completed coding-standard work from Issue #2; this plan extends that
same pull request without changing `main` directly.

## Scope and Non-Goals

In scope are reviewed Linux, Windows, and macOS release presets; fixed outputs
below ignored `artifacts/exports/`; a `g2d export` command with `--dry-run`;
template, process, and artifact validation; unit and repository-contract tests;
native CI exports and artifact uploads; and local/export-signing documentation.
Changing system Python, automatically installing the 1.2 GB Godot template
archive, accepting arbitrary output paths, release signing, Apple notarization,
store packaging, and publishing a GitHub Release are out of scope.

## Concrete Steps

1. Audit Issue #3, repository policy, Godot 4.7.2 export behavior, existing CLI,
   project tests, ignored paths, and the native CI matrix.
2. Version conservative presets and implement target metadata plus safe export
   preparation, command execution, timeout handling, and exact artifact checks.
3. Add CLI dispatch and focused tests for every target, dry-run immutability,
   missing prerequisites, failed processes, unsafe paths, and invalid outputs.
4. Extend native CI to install the SHA-512-verified official export templates,
   export on one Python job per operating system, validate outputs, and upload
   short-lived artifacts.
5. Document prerequisites, commands, unsigned-build boundaries, notarization,
   recovery, output retention, and the added CI action dependency.
6. Run focused tests, all Python tests, source style, headless Godot checks, and
   the complete `g2d check` gate.
7. Commit with an emoji-prefixed English subject, push to the shared issue
   branch, wait at least three minutes before every CI inspection, and iterate
   until all eight required jobs are green.

## Progress

- [x] 2026-08-28: Confirmed Issue #3 scope, a clean shared branch, draft PR #9,
  and eight green baseline status checks from completed Issue #2.
- [x] 2026-08-28: Audited repository tooling, project configuration, CI, tests,
  ignored paths, official Godot CLI export behavior, and 4.7.2 platform options.
- [x] 2026-08-28: Added reviewed presets and the safe repository-local export
  implementation with fixed paths, template checks, timeout, and file signatures.
- [x] 2026-08-28: Added unit, CLI, project-contract, source-safety, and CI-contract
  coverage for all targets and expected failure families.
- [x] 2026-08-28: Updated native CI for verified templates, native exports, exact
  artifact checks, and bounded upload retention.
- [x] 2026-08-28: Documented local prerequisites, commands, safety, signing and
  notarization boundaries, CI retention, limitations, and troubleshooting.
- [x] 2026-08-28: Passed 132 Python tests, source style, the complete repository
  gate, and real checksum-verified Linux, Windows, and macOS exports.
- [ ] Pass all protected pull-request checks and record the Issue #3 outcome.

## Surprises & Discoveries

- 2026-08-28: Godot publishes one cross-platform export-template archive of
  roughly 1.2 GB rather than small per-target archives, so CI should export only
  on the Python 3.11 job for each native runner instead of downloading it twice.
- 2026-08-28: Godot resolves preset-relative output paths from the project
  directory, while the CLI also accepts an explicit absolute destination. The
  preset and command therefore point to the same canonical ignored directory.
- 2026-08-28: macOS ZIP export works without a distribution identity, but an
  ad-hoc signature is not notarization and downloaded builds remain subject to
  Gatekeeper. CI artifacts must be documented as test builds, not releases.
- 2026-08-28: A real cross-export showed that Godot rejects universal macOS
  binaries unless ETC2/ASTC texture import is enabled. The portable project
  setting is now versioned and protected by a project-contract test.
- 2026-08-28: Real exports generated the missing Godot 4.4+ script UID sidecars.
  Official guidance requires committing these stable source identifiers, so all
  eight unique files are versioned and a project-contract test protects them.
- 2026-08-28: The first pull-request run passed Linux but exposed equivalent
  temporary-path aliases in one test: macOS `/var` versus `/private/var`, and
  Windows 8.3 versus long user-directory names. Comparing filesystem identity
  preserves the exact-artifact assertion across all supported hosts.

## Decision Log

- 2026-08-28: Use fixed target metadata rather than a user-supplied output path.
  This prevents exports from escaping the repository artifact root and gives CI
  exact names to validate.
- 2026-08-28: Export Linux `Forge2D-Template.x86_64`, Windows
  `Forge2D-Template.exe`, and macOS `Forge2D-Template.zip`. ZIP is the documented
  portable macOS bundle format; the other extensions follow Godot conventions.
- 2026-08-28: Keep `--dry-run` strictly read-only: discover and validate existing
  inputs, then show the command without creating output directories or deleting
  stale files.
- 2026-08-28: Run CI exports only for Python 3.11 on each native OS. The full
  Python matrix still runs `g2d check`; exports depend on Godot, not Python minor
  behavior, and avoiding duplicate template downloads reduces time and bandwidth.
- 2026-08-28: Add `actions/upload-artifact@v7` solely to retain validated CI
  exports for seven days. It is the GitHub-maintained MIT-licensed artifact
  action. Maintenance risk is a future runner-runtime or major-version change;
  the considered alternative was leaving outputs only on ephemeral runners,
  which would not satisfy Issue #3's artifact requirement.
- 2026-08-28: Add no Python or Godot runtime dependency. Export templates remain
  external generated tooling, are checksum-verified in CI, and never enter Git.

## Validation

| Command / check | Result |
| --- | --- |
| Focused export, CLI, project, and CI tests | Passed |
| `python tools/control.py style` | Passed; 37 source files |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 132 tests |
| Official Godot 4.7.2 export-template SHA-512 | Passed; `ca4d71…4079` |
| All three `g2d export TARGET --dry-run` commands | Passed; no output changes |
| Real Linux export | Passed; valid 73,551,432-byte ELF |
| Real Windows export | Passed; valid 109,159,704-byte PE32+ executable |
| Real macOS export | Passed; valid 60,484,109-byte universal ZIP |
| Initial gate with `GODOT4_BIN` inherited by unit tests | Failed as expected; 10 discovery fixtures were overridden, so validation switched to CI-equivalent `PATH` discovery |
| `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 37/37, 132 tests, Godot integration |
| Pull-request CI run `33168743033` | Failed during hardening; 4 native macOS/Windows jobs exposed path-alias test assumptions, while all 4 Linux jobs passed |
| Pull-request CI matrix | Pending |

## Recovery / Idempotence

Dry runs never mutate the checkout. A real export may replace only the selected
canonical artifact; it never removes the complete output root. Failed or empty
outputs are rejected so stale files cannot hide a failure. CI template setup is
recreated on ephemeral runners and can be rerun safely. If Godot changes preset
keys or template layout, update the pinned version, presets, contract tests, and
documentation together rather than weakening validation.

## Outcomes & Retrospective

Pending implementation and validation.
<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
