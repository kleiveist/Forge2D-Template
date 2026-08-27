<!-- AUTO-GENERATED:backlink START -->
[← Back](reports.md)
<!-- AUTO-GENERATED:backlink END -->
# M03 Release v0.1.0 Report

- Date: 2026-08-26
- Status: Local release gate passed; publication pending until commit/tag/release

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
| Godot 4.7.2 official Linux binary | Run headless smoke validation | MIT | Large upstream binary download can fail or become unavailable | Distribution packages; rejected because they may not provide the tested release |

Validation evidence:

| Command | Result |
| --- | --- |
| `python tools/control.py install` | Passed |
| `python tools/control.py doctor` | Passed, 12 checks |
| `.venv/bin/python -m pytest tools/tests` | Passed, 50 tests |
| `python tools/control.py check` | Passed |
| `godot4 --headless --path game -- --test-mode` | Passed |
| `python tools/control.py godot4 test` | Passed |
| `xvfb-run -a python tools/control.py godot4 run -- --test-mode` | Passed |
| `git diff --check` | Passed |

Publication identifiers are recorded after the GitHub release is created.
