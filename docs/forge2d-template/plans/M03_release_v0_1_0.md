<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M03 Release v0.1.0 ExecPlan

This living plan covers both repository release readiness and the final,
externally visible publication of Forge2D Template v0.1.0.

## Purpose / Big Picture

Publish the first immutable GitHub release from an approved commit on protected
`main`. The release must have consistent version metadata and notes, an annotated
tag, validated Linux/Windows/macOS exports, cryptographic checksums, and enough
recorded evidence for another maintainer to verify the commit and downloads.

## Current State

Repository identity, the local release gate, cross-platform installer, mandatory
coding standards, protected-main policy, and native export CI are implemented.
The shared draft PR is `#9` on `feat/release-readiness`; its head is not yet a
commit on protected `main`. The current `main` commit therefore cannot satisfy
Issue #4's dependency on the export system in Issue #3. No `v0.1.0` tag or GitHub
Release exists.

Release notes and safe asset preparation can be reviewed within PR #9. The
annotated tag and public release must wait until the complete PR is merged and a
new push CI run for the exact resulting `main` commit passes all eight required
checks.

## Scope and Non-Goals

In scope are consolidated v0.1.0 changelog contents, checked-in release notes,
metadata consistency checks, deterministic public asset names, SHA-256 sums,
safe and idempotent asset staging, an independently verifiable publication
procedure, an annotated immutable tag, GitHub Release publication, and the final
Issue #4 evidence comment.

Production code signing, Windows Authenticode, Apple Developer ID notarization,
store packaging, history rewrites, tag replacement, and merging PR #9 without
the user's explicit approval are out of scope. The unsigned status of each
platform artifact must be visible in the release notes.

## Concrete Steps

1. Audit Issue #4, remote tags/releases, protected `main`, PR #9, version
   metadata, changelog, native CI outputs, and artifact retention.
2. Consolidate all current first-release changes under one v0.1.0 changelog
   heading and derive checked-in release notes from it.
3. Implement `g2d release prepare` to verify metadata and downloaded native CI
   exports, assign immutable versioned names, and atomically write SHA-256 sums.
4. Add deterministic tests for success, dry-run immutability, idempotence,
   metadata mismatch, missing/invalid platform outputs, unsafe paths, and
   non-overwrite behavior.
5. Document exact-main CI selection, artifact download, local and remote hash
   verification, annotated tagging, publication, and non-destructive recovery.
6. Run focused tests, all Python tests, source style, `g2d check`, and a local
   preparation dry-run using the real checksum-verified exports.
7. Commit with an emoji-prefixed English subject, push PR #9, wait at least three
   minutes before inspecting Actions, and iterate until all eight jobs are green.
8. After the complete PR is explicitly approved and merged, select the exact
   successful `main` push run, prepare its artifacts, create and push the
   annotated `v0.1.0` tag, publish the GitHub Release, download and verify all
   remote assets, update the report, and comment on Issue #4.

## Progress

- [x] 2026-08-26: Established repository identity, release gate, CI, license,
  and consistent initial `0.1.0` metadata.
- [x] 2026-08-28: Confirmed protected `main` at `a5f2cb8`, draft PR #9 at
  `0bddc49`, no remote/local v0.1.0 tag, and no GitHub Release.
- [x] 2026-08-28: Confirmed all eight jobs are green for PR run `33169483969`
  and its Linux, Windows, and macOS workflow artifacts are still available.
- [x] 2026-08-28: Identified the hard publication boundary: current `main` does
  not contain Issue #3, while the user requires all issue work in the shared PR.
- [x] 2026-08-28: Added consolidated changelog contents, v0.1.0 release notes,
  safe release-asset preparation, focused tests, and operator documentation.
- [x] 2026-08-28: Passed 150 Python tests, source style, the complete local
  release gate, and real three-platform preparation/checksum validation.
- [x] 2026-08-28: Passed all eight required jobs in pull-request CI run
  `33171491545` for Issue #4 preparation commit `ecc5335`.
- [ ] Merge the complete shared PR only after explicit user approval.
- [ ] Tag the exact green protected-main commit and publish/verify v0.1.0.

## Surprises & Discoveries

- 2026-08-28: The existing v0.1.0 changelog heading was dated as though a
  release existed, while GitHub and Git had no matching release or tag. All
  first-release changes must be consolidated before publication.
- 2026-08-28: Pull-request run `33169483969` has valid artifacts, but its commit
  is not the final protected-main commit required by Issue #4. A post-merge push
  run must regenerate the release inputs.
- 2026-08-28: GitHub Actions archives do not preserve Linux executable mode.
  Release verification therefore relies on content signatures and SHA-256; users
  may still need `chmod +x` after downloading the direct Linux release asset.
- 2026-08-28: The three native outputs total roughly 232 MB. Reusing the exact
  already-validated main CI outputs avoids a second release workflow and a
  duplicated 1.2 GB export-template download on every platform.

## Decision Log

- 2026-08-28: Do not tag the feature branch or today's pre-export `main` merely
  to satisfy ordering. Version tags are immutable release records and must point
  to the exact approved protected-main commit.
- 2026-08-28: Reuse the native Python 3.11 CI artifacts from the selected main
  run, then independently revalidate ELF/PE/ZIP signatures and SHA-256 locally.
- 2026-08-28: Add no dependency and no write-enabled release workflow. The
  repository's Python standard library and authenticated GitHub CLI are enough;
  keeping tag creation manual preserves the required review boundary.
- 2026-08-28: Use fixed public names containing `v0.1.0` and architecture, and
  list every file explicitly during publication. Broad globs could attach an
  unrelated ignored file.
- 2026-08-28: Make preparation atomic and non-overwriting. An identical second
  run is accepted, but any mismatch requires the operator to move the existing
  asset directory aside and investigate.

## Validation

| Command / check | Result |
| --- | --- |
| Focused release contract and failure tests | Passed; 15 tests |
| `python tools/control.py style` | Passed; 39 source files |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 150 tests |
| `python tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 39/39, 150 tests, Godot integration |
| Real three-platform `release prepare --dry-run` | Passed; validated 73,551,432-byte ELF, 109,159,704-byte PE, and 60,484,109-byte ZIP without writing assets |
| Real preparation, independent SHA-256 audit, and identical rerun | Passed; three versioned assets, 322-byte checksum document, and no rewrite on rerun |
| `git diff --check` | Passed |
| [Pull-request CI run `33171491545`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33171491545) | Passed; all eight Ubuntu, Windows, macOS, Debian, and Arch jobs |
| Exact protected-main push CI | Blocked until the complete PR is merged |
| Remote tag, release, and downloaded checksum audit | Blocked until protected-main CI passes |

## Recovery / Idempotence

`release prepare --dry-run` is read-only. A real preparation validates every
input first, stages into a temporary sibling, and atomically creates the complete
asset directory. It never clears downloads or overwrites an existing mismatch.
Generated downloads/assets remain below ignored `artifacts/` and can be recreated
from the recorded main CI run.

Before push, an incorrect local tag can be deleted and recreated after review.
After push, `v0.1.0` must never move or be overwritten. A publication failure is
recovered by keeping the tag and retrying the release step; an error in published
code or binaries requires a new patch release rather than rewritten history.

## Outcomes & Retrospective

Repository-side release preparation is implemented and validated locally and in
all eight pull-request jobs. Final protected-main SHA/run, tag object, release
URL, published asset list, and remote checksum results are recorded only after
the complete shared PR is approved and merged.
