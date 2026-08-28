<!-- AUTO-GENERATED:backlink START -->
[← Back](reports.md)
<!-- AUTO-GENERATED:backlink END -->
# M03 Release v0.1.0 Report

- Date: 2026-08-28
- Status: Release preparation in PR #9; publication blocked until approved merge

M03 prepares Forge2D Template v0.1.0 for public template use. The release sets
the repository identity to `Forge2D-Template`, the display name to Forge2D
Template, and the template ID to `forge2d-template`.

Release gate:

- `python tools/control.py install`
- `python tools/control.py doctor`
- `python tools/control.py check`
- `python -m pytest tools/tests`
- `godot4 --headless --path game -- --test-mode`
- `python tools/control.py godot4 run -- --test-mode`

External tools and CI actions adopted for this release:

| Dependency | Purpose | License | Maintenance risk | Considered alternative |
| --- | --- | --- | --- | --- |
| `pytest>=8,<9` | Standard Python test runner for local gate and CI | MIT | Major upgrades can alter collection or reporting behavior | Keep only `unittest`; rejected because the release gate explicitly requires pytest as a dev dependency |
| `actions/checkout@v7` | Fetch repository source in CI | MIT | GitHub-hosted action behavior can change between major versions | Manual git clone in CI; rejected as less maintainable |
| `actions/setup-python@v7` | Install Python 3.11 and 3.14 in CI | MIT | Runner/toolcache behavior can change between major versions | Use runner default Python; rejected because the supported versions should be explicit |
| `actions/upload-artifact@v7` | Retain validated native game exports for seven days | MIT | Runner integration or archive behavior can change between major versions | Re-export separately during publication; rejected because it duplicates large verified template downloads and weakens commit traceability |
| Godot 4.7.2 official editors and export templates | Run integration tests and native exports | MIT | Large upstream downloads can fail or become unavailable | Distribution packages; rejected because they may not provide the exact tested release and matching templates |

Validation evidence:

| Command | Result |
| --- | --- |
| `python tools/control.py install` | Passed |
| `python tools/control.py doctor` | Passed, 12 checks |
| `.venv/bin/python -m pytest tools/tests -q` | Passed, 150 tests |
| `python tools/control.py style` | Passed, 39 source files |
| `python tools/control.py check` | Passed; Doctor 12/12, style, 150 tests, and Godot 4.7.2 integration |
| `python tools/control.py release prepare --dry-run` with all real exports | Passed without writes; ELF, PE, and ZIP signatures validated |
| `python tools/control.py release prepare` and identical rerun | Passed; three fixed assets and SHA-256 sums created atomically, then accepted without rewrite |
| Independent SHA-256 recomputation | Passed for all three 232 MB platform assets |
| `godot4 --headless --path game -- --test-mode` | Passed |
| `python tools/control.py godot4 test` | Passed |
| `xvfb-run -a python tools/control.py godot4 run -- --test-mode` | Passed |
| `git diff --check` | Passed |
| [Pull-request CI run `33171491545`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33171491545) | Passed; all eight required jobs for preparation commit `ecc5335` |

Publication identifiers are recorded after the GitHub release is created.

Issue #4 publication boundary:

- Protected `main` is currently `a5f2cb8`; it predates the Issue #3 export
  system and cannot be tagged as the requested release.
- Draft PR #9 contains the release work but is not an approved `main` commit.
- The annotated tag, platform assets, and GitHub Release will be created only
  after the complete PR is explicitly approved, merged, and followed by an
  eight-job successful push run for the exact resulting main SHA.

Repository-side preparation now includes checked-in v0.1.0 notes, fixed asset
names, independent ELF/PE/ZIP validation, deterministic SHA-256 sums, atomic
non-overwriting staging, and the reviewed procedure in `docs/releasing.md`.
Preparation commit `ecc5335` passed all eight checks in pull-request run
`33171491545`. Final protected-main identifiers, release URL, published assets,
and downloaded checksum evidence remain intentionally pending.
