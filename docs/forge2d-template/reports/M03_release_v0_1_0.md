<!-- AUTO-GENERATED:backlink START -->
[← Back](reports.md)
<!-- AUTO-GENERATED:backlink END -->
# M03 Release v0.1.0 Report

- Date: 2026-08-28
- Status: Published and independently verified

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
| `.venv/bin/python -m pytest tools/tests -q` | Passed, 172 tests on final `main` |
| `python tools/control.py style` | Passed, 44 source files on final `main` |
| `python tools/control.py check` | Passed on `e0c53ce`; Doctor 12/12, style, 172 tests, and Godot 4.7.2 integration |
| `python tools/control.py release prepare --dry-run` with exact-main exports | Passed without writes; ELF, PE, and ZIP signatures validated |
| `python tools/control.py release prepare` and identical rerun | Passed; three fixed assets and SHA-256 sums created atomically, then accepted without rewrite |
| Independent local and published SHA-256 recomputation | Passed for every Linux, Windows, and macOS asset |
| `godot4 --headless --path game -- --test-mode` | Passed |
| `python tools/control.py godot4 test` | Passed |
| `xvfb-run -a python tools/control.py godot4 run -- --test-mode` | Passed |
| `git diff --check` | Passed |
| [Pull-request CI run `33171491545`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33171491545) | Passed; all eight required jobs for preparation commit `ecc5335` |
| [Protected-main push run `33201281319`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33201281319) | Passed; all eight required jobs for exact SHA `e0c53ce` |
| [GitHub Release `v0.1.0`](https://github.com/kleiveist/Forge2D-Template/releases/tag/v0.1.0) | Published as latest; not a draft or prerelease; four assets uploaded |

Publication identifiers:

- Protected `main` commit:
  `e0c53ce78d1d52b14e4a2fd9729ab09c25eaabe0`.
- Successful exact-commit push CI run:
  [`33201281319`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33201281319).
- Annotated `v0.1.0` tag object:
  `2274f84eff18508cc00dd7acb169c1fa85d79e1c`.
- GitHub Release:
  <https://github.com/kleiveist/Forge2D-Template/releases/tag/v0.1.0>.

Published assets:

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `Forge2D-Template-v0.1.0-linux-x86_64` | 73,569,392 | `e3fa0bb8fb4f4143d49c3b8ace88dd8dd30b1581dee143441a784be28dc6a037` |
| `Forge2D-Template-v0.1.0-windows-x86_64.exe` | 109,177,664 | `c6f77417658b0eb32562f3bf5ac9431ed1ff7a33f3e285f6507bda59a078d172` |
| `Forge2D-Template-v0.1.0-macos-universal.zip` | 60,490,683 | `e32a3479d95f60453cdafe27cb76adace305e01a61115547ccad99d307573406` |
| `SHA256SUMS.txt` | 322 | Contains the three digests above |

Repository-side preparation now includes checked-in v0.1.0 notes, fixed asset
names, independent ELF/PE/ZIP validation, deterministic SHA-256 sums, atomic
non-overwriting staging, and the reviewed procedure in
`docs/forge2d-template/tooling/releasing.md`.
Preparation commit `ecc5335` passed all eight checks in pull-request run
`33171491545`. PR #9 was then merged as `e0c53ce`, whose exact push run passed
all eight checks again. The three artifacts from that run were prepared without
overwriting the earlier PR outputs, published with `SHA256SUMS.txt`, downloaded
into a fresh temporary directory, and independently verified byte for byte.
