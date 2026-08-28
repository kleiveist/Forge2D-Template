<!-- AUTO-GENERATED:backlink START -->
[← Back](index.md)
<!-- AUTO-GENERATED:backlink END -->
# Mandatory Python Coding Standard

This standard is mandatory for every Python change in Forge2D Template. It
applies to `tools/control.py`, `tools/src/**/*.py`, and `tools/tests/**/*.py`.
[PEP 8](https://peps.python.org/pep-0008/) and
[PEP 257](https://peps.python.org/pep-0257/) are the upstream baseline; this
repository standard resolves project-specific choices and takes precedence when
it is more specific.

## Automated rules

`python tools/control.py style` checks every repository `.py` file and reports a
path, line, column, rule code, cause, and repair direction. The same read-only
check is a required step of `python tools/control.py check` and therefore runs in
the Linux, Windows, and macOS CI matrix.

The checker requires:

- UTF-8 without a byte-order mark, LF line endings, a final newline, and no
  trailing whitespace;
- at most 100 characters per line after expanding tabs to four columns;
- four-space indentation and no tab indentation;
- syntactically parseable Python and a module docstring in every module;
- explicit imports instead of wildcard imports;
- a narrow exception type instead of bare `except:`; and
- parameter and return annotations on every function in production tooling under
  `tools/control.py` and `tools/src` (`self` and `cls` are exempt).

Generated environments and outputs such as `.venv`, `.ci-artifact-venv`, caches,
`build`, and `dist` are excluded. Do not move source into an excluded path to
evade the check.

## Formatting and imports

- Use four spaces per indentation level and implicit continuation inside
  parentheses, brackets, or braces. Do not use backslashes for routine wrapping.
- Keep lines at or below 100 characters. Prefer readable wrapping before the
  limit and include a trailing comma in multiline calls and collections.
- Group imports as standard library, third-party packages, then repository
  modules, with one blank line between groups. Import names explicitly.
- Put two blank lines around module-level classes and functions and one blank
  line between logical sections inside a function.
- Keep source, comments, identifiers, diagnostics, and test descriptions in
  English.

Compliant:

```python
from pathlib import Path

from g2dtool.repository import RepositoryLayout


def cache_directory(layout: RepositoryLayout) -> Path:
    """Return the repository-local cache directory."""

    return layout.repository_root / ".cache"
```

Non-compliant:

```python
from g2dtool.repository import *

def cacheDirectory(layout): return layout.repository_root / ".cache"
```

## Naming and types

- Name modules, functions, methods, parameters, and variables with
  `lower_snake_case`; classes and exceptions with `UpperCamelCase`; and constants
  with `UPPER_SNAKE_CASE`.
- Prefix internal interfaces with one underscore. Do not invent double-underscore
  names or abbreviate a public name merely to shorten a line.
- Use Python 3.11 syntax: built-in collections such as `list[str]`, `Path | None`
  for unions, and `collections.abc` for callable and collection protocols.
- Type all production function boundaries, including `-> None`. Prefer precise
  domain types over `Any`; confine unavoidable dynamic values to a validated
  boundary.
- Unit-test methods and small local test doubles may omit annotations when the
  test framework or immediate call site makes the type unambiguous. Shared test
  helpers should be typed.
- Do not silence a type or lint finding globally. A narrow suppression needs a
  nearby explanation and reviewer agreement.

## Documentation

- Start every module with a concise purpose docstring; this is automated.
- Document public classes and functions, non-obvious side effects, raised
  exceptions, platform differences, and safety constraints. Avoid restating the
  signature.
- Write one-line docstrings as an imperative phrase ending with a period, for
  example `"""Return the resolved repository root."""`.
- For a multiline docstring, put a summary first, then a blank line and the
  details. Keep comments focused on why a decision exists, not what the code
  visibly does.

## Errors and user-facing output

- Catch the narrow expected exception. Never swallow an exception with `pass`.
  `except Exception` is reserved for a command boundary that converts unexpected
  failure into a stable exit code while preserving useful context.
- Expected failures must state the cause and a concrete recovery action. Do not
  expose tokens, credential files, or sensitive subprocess output.
- Use `g2dtool.logger` for statuses, warnings, failures, plans, and remediation.
  Plain `print` is limited to intentional stable payloads such as `version`, the
  bootstrap path before package imports, or faithfully relayed child output.
- Run subprocesses with argument sequences, `shell=False`, a finite timeout, and
  an explicit working directory. Check and propagate exit status.

Compliant:

```python
try:
    contents = path.read_text(encoding="utf-8")
except OSError as exc:
    raise ProjectConfigError(
        f"Cannot read project configuration at {path}: {exc}"
    ) from exc
```

Non-compliant:

```python
try:
    contents = open(path).read()
except:
    pass
```

## Tests and review

- Every behavior change needs a deterministic regression test. Run the fastest
  focused test first, then the complete suite, then `g2d check` when its external
  requirements are available.
- Tests must not depend on execution order, a developer home directory, network
  access, locale-specific output, or the host shell. Use temporary directories
  and inject platform/process boundaries.
- Cover success, expected failure, recovery guidance, and relevant platform
  branches. Assert observable contracts rather than implementation trivia.
- Reviewers enforce naming clarity, useful types/docstrings, exception scope,
  safe logging, and test quality. These judgments are mandatory even though they
  are intentionally not reduced to regex checks.

Run locally:

```text
python tools/control.py style
.venv/bin/python -m pytest tools/tests -q
python tools/control.py check
```

On Windows, use `.venv\Scripts\python.exe` for the direct pytest command.
