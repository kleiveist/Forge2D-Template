<!-- AUTO-GENERATED:backlink START -->
[← Back](reports.md)
<!-- AUTO-GENERATED:backlink END -->
# M06 Cross-Platform Installer Completion Report

- Date: 2026-08-28
- Status: **Complete; implementation is on `main`, report is in draft PR #9**

## Goal and Outcome

M06 changed `g2d install` from a local package bootstrap into a safe, mostly
automatic setup path for Linux, Windows, and macOS. It checks the running Python,
`venv`/`ensurepip`, repository-local pip, Godot 4, and every Python distribution
declared in [`config/toolchain.toml`](../../../config/toolchain.toml). Missing
system requirements can be planned through an already available APT, Pacman,
Winget, or Homebrew installation.

Python project packages are never installed into system Python. New and reused
environments are confined to `.venv`, and every pip operation begins with that
environment's Python executable. `--dry-run` performs probes and prints a plan
without prompting or changing the checkout; `--yes` accepts only confirmations
owned by the installer. Operating-system privilege controls remain in force.

The implementation, user workflow, and current recovery guidance are maintained
in the [M06 ExecPlan](../plans/M06_cross_platform_installer.md) and the
[installation guide](../tooling/installation.md).

## Delivered Behavior

| Area | Delivered behavior |
| --- | --- |
| Python | Requires the configured minimum, currently Python 3.11; reports the detected version and a concrete rerun command when a newer interpreter is needed. |
| `venv` and pip bootstrap | Probes `venv` and `ensurepip`; plans `python3-venv` on supported APT hosts or a Python repair through the other supported managers. |
| Local environment | Creates `.venv`, reuses it when healthy, and requires separate confirmation before clearing an incomplete existing environment. |
| Python packages | Installs the repository tooling and configured dependencies only through `.venv` Python, then runs `pip check` and `pip show` verification. |
| Godot | Discovers configured command candidates, rejects the wrong major, and checks for Godot 4 before and after setup. |
| Dry-run | Performs read-only discovery/version probes, prints system/venv/pip actions, never prompts, never invokes a mutating command, and never creates `.venv`. |
| Confirmation | Groups package-manager actions behind one prompt; protects broken-`.venv` replacement with a separate prompt; `--yes` accepts both without bypassing sudo, UAC, or policy controls. |
| Failures | Returns stable nonzero results for expected failures and prints the failed operation, exit code/output where available, and specific recovery steps. |

The package-manager plan is intentionally narrow:

| Host | Existing manager used | Safe automatic scope |
| --- | --- | --- |
| Debian/Ubuntu family | APT | `python3-venv`; `godot` only when `apt-cache policy` proves that the selected candidate has the required major |
| Arch family | Pacman | Python bootstrap repair and `godot`, using `--needed` and `--noconfirm` when `--yes` is active |
| Windows | Winget | Exact Python minimum package ID when required and exact `GodotEngine.GodotEngine`, including source/agreement flags |
| macOS | Homebrew | Versioned Python formula when required and the `godot` cask |

APT's candidate check prevents an apparently successful but incompatible Godot
3 installation on repositories that do not provide Godot 4. When a compatible,
provable route is unavailable, the installer prints a manual Godot 4 path rather
than adding an unreviewed repository or downloading an executable itself.

## Safety and Recovery

The implementation in
[`tools/src/g2dtool/install.py`](../../../tools/src/g2dtool/install.py) constructs
commands as argument sequences and does not execute them through a shell. System
actions are shown before execution. A declined package-manager prompt executes
none of the group, and a declined `.venv` replacement leaves that environment
untouched.

Expected failures distinguish the cause from the remedy. Examples include:

- an old Python process that must be restarted through the newly installed
  interpreter;
- missing `venv`/`ensurepip` support that must be repaired without system pip;
- an incompatible or ambiguous APT Godot candidate that requires a trusted
  manual Godot 4 installation;
- package-manager failures with the exact failed command and captured error;
- package-index or dependency-consistency failures with `.venv`-only repair
  instructions; and
- invalid toolchain configuration with the configuration file to review.

Re-running the installer is safe. A healthy `.venv` is reused, native package
manager flags are idempotent where available, and dry-run remains read-only. A
broken `.venv` is cleared only through its dedicated confirmation or `--yes`.

## Tests and Hosted CI

[`tools/tests/test_install.py`](../../../tools/tests/test_install.py) covers APT,
Pacman, Winget, Homebrew, incompatible APT candidates, old Python, missing
bootstrap support, a healthy or broken `.venv`, both confirmation paths,
package-manager and Python-package failures, invalid configuration, system-pip
exclusion, and the native CI dry-run contract.

The native matrix in
[`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) runs on Ubuntu,
Windows, and macOS with Python 3.11 and 3.14. Before installing Godot or the
repository environment, each of those six jobs runs `install --dry-run --yes`
and asserts that `.venv` did not exist before or after it. Separate Debian 13
and Arch Linux container jobs install their system prerequisites explicitly,
then exercise the real repository-local `install --yes`, Doctor, and complete
gate. CI does not mutate the native hosted runners through APT, Winget, or
Homebrew, so it validates planning and side-effect freedom rather than claiming
end-to-end privileged package installation on every host.

### Validation Evidence

| Command or evidence | Observed result |
| --- | --- |
| Focused installer, CLI, control, and logger tests during M06 | Passed; 39 tests |
| `python3 tools/control.py install --dry-run --yes` | Passed; read-only probes and a plan, with no installer mutation |
| Real `install --yes` with checksum-verified Godot 4.7.2 | Passed; `.venv` pip/packages verified and Doctor 12/12 |
| `python3 tools/control.py check` with temporary Godot 4.7.2 on `PATH` | Passed; Doctor 12/12, 90 Python tests, and real headless Godot integration |
| `.venv/bin/python -m unittest discover -s tools/tests` | Passed; 90 tests |
| `python tools/control.py godot4 test` with temporary Godot 4.7.2 | Passed; required integration marker emitted |
| Python source compilation | Passed for bootstrap, package, and tests |
| Temporary wheel build and isolated install | Passed; installed CLI version/help and installer dry-run worked |
| CI contract test | Passed; native Linux, Windows, and macOS jobs contain the side-effect-free dry-run guard |
| [Initial run `33161384474`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33161384474) for `0c1d1a6` | Installer dry-run steps passed; four macOS/Windows jobs later failed two raw temporary-path assertions, so this was not counted as a successful run |
| Symlink/path-alias regression tests after `e584620` | Passed; `.venv` pip targets compare canonical paths on macOS and Windows |
| [Corrected run `33161920298`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33161920298) for `e584620` | Passed; all 8 jobs green, including all 6 native installer dry-run steps |
| Current `.venv/bin/python tools/control.py install --dry-run --yes` on Debian | Passed without changes; retained healthy `.venv`, refused ambiguous APT Godot, and printed trusted manual recovery |
| Current focused installer, CLI, control, and logger tests | Passed; 46 tests |
| Current installer/report hygiene tests | Passed; 32 tests |
| Current local `python tools/control.py check` with verified Godot 4.7.2 | Passed; Doctor 12/12, style 44/44, 172 Python tests, and Godot integration |
| [Current PR run `33179894053`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33179894053) for `cf3ff6b` | Passed; all 8 Linux, Windows, and macOS jobs green |
| [Report run `33180569741`](https://github.com/kleiveist/Forge2D-Template/actions/runs/33180569741) for `9901671` | Passed; all 8 jobs green and all 6 native installer dry-run steps succeeded |

The first hosted failure was diagnostic, not hidden: macOS can expose the same
temporary directory through `/var` and `/private/var`, and Windows also
normalizes temporary paths. Commit `e584620` retained the production safety
check while making only the test assertions compare resolved executable paths.

## Traceability

- Implementation commit
  [`0c1d1a6`](https://github.com/kleiveist/Forge2D-Template/commit/0c1d1a6ef06b5edff6eeb7da873ac5328cfae69f)
  added the installer, platform plans, tests, native dry-run workflow, README,
  changelog, installation guide, and M06 plan.
- Correction commit
  [`e584620`](https://github.com/kleiveist/Forge2D-Template/commit/e584620bf6f72915b0a435aaa3d1a26c86579db5)
  normalized cross-platform test comparisons and received the first fully green
  hosted M06 run.
- Documentation integration commit
  [`5059a42`](https://github.com/kleiveist/Forge2D-Template/commit/5059a4202d5e44ec3a69ab3d9bd8668162a4c09a)
  moved M06 material into the protected-main documentation architecture without
  rewriting the shared issue branch.
- This completion report is tracked by
  [Issue #8](https://github.com/kleiveist/Forge2D-Template/issues/8) in
  [draft PR #9](https://github.com/kleiveist/Forge2D-Template/pull/9).

No new dependency was adopted for M06. Detection, planning, execution, and tests
use the Python standard library. Optional package managers remain external host
capabilities, and configured project dependencies retain their purpose, license,
risk, and alternative records in `config/toolchain.toml`.

## Remaining Limitations and Follow-up

- The installer itself must start under some Python. It can install or plan the
  configured minimum, but a running old interpreter cannot switch in place; the
  user must rerun the printed command with the new Python.
- Only APT and Pacman are automated on Linux. Other distributions and package
  managers receive manual guidance.
- The installer never installs a package manager, adds repositories/taps,
  downloads executables directly, changes shell profiles, bypasses agreements,
  or circumvents organization policy.
- APT automation deliberately stops when it cannot prove a compatible Godot 4
  candidate. Debian 13 and Ubuntu 24.04 commonly require a trusted manual Godot
  4 installation.
- Sudo passwords, UAC, package-source availability, network access, corporate
  policy, and post-install PATH refreshes remain host responsibilities.
- A compatible Godot 4.x satisfies installation; the exact release baseline is
  Godot 4.7.2 and remains enforced by CI rather than by replacing a compatible
  local editor.
- Godot export templates are separate, large artifacts and are not installed by
  `g2d install`; the export guide documents their explicit setup.
- Hosted native jobs prove side-effect-free command planning, not privileged
  real package-manager mutations. Such mutations remain unit-tested and require
  confirmation on a developer-owned host.

## Conclusion

M06 is complete. Forge2D Template has a cross-platform installer that automates
the safe portions of setup, isolates Python changes in `.venv`, makes every
proposed action reviewable, and fails with recovery guidance when automation
cannot be proven safe. The remaining boundaries are explicit host privilege,
package availability, and deliberate manual installation paths rather than
hidden or overstated automation.
