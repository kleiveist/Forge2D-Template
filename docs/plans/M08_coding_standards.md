<!-- AUTO-GENERATED:backlink START -->
[← Back](plans.md)
<!-- AUTO-GENERATED:backlink END -->
# M08 Coding Standards ExecPlan

## Purpose / Big Picture

Establish mandatory, repository-wide GDScript and Python conventions that make
new code predictable to read and review. Turn the reliable formatting subset
into a dependency-free repository command and make it part of the standard
`g2d check` gate on every supported operating system.

## Current State

The topic branch now contains mandatory Python and GDScript guides, a
standard-library-only `g2d style` command, and a distinct source-style step in
`g2d check`. The checker reinforces the existing `.editorconfig` and
`.gitattributes`, and the complete audited source passes it. Local unit and
headless Godot validation are green, as are all eight protected jobs in the
cross-platform pull-request matrix.

## Scope and Non-Goals

In scope are formatting, naming, typing, documentation, error handling, logging,
and testing rules for repository Python and GDScript; concise examples; a
standard-library-only checker; a `g2d style` command; `g2d check` integration;
focused tests; correction of current mechanical violations; and documentation
index links. Automatic code reformatting, third-party linters, generated files,
Godot project resources other than `.gd`, and subjective review automation are
out of scope. No dependency is added.

## Concrete Steps

1. Audit all tracked Python and GDScript source and compare the current
   conventions with the official Python and Godot guides.
2. Write mandatory language guides that distinguish automated rules from
   human-review rules and include compliant and non-compliant examples.
3. Implement deterministic source discovery and actionable diagnostics for
   encoding, whitespace, line length, Python structure, and GDScript structure.
4. Expose the checker through `g2d style`, run it as its own `g2d check` step,
   and unit-test valid input plus each failure family.
5. Correct existing violations, update navigation and command documentation,
   then run focused tests, the complete Python suite, and the standard gate.
6. Push an emoji-prefixed English commit to the shared issue branch, wait at
   least three minutes before each CI inspection, and require all eight jobs to
   pass before recording Issue #2 as implemented.

## Progress

- [x] 2026-08-28: Audited Issue #2, repository policy, editor/Git settings,
  current Python/GDScript source, CLI, release gate, tests, and documentation.
- [x] 2026-08-28: Confirmed the official Godot style guide and Python PEP 8/257
  as upstream references and chose a shared 100-column repository limit.
- [x] 2026-08-28: Added the binding language guides and dependency-free checker
  with compiler-style rule diagnostics and repair directions.
- [x] 2026-08-28: Integrated and unit-tested `g2d style` plus the dedicated
  `g2d check` style step.
- [x] 2026-08-28: Corrected all four Python lines over 100 columns and completed
  the repository audit with 34 of 34 source files passing.
- [x] 2026-08-28: Passed 105 Python tests and the full local release gate with a
  SHA-512-verified official Godot 4.7.2 binary.
- [x] 2026-08-28: Passed all eight protected jobs in pull-request CI run
  `33166426109` after hardening the Windows fixture and artifact boundary.

## Surprises & Discoveries

- 2026-08-28: The repository already had the cross-platform newline and
  indentation policy needed by both languages, so the checker can reinforce it
  instead of introducing an editor configuration change.
- 2026-08-28: All GDScript source already follows the planned automated rules;
  only four Python lines need mechanical cleanup.
- 2026-08-28: Masking GDScript strings with spaces made quoted content look like
  indentation. A focused real-repository run exposed the false positives; using
  non-whitespace placeholders preserves code positions without inventing indent.
- 2026-08-28: The first pull-request run exposed two generated-input boundaries:
  Windows wrote CRLF into a temporary test fixture, and the packaged CLI check
  created `.ci-artifact-venv` before invoking `g2d check`. The fixture now writes
  explicit LF, and only that known generated CI environment is excluded.

## Decision Log

- 2026-08-28: Use one 100-column maximum for `.py` and `.gd`. Godot recommends
  keeping GDScript below 100 characters, while PEP 8 explicitly permits an
  agreed team limit near 100; a shared limit is simple and reviewable.
- 2026-08-28: Implement the reliable subset with Python's standard library
  instead of adopting a formatter or linter. This avoids a new dependency while
  still making CI reject objective violations.
- 2026-08-28: Keep naming, documentation quality, error context, logging intent,
  and test quality as mandatory review rules because regex enforcement would
  create misleading false positives.

## Validation

| Command / check | Result |
| --- | --- |
| `.venv/bin/python -m pytest tools/tests/test_style.py tools/tests/test_cli.py tools/tests/test_check.py -q` | Passed; 30 tests |
| `python3 tools/control.py style` | Passed; 34 source files, no violations |
| `.venv/bin/python -m pytest tools/tests -q` | Passed; 105 tests |
| Initial `python3 tools/control.py check` without Godot on `PATH` | Expected environment failure; style and 104 then-current tests passed, Doctor identified only missing Godot |
| Official Godot 4.7.2 archive SHA-512 verification | Passed against release `SHA512-SUMS.txt` |
| `python3 tools/control.py check` with verified Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, style 34/34, 105 Python tests, marker-validated Godot test |
| Pull-request CI run `33166091454` | Failed during hardening; Windows exposed a CRLF test fixture and all artifact checks exposed generated `.ci-artifact-venv` source |
| [Pull-request CI run `33166426109`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33166426109) | Passed; all 8 jobs on Ubuntu, Windows, macOS, Debian, and Arch |

## Recovery / Idempotence

The checker is read-only and can be rerun safely. Each diagnostic names a file,
line, rule, cause, and repair direction. If a rule proves too broad, adjust its
focused unit tests and documented contract together; do not bypass the style
step in CI.

## Outcomes & Retrospective

The implementation is complete without a new dependency. Objective rules fail
early with actionable diagnostics, while the guides explicitly keep subjective
quality decisions in human review. Pull-request CI confirms the same command and
packaged CLI behavior across the complete protected matrix. Because Issues #2
through #8 share draft pull request #9, later issue commits will rerun that matrix
before the combined pull request is ready to merge.
