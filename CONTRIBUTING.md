# Contributing to Forge2D Template

Thank you for improving Forge2D Template. Contributions should keep the template
small, reusable, cross-platform, and safe for downstream projects.

## Choose the Right Route

- Use the GitHub issue chooser's bug form for reproducible defects.
- Use the feature form for a concrete problem and proposed capability.
- Do not open a public issue for a suspected vulnerability. Follow the private
  process in [SECURITY.md](SECURITY.md).
- Search open and closed issues before filing a duplicate. Large architectural
  changes should start with an issue so scope and compatibility can be agreed
  before implementation.

Blank issues are deliberately disabled for external contributors so reports
contain enough information to act on. GitHub may still show a maintainer-only
blank option to users with repository write access for exceptional maintenance
work.

## Prepare the Checkout Safely

Forge2D Template requires Python 3.11 or newer and is tested with Godot 4.7.2.
Inspect setup before allowing changes:

```text
python tools/control.py install --dry-run
python tools/control.py install --yes
python tools/control.py doctor
```

Use `python3` where `python` is unavailable, or `py -3.11` on Windows. The
installer must not modify system Python: editable tooling and declared packages
belong in the repository-local `.venv`. It may use an existing APT, Pacman,
Winget, or Homebrew installation for missing system requirements after applying
its confirmation rules. See
[cross-platform installation](docs/forge2d-template/tooling/installation.md) for
supported paths, dry-run guarantees, and recovery steps.

Activation is optional. Repository commands can continue to use
`python tools/control.py`; the full check automatically prefers `.venv` for
Python tests.

## Create a Focused Change

1. Start from an up-to-date `main` and create a descriptive topic branch. Never
   push a contribution directly to protected `main`.
2. Keep the change focused on one agreed problem. Preserve unrelated local work
   and do not commit generated caches, export artifacts, local binaries,
   credentials, tokens, or machine-specific paths.
3. Follow the mandatory
   [Python](docs/forge2d-template/tooling/python-style-guide.md) and
   [GDScript](docs/forge2d-template/tooling/gdscript-style-guide.md) standards.
4. Add or update tests and relevant documentation whenever behavior changes.
5. Start each commit subject with a relevant emoji followed by a concise,
   imperative English summary.

Do not add a dependency without prior review. Record its purpose, maintenance
risk, license, and considered alternative in the relevant plan or decision
before adoption.

## Validate the Change

Run the fastest relevant test first. For a focused Python test on Linux or
macOS, for example:

```text
.venv/bin/python -m pytest tools/tests/test_example.py -q
```

On Windows, use `.venv\Scripts\python.exe` instead. Then run the objective style
gate and the complete repository gate:

```text
python tools/control.py style
python tools/control.py check
```

`g2d check` runs Doctor, source style, all Python tests, and the Godot headless
integration suite. Report only commands actually run and include actionable
details for any skipped or failing check. Do not weaken a check to make a change
pass.

## Open and Maintain the Pull Request

- Open a pull request against `main` and complete every applicable section of
  the repository template. Link the issue with a closing keyword when the PR
  fully resolves it.
- Explain user-visible behavior, tests, documentation, risk, recovery, and any
  platform-specific limitation. Update `CHANGELOG.md` for a notable change.
- Keep the branch current with `main`, respond to review, and resolve every
  conversation without rewriting another contributor's work.
- Convert a draft to ready only when the change is reviewable and its known
  limitations are explicit.

Protected `main` requires a pull request, linear history, an up-to-date branch,
resolved conversations, and all eight Linux, Windows, and macOS CI jobs to pass.
Administrators cannot bypass those gates. Independent approval is not currently
required for solo maintenance; reviewers still assess scope, naming, tests,
documentation, failure handling, security, compatibility, and recovery. See
[main branch protection](docs/forge2d-template/tooling/branch-protection.md) for
the exact policy.

Maintainers decide the final merge method and release timing. Do not merge,
tag, publish a release, or push additional scope without the requested review
and authorization.
