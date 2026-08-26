"""Emoji-aware logging helpers for Forge2D Template tooling."""

from __future__ import annotations

from collections.abc import Sequence
import sys


STATUS_ICONS: dict[str, str] = {
    "pass": "✅",
    "warn": "⚠️",
    "fail": "❌",
    "error": "🛑",
    "info": "ℹ️",
    "success": "✅",
    "running": "🚀",
    "plan": "🛠️",
    "help": "💡",
}


def _print(message: str, *, stream: object = sys.stdout) -> None:
    try:
        print(message, file=stream, flush=True)  # noqa: T201 - user-facing command output
    except UnicodeEncodeError:
        encoding = getattr(stream, "encoding", None) or "ascii"
        safe_message = message.encode(
            encoding,
            errors="replace",
        ).decode(encoding)
        print(safe_message, file=stream, flush=True)  # noqa: T201


def _stream() -> object:
    return sys.stdout


def log_status(status: str, name: str, detail: str) -> str:
    icon = STATUS_ICONS.get(status.lower(), "🔹")
    label = status.upper()
    return f"{icon} [{label}] {name}: {detail}"


def print_status_line(status: str, name: str, detail: str) -> None:
    _print(log_status(status, name, detail), stream=_stream())


def command_plan(text: str) -> str:
    return f"{STATUS_ICONS['plan']} [PLAN] {text}"


def print_command_plan(text: str) -> None:
    _print(command_plan(text), stream=_stream())


def dry_run(text: str) -> str:
    return f"{STATUS_ICONS['plan']} [DRY-RUN] {text}"


def print_dry_run(text: str) -> None:
    _print(dry_run(text), stream=_stream())


def message(icon: str, label: str, text: str) -> str:
    return f"{icon} [{label}] {text}" if label else f"{icon} {text}"


def info(text: str) -> None:
    _print(message(STATUS_ICONS["info"], "INFO", text), stream=_stream())


def success(text: str) -> None:
    _print(message(STATUS_ICONS["success"], "OK", text), stream=_stream())


def warning(text: str) -> None:
    _print(message(STATUS_ICONS["warn"], "WARN", text), stream=_stream())


def error(text: str) -> None:
    _print(message(STATUS_ICONS["error"], "ERROR", text), stream=_stream())


def running(text: str) -> None:
    _print(message(STATUS_ICONS["running"], "RUN", text), stream=_stream())


def help_line(text: str) -> str:
    return message(STATUS_ICONS["help"], "TIP", text)


def print_help_line(text: str) -> None:
    _print(help_line(text), stream=_stream())


def join_command(command: Sequence[str] | Sequence[object]) -> str:
    return " ".join(map(str, command))
