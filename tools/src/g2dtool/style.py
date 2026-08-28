"""Validate repository Python and GDScript coding standards."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ast
import os
import re

from g2dtool.logger import error, print_help_line, success
from g2dtool.repository import discover_repository_layout


MAX_LINE_LENGTH = 100
SOURCE_SUFFIXES = frozenset({".gd", ".py"})
EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".godot",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
)
FUNCTION_DECLARATION = re.compile(
    r"(?m)^[\t ]*(?:static[\t ]+)?func[\t ]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)[\t ]*\("
)
TYPED_GDSCRIPT_PARAMETER = re.compile(r"^[\t ]*[A-Za-z_][A-Za-z0-9_]*[\t ]*:")


@dataclass(frozen=True, slots=True)
class StyleViolation:
    """One actionable source-style violation."""

    path: str
    line: int
    column: int
    rule: str
    message: str
    solution: str

    def format(self) -> str:
        """Return a stable compiler-style diagnostic."""

        return (
            f"{self.path}:{self.line}:{self.column} [{self.rule}] {self.message} "
            f"Fix: {self.solution}"
        )


@dataclass(frozen=True, slots=True)
class StyleReport:
    """Result of checking all repository Python and GDScript source."""

    checked_files: int
    violations: tuple[StyleViolation, ...]

    @property
    def exit_code(self) -> int:
        """Return zero only when every checked file follows the standard."""

        return 0 if not self.violations else 1


def discover_source_files(repository_root: Path) -> tuple[Path, ...]:
    """Return deterministic repository source paths while excluding generated data."""

    paths: list[Path] = []
    for current_root, directory_names, file_names in os.walk(repository_root):
        directory_names[:] = sorted(
            name for name in directory_names if name not in EXCLUDED_DIRECTORIES
        )
        current = Path(current_root)
        for file_name in sorted(file_names):
            path = current / file_name
            if path.suffix in SOURCE_SUFFIXES and not path.is_symlink():
                paths.append(path)
    return tuple(paths)


def collect_style_report(repository_root: Path) -> StyleReport:
    """Check all supported source below a repository root."""

    root = repository_root.resolve()
    source_files = discover_source_files(root)
    violations: list[StyleViolation] = []
    for path in source_files:
        relative_path = path.relative_to(root)
        violations.extend(_check_source(path, relative_path))
    return StyleReport(
        checked_files=len(source_files),
        violations=tuple(
            sorted(
                violations,
                key=lambda item: (item.path, item.line, item.column, item.rule),
            )
        ),
    )


def run_style(*, start: Path | None = None) -> int:
    """Check repository source, print actionable results, and return an exit code."""

    layout = discover_repository_layout(start)
    report = collect_style_report(layout.repository_root)
    if report.exit_code == 0:
        success(f"Source style passed for {report.checked_files} files.")
        return 0

    error(
        f"Source style found {len(report.violations)} violation(s) "
        f"in {report.checked_files} checked file(s)."
    )
    for violation in report.violations:
        error(violation.format())
    print_help_line("See docs/python-style-guide.md and docs/gdscript-style-guide.md.")
    return 1


def _check_source(path: Path, relative_path: Path) -> list[StyleViolation]:
    relative = relative_path.as_posix()
    try:
        contents = path.read_bytes()
    except OSError as exc:
        return [
            StyleViolation(
                relative,
                1,
                1,
                "SRC001",
                f"source cannot be read: {exc}",
                "restore readable repository permissions and retry",
            )
        ]

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        line, column = _byte_position(contents, exc.start)
        return [
            StyleViolation(
                relative,
                line,
                column,
                "SRC002",
                "source is not valid UTF-8",
                "save the file as UTF-8 without a byte-order mark",
            )
        ]

    violations = _check_common_style(relative, contents, text)
    if text.startswith("\ufeff"):
        text = text[1:]
    if path.suffix == ".py":
        violations.extend(_check_python_style(relative_path, relative, text))
    else:
        violations.extend(_check_gdscript_style(relative, text))
    return violations


def _check_common_style(path: str, contents: bytes, text: str) -> list[StyleViolation]:
    violations: list[StyleViolation] = []
    if text.startswith("\ufeff"):
        violations.append(
            StyleViolation(
                path,
                1,
                1,
                "SRC003",
                "UTF-8 byte-order marks are not allowed",
                "save the file as plain UTF-8",
            )
        )
    if b"\r" in contents:
        line, column = _byte_position(contents, contents.index(b"\r"))
        violations.append(
            StyleViolation(
                path,
                line,
                column,
                "SRC004",
                "carriage-return line endings are not allowed",
                "convert line endings to LF",
            )
        )
    if contents and not contents.endswith(b"\n"):
        lines = text.splitlines() or [""]
        violations.append(
            StyleViolation(
                path,
                len(lines),
                len(lines[-1]) + 1,
                "SRC005",
                "file has no final newline",
                "add one LF newline at the end of the file",
            )
        )

    for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        line = raw_line.rstrip("\r\n")
        if line.endswith((" ", "\t")):
            violations.append(
                StyleViolation(
                    path,
                    line_number,
                    len(line.rstrip(" \t")) + 1,
                    "SRC006",
                    "line has trailing whitespace",
                    "remove spaces and tabs at the end of the line",
                )
            )
        width = len(line.expandtabs(4))
        if width > MAX_LINE_LENGTH:
            violations.append(
                StyleViolation(
                    path,
                    line_number,
                    MAX_LINE_LENGTH + 1,
                    "SRC007",
                    f"line is {width} characters; maximum is {MAX_LINE_LENGTH}",
                    "wrap the expression using the language's normal continuation style",
                )
            )
    return violations


def _check_python_style(
    relative_path: Path,
    path: str,
    text: str,
) -> list[StyleViolation]:
    violations: list[StyleViolation] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        leading = line[: len(line) - len(line.lstrip(" \t"))]
        if "\t" in leading:
            violations.append(
                StyleViolation(
                    path,
                    line_number,
                    leading.index("\t") + 1,
                    "PY001",
                    "Python indentation contains a tab",
                    "indent with four spaces",
                )
            )

    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        violations.append(
            StyleViolation(
                path,
                exc.lineno or 1,
                exc.offset or 1,
                "PY002",
                f"Python syntax cannot be parsed: {exc.msg}",
                "repair the syntax before running the style gate",
            )
        )
        return violations

    if ast.get_docstring(tree, clean=False) is None:
        violations.append(
            StyleViolation(
                path,
                1,
                1,
                "PY003",
                "Python module has no module docstring",
                "add a concise triple-quoted module purpose at the top",
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(
            alias.name == "*" for alias in node.names
        ):
            violations.append(
                StyleViolation(
                    path,
                    node.lineno,
                    node.col_offset + 1,
                    "PY004",
                    "wildcard imports hide module dependencies",
                    "import the required names explicitly",
                )
            )
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            violations.append(
                StyleViolation(
                    path,
                    node.lineno,
                    node.col_offset + 1,
                    "PY005",
                    "bare except catches process-control exceptions",
                    "catch the narrow expected exception type",
                )
            )
        if _is_production_python(relative_path) and isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            violations.extend(_check_python_annotations(path, node))
    return violations


def _check_python_annotations(
    path: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[StyleViolation]:
    violations: list[StyleViolation] = []
    if node.returns is None:
        violations.append(
            StyleViolation(
                path,
                node.lineno,
                node.col_offset + 1,
                "PY006",
                f"production function '{node.name}' has no return annotation",
                "add an explicit return type, including -> None when appropriate",
            )
        )

    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg is not None:
        arguments.append(node.args.vararg)
    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)
    for argument in arguments:
        if argument.arg not in {"self", "cls"} and argument.annotation is None:
            violations.append(
                StyleViolation(
                    path,
                    argument.lineno,
                    argument.col_offset + 1,
                    "PY007",
                    f"production parameter '{argument.arg}' has no type annotation",
                    "add an explicit parameter type",
                )
            )
    return violations


def _check_gdscript_style(path: str, text: str) -> list[StyleViolation]:
    violations: list[StyleViolation] = []
    code_text = _mask_gdscript_non_code(text)
    for line_number, line in enumerate(code_text.splitlines(), start=1):
        leading = line[: len(line) - len(line.lstrip(" \t"))]
        if line.strip() and " " in leading:
            violations.append(
                StyleViolation(
                    path,
                    line_number,
                    leading.index(" ") + 1,
                    "GD001",
                    "GDScript indentation contains a space",
                    "indent code and continuations with tabs",
                )
            )

    for offset in _gdscript_semicolon_offsets(code_text):
        line, column = _text_position(text, offset)
        violations.append(
            StyleViolation(
                path,
                line,
                column,
                "GD002",
                "semicolon combines or terminates statements",
                "put one statement on each line without a semicolon",
            )
        )

    for match in FUNCTION_DECLARATION.finditer(code_text):
        opening_parenthesis = match.end() - 1
        closing_parenthesis = _find_closing_parenthesis(
            code_text,
            opening_parenthesis,
        )
        if closing_parenthesis is None:
            continue
        tail_end = code_text.find(":", closing_parenthesis)
        newline = code_text.find("\n", closing_parenthesis)
        if tail_end == -1 or (newline != -1 and tail_end > newline):
            tail_end = newline if newline != -1 else len(text)
        tail = code_text[closing_parenthesis + 1 : tail_end]
        if "->" not in tail:
            line, column = _text_position(text, match.start())
            violations.append(
                StyleViolation(
                    path,
                    line,
                    column,
                    "GD003",
                    f"function '{match.group('name')}' has no return type",
                    "add an explicit return type, including -> void when appropriate",
                )
            )

        parameters = text[opening_parenthesis + 1 : closing_parenthesis]
        parameter_offset = opening_parenthesis + 1
        for parameter, relative_offset in _split_gdscript_parameters(parameters):
            stripped_parameter = parameter.strip()
            if stripped_parameter and not TYPED_GDSCRIPT_PARAMETER.match(
                stripped_parameter
            ):
                line, column = _text_position(
                    text,
                    parameter_offset + relative_offset,
                )
                violations.append(
                    StyleViolation(
                        path,
                        line,
                        column,
                        "GD004",
                        f"function '{match.group('name')}' has an untyped parameter",
                        "add an explicit parameter type",
                    )
                )
    return violations


def _is_production_python(relative_path: Path) -> bool:
    parts = relative_path.parts
    return relative_path == Path("tools/control.py") or parts[:2] == ("tools", "src")


def _byte_position(contents: bytes, offset: int) -> tuple[int, int]:
    prefix = contents[:offset]
    return prefix.count(b"\n") + 1, len(prefix.rsplit(b"\n", 1)[-1]) + 1


def _text_position(text: str, offset: int) -> tuple[int, int]:
    prefix = text[:offset]
    return prefix.count("\n") + 1, len(prefix.rsplit("\n", 1)[-1]) + 1


def _find_closing_parenthesis(text: str, opening_offset: int) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    in_comment = False
    for offset in range(opening_offset, len(text)):
        character = text[offset]
        if in_comment:
            if character == "\n":
                in_comment = False
            continue
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character == "#":
            in_comment = True
        elif character in {'"', "'"}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return offset
    return None


def _split_gdscript_parameters(parameters: str) -> tuple[tuple[str, int], ...]:
    results: list[tuple[str, int]] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for offset, character in enumerate(parameters):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
        elif character == "," and depth == 0:
            results.append((parameters[start:offset], start))
            start = offset + 1
    results.append((parameters[start:], start))
    return tuple(results)


def _mask_gdscript_non_code(text: str) -> str:
    masked = list(text)
    quote: str | None = None
    quote_length = 1
    escaped = False
    in_comment = False
    offset = 0
    while offset < len(text):
        character = text[offset]
        if in_comment:
            if character == "\n":
                in_comment = False
            else:
                masked[offset] = "x"
            offset += 1
            continue
        if quote is not None:
            marker = quote * quote_length
            if escaped and quote_length == 1:
                escaped = False
                if character != "\n":
                    masked[offset] = "x"
                offset += 1
            elif character == "\\" and quote_length == 1:
                masked[offset] = "x"
                escaped = True
                offset += 1
            elif text.startswith(marker, offset):
                masked[offset : offset + quote_length] = "x" * quote_length
                quote = None
                offset += quote_length
            else:
                if character != "\n":
                    masked[offset] = "x"
                offset += 1
            continue
        if character == "#":
            masked[offset] = "x"
            in_comment = True
            offset += 1
        elif text.startswith(('"""', "'''"), offset):
            masked[offset : offset + 3] = "xxx"
            quote = character
            quote_length = 3
            offset += 3
        elif character in {'"', "'"}:
            masked[offset] = "x"
            quote = character
            quote_length = 1
            offset += 1
        else:
            offset += 1
    return "".join(masked)


def _gdscript_semicolon_offsets(code_text: str) -> tuple[int, ...]:
    return tuple(
        offset for offset, character in enumerate(code_text) if character == ";"
    )
