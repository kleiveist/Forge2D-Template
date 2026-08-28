"""Tests for the dependency-free Python and GDScript style gate."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.style import (
    StyleViolation,
    collect_style_report,
    discover_source_files,
    run_style,
)


class StyleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "repository"
        (self.root / ".git").mkdir(parents=True)

    def test_accepts_compliant_python_and_multiline_gdscript(self) -> None:
        self._write(
            "tools/src/example.py",
            '"""Provide one typed example."""\n\n\ndef greet(name: str) -> str:\n'
            '    """Return a greeting."""\n\n    return f"Hello {name}"\n',
        )
        self._write(
            "game/example.gd",
            "extends Node\n\n\nfunc greet(\n\t\tname: String,\n) -> String:\n"
            '\treturn "Hello %s" % name\n',
        )

        report = collect_style_report(self.root)

        self.assertEqual(report.exit_code, 0)
        self.assertEqual(report.checked_files, 2)
        self.assertEqual(report.violations, ())

    def test_source_discovery_excludes_generated_directories(self) -> None:
        source = self._write("tools/source.py", '"""Tracked source."""\n')
        self._write(".venv/generated.py", "not valid python")
        self._write("build/generated.gd", " invalid")

        discovered = discover_source_files(self.root)

        self.assertEqual(discovered, (source,))

    def test_reports_encoding_newline_whitespace_and_length_failures(self) -> None:
        path = self.root / "tools" / "tests" / "common.py"
        path.parent.mkdir(parents=True)
        path.write_bytes(
            b'\xef\xbb\xbf"""Bad common style.""" \r\n#' + (b"x" * 101)
        )

        report = collect_style_report(self.root)

        self.assertEqual(
            self._rules(report),
            {"SRC003", "SRC004", "SRC005", "SRC006", "SRC007"},
        )

    def test_reports_invalid_utf8_without_attempting_language_checks(self) -> None:
        path = self.root / "tools" / "invalid.py"
        path.parent.mkdir(parents=True)
        path.write_bytes(b'"""Broken encoding."""\n\xff\n')

        report = collect_style_report(self.root)

        self.assertEqual(self._rules(report), {"SRC002"})

    def test_reports_python_structure_and_production_typing_failures(self) -> None:
        self._write(
            "tools/src/bad.py",
            '"""Exercise structural rules."""\n\nfrom values import *\n\n\n'
            "def recover(value):\n"
            "    try:\n"
            "        return value\n"
            "    except:\n"
            "        return None\n",
        )
        self._write("tools/tests/missing_docstring.py", "VALUE = 1\n")
        self._write(
            "tools/tests/tabbed.py",
            '"""Exercise indentation."""\n\n\ndef tabbed() -> None:\n\treturn None\n',
        )

        report = collect_style_report(self.root)

        self.assertEqual(
            self._rules(report),
            {"PY001", "PY003", "PY004", "PY005", "PY006", "PY007"},
        )

    def test_reports_python_syntax_failure(self) -> None:
        self._write("tools/tests/syntax.py", '"""Broken syntax."""\n\ndef broken(:\n')

        report = collect_style_report(self.root)

        self.assertEqual(self._rules(report), {"PY002"})

    def test_reports_gdscript_indent_statement_and_typing_failures(self) -> None:
        self._write(
            "game/bad.gd",
            "extends Node\n\n\nfunc bad(value):\n"
            '\tvar label := "semicolon; in a string" # comment ;\n'
            "\tpass; pass\n"
            "    pass\n",
        )

        report = collect_style_report(self.root)

        self.assertEqual(self._rules(report), {"GD001", "GD002", "GD003", "GD004"})

    def test_gdscript_rules_ignore_comments_and_string_contents(self) -> None:
        self._write(
            "game/string_content.gd",
            "extends Node\n\n\nfunc embedded_source() -> String:\n"
            '\treturn """\nfunc fake(value):\n    pass; # not code\n"""\n',
        )

        report = collect_style_report(self.root)

        self.assertEqual(report.violations, ())

    def test_run_style_returns_failure_with_actionable_output(self) -> None:
        self._write("tools/tests/no_docstring.py", "VALUE = 1\n")
        output = StringIO()

        with redirect_stdout(output):
            exit_code = run_style(start=self.root)

        self.assertEqual(exit_code, 1)
        self.assertIn("tools/tests/no_docstring.py:1:1 [PY003]", output.getvalue())
        self.assertIn("Fix:", output.getvalue())
        self.assertIn("docs/python-style-guide.md", output.getvalue())

    def test_violation_format_is_stable_and_compiler_friendly(self) -> None:
        violation = StyleViolation(
            "tools/example.py",
            4,
            9,
            "PY999",
            "example problem",
            "apply the example repair",
        )

        self.assertEqual(
            violation.format(),
            "tools/example.py:4:9 [PY999] example problem "
            "Fix: apply the example repair",
        )

    def _write(self, relative_path: str, contents: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8", newline="\n")
        return path

    @staticmethod
    def _rules(report) -> set[str]:
        return {violation.rule for violation in report.violations}


if __name__ == "__main__":
    unittest.main()
