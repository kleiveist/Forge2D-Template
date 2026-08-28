"""Prepare verified, versioned assets for a reviewed GitHub release."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import re
import shutil

from g2dtool import __version__
from g2dtool.config import ProjectConfigError, load_project_config
from g2dtool.export import (
    EXPORT_TARGETS,
    ExportError,
    ExportTarget,
    validate_export_artifact,
)
from g2dtool.logger import error, print_dry_run, print_help_line, success
from g2dtool.repository import RepositoryLayout, discover_repository_layout


CHANGELOG_HEADING = re.compile(
    r"^## Forge2D-Template v(?P<version>\d+\.\d+\.\d+)"
    r" - (?P<date>\d{4}-\d{2}-\d{2})$",
    re.MULTILINE,
)
GODOT_VERSION = re.compile(r'^config/version="(?P<version>[^"]+)"$', re.MULTILINE)
SEMANTIC_VERSION = re.compile(r"\d+\.\d+\.\d+\Z")


class ReleaseError(RuntimeError):
    """Expected release-preparation failure with concrete recovery steps."""

    def __init__(self, cause: str, solutions: Sequence[str] = ()) -> None:
        super().__init__(cause)
        self.cause = cause
        self.solutions = tuple(solutions)


@dataclass(frozen=True, slots=True)
class ReleaseMetadata:
    """Consistent version metadata required before creating release assets."""

    version: str
    tag: str
    release_date: str
    notes_path: Path


@dataclass(frozen=True, slots=True)
class ReleaseAsset:
    """Map one CI workflow artifact to its public release asset."""

    target: ExportTarget
    workflow_artifact: str
    downloaded_relative: Path
    filename_suffix: str

    def filename(self, version: str) -> str:
        """Return the immutable public filename for a semantic version."""

        return f"Forge2D-Template-v{version}-{self.filename_suffix}"


RELEASE_ASSETS: tuple[ReleaseAsset, ...] = (
    ReleaseAsset(
        target=EXPORT_TARGETS["linux"],
        workflow_artifact="forge2d-template-Linux",
        downloaded_relative=Path(
            "forge2d-template-Linux/linux/Forge2D-Template.x86_64"
        ),
        filename_suffix="linux-x86_64",
    ),
    ReleaseAsset(
        target=EXPORT_TARGETS["windows"],
        workflow_artifact="forge2d-template-Windows",
        downloaded_relative=Path(
            "forge2d-template-Windows/windows/Forge2D-Template.exe"
        ),
        filename_suffix="windows-x86_64.exe",
    ),
    ReleaseAsset(
        target=EXPORT_TARGETS["macos"],
        workflow_artifact="forge2d-template-macOS",
        downloaded_relative=Path(
            "forge2d-template-macOS/macos/Forge2D-Template.zip"
        ),
        filename_suffix="macos-universal.zip",
    ),
)


def run_release_prepare(
    *,
    start: Path | None = None,
    dry_run: bool = False,
) -> int:
    """Prepare release assets and report expected failures without tracebacks."""

    try:
        return _run_release_prepare(start=start, dry_run=dry_run)
    except (ProjectConfigError, ReleaseError) as exc:
        if isinstance(exc, ReleaseError):
            cause = exc.cause
            solutions = exc.solutions
        else:
            cause = str(exc)
            solutions = (
                "Repair config/project.toml before preparing a release.",
            )
        error(f"Release preparation failed: {cause}")
        for solution in solutions:
            print_help_line(solution)
        return 1


def validate_release_metadata(layout: RepositoryLayout) -> ReleaseMetadata:
    """Validate repository version, changelog, and release-note consistency."""

    project = load_project_config(layout.project_config)
    version = project.version
    if SEMANTIC_VERSION.fullmatch(version) is None:
        raise ReleaseError(
            f"Release version must use major.minor.patch, got {version!r}.",
            ("Set project.version to a complete semantic version.",),
        )
    if version != __version__:
        raise ReleaseError(
            f"Version mismatch: config/project.toml has {version}, "
            f"but g2dtool has {__version__}.",
            ("Update project and tooling version metadata in the same reviewed change.",),
        )

    game_text = _read_text(layout.game_project_path, "Godot project metadata")
    game_match = GODOT_VERSION.search(game_text)
    game_version = game_match.group("version") if game_match else None
    if game_version != version:
        raise ReleaseError(
            f"Version mismatch: game/project.godot has {game_version!r}, "
            f"expected {version!r}.",
            ("Set application config/version to the reviewed release version.",),
        )

    readme_path = layout.repository_root / "README.md"
    readme = _read_text(readme_path, "README version metadata")
    if f"- Version: `{version}`" not in readme.splitlines():
        raise ReleaseError(
            f"README.md does not declare release version {version}.",
            (f"Set the README version line to version {version}.",),
        )

    changelog_path = layout.repository_root / "CHANGELOG.md"
    changelog = _read_text(changelog_path, "changelog")
    heading_matches = tuple(CHANGELOG_HEADING.finditer(changelog))
    version_matches = [
        match for match in heading_matches if match.group("version") == version
    ]
    if len(version_matches) != 1:
        raise ReleaseError(
            f"CHANGELOG.md must contain exactly one release heading for v{version}.",
            (f"Add `## Forge2D-Template v{version} - YYYY-MM-DD` once.",),
        )
    if _unreleased_has_entries(changelog):
        raise ReleaseError(
            "CHANGELOG.md still contains Unreleased list entries.",
            (f"Move every intended change into the v{version} release section.",),
        )

    release_date = version_matches[0].group("date")
    try:
        date.fromisoformat(release_date)
    except ValueError as exc:
        raise ReleaseError(
            f"CHANGELOG.md has an invalid release date: {release_date}.",
            ("Use a real calendar date in YYYY-MM-DD format.",),
        ) from exc
    notes_path = layout.repository_root / "docs" / "releases" / f"v{version}.md"
    notes = _read_text(notes_path, "release notes")
    expected_title = f"# Forge2D Template v{version}"
    expected_date = f"Release date: {release_date}"
    note_lines = notes.splitlines()
    if expected_title not in note_lines or expected_date not in note_lines:
        raise ReleaseError(
            f"Release notes do not match v{version} dated {release_date}.",
            (
                f"Use `{expected_title}` and `{expected_date}` in "
                f"{notes_path.relative_to(layout.repository_root)}.",
            ),
        )

    return ReleaseMetadata(
        version=version,
        tag=f"v{version}",
        release_date=release_date,
        notes_path=notes_path,
    )


def _run_release_prepare(*, start: Path | None, dry_run: bool) -> int:
    layout = discover_repository_layout(start)
    metadata = validate_release_metadata(layout)
    _validate_release_paths(layout)
    sources = _validate_downloaded_assets(layout)
    checksum_text = _checksum_document(metadata.version, sources)

    if _prepared_assets_match(layout, metadata.version, sources, checksum_text):
        if dry_run:
            print_dry_run(
                f"Existing release assets for {metadata.tag} are complete and verified."
            )
            success("Release preparation dry-run complete; no changes were made.")
            return 0
        success(
            f"Release assets for {metadata.tag} are already prepared and verified."
        )
        return 0

    if layout.release_asset_directory.exists():
        raise ReleaseError(
            f"Existing release asset directory is incomplete or does not match "
            f"{metadata.tag}: {layout.release_asset_directory}.",
            (
                "Move artifacts/release/assets aside and rerun preparation; "
                "the command never overwrites it.",
            ),
        )

    for asset, source in sources.items():
        destination = layout.release_asset_directory / asset.filename(metadata.version)
        if dry_run:
            print_dry_run(
                f"Would copy verified {asset.target.preset_name} artifact "
                f"from {source.relative_to(layout.repository_root)} to "
                f"{destination.relative_to(layout.repository_root)}"
            )
    if dry_run:
        print_dry_run("Would write artifacts/release/assets/SHA256SUMS.txt")
        success("Release preparation dry-run complete; no changes were made.")
        return 0

    _write_assets_atomically(layout, metadata.version, sources, checksum_text)
    success(
        f"Prepared {len(sources)} verified assets and SHA256SUMS.txt for "
        f"{metadata.tag}."
    )
    return 0


def _validate_release_paths(layout: RepositoryLayout) -> None:
    repository_root = layout.repository_root.resolve()
    release_root = layout.release_directory.resolve(strict=False)
    download_root = layout.release_download_directory.resolve(strict=False)
    asset_root = layout.release_asset_directory.resolve(strict=False)

    if not release_root.is_relative_to(repository_root):
        raise ReleaseError(
            f"Release directory resolves outside the repository: {release_root}.",
            ("Remove symlinks beneath artifacts and retry.",),
        )
    for name, candidate in (("download", download_root), ("asset", asset_root)):
        if not candidate.is_relative_to(release_root):
            raise ReleaseError(
                f"Release {name} directory resolves outside {release_root}: {candidate}.",
                ("Remove symlinks beneath artifacts/release and retry.",),
            )
    if layout.release_directory.is_symlink() or (
        layout.release_directory.exists() and not layout.release_directory.is_dir()
    ):
        raise ReleaseError(
            f"Release root is not a normal directory: {layout.release_directory}.",
            ("Move that path aside manually and retry.",),
        )
    if layout.release_asset_directory.is_symlink() or (
        layout.release_asset_directory.exists()
        and not layout.release_asset_directory.is_dir()
    ):
        raise ReleaseError(
            f"Release asset path is not a normal directory: "
            f"{layout.release_asset_directory}.",
            ("Move that path aside manually and retry.",),
        )


def _validate_downloaded_assets(
    layout: RepositoryLayout,
) -> Mapping[ReleaseAsset, Path]:
    sources: dict[ReleaseAsset, Path] = {}
    resolved_root = layout.release_download_directory.resolve(strict=False)
    for asset in RELEASE_ASSETS:
        source = layout.release_download_directory / asset.downloaded_relative
        if source.is_symlink() or not source.is_file():
            raise ReleaseError(
                f"Downloaded {asset.target.preset_name} artifact is missing or "
                f"not a regular file: {source}.",
                (
                    f"Download workflow artifact {asset.workflow_artifact!r} "
                    "from the approved successful main CI run.",
                ),
            )
        if not source.resolve().is_relative_to(resolved_root):
            raise ReleaseError(
                f"Downloaded artifact resolves outside the release directory: {source}.",
                ("Remove symlinks beneath artifacts/release/downloads and retry.",),
            )
        try:
            validate_export_artifact(source, asset.target)
        except ExportError as exc:
            raise ReleaseError(
                f"Downloaded {asset.target.preset_name} artifact is invalid: "
                f"{exc.cause}",
                (
                    "Discard the downloads and use the artifacts from the exact "
                    "approved successful main CI run.",
                ),
            ) from exc
        sources[asset] = source
    return sources


def _prepared_assets_match(
    layout: RepositoryLayout,
    version: str,
    sources: Mapping[ReleaseAsset, Path],
    checksum_text: str,
) -> bool:
    destination_root = layout.release_asset_directory
    if not destination_root.exists():
        return False

    expected_names = {
        asset.filename(version) for asset in RELEASE_ASSETS
    } | {"SHA256SUMS.txt"}
    try:
        actual_paths = tuple(destination_root.iterdir())
    except OSError as exc:
        raise ReleaseError(
            f"Release asset directory cannot be inspected: {exc}.",
            ("Check repository permissions and retry.",),
        ) from exc
    if {path.name for path in actual_paths} != expected_names:
        return False
    if any(path.is_symlink() or not path.is_file() for path in actual_paths):
        return False

    for asset, source in sources.items():
        destination = destination_root / asset.filename(version)
        if _sha256(destination) != _sha256(source):
            return False
    try:
        actual_checksums = (destination_root / "SHA256SUMS.txt").read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError):
        return False
    return actual_checksums == checksum_text


def _checksum_document(
    version: str,
    sources: Mapping[ReleaseAsset, Path],
) -> str:
    lines = [
        f"{_sha256(source)}  {asset.filename(version)}"
        for asset, source in sources.items()
    ]
    return "\n".join(sorted(lines)) + "\n"


def _write_assets_atomically(
    layout: RepositoryLayout,
    version: str,
    sources: Mapping[ReleaseAsset, Path],
    checksum_text: str,
) -> None:
    try:
        layout.release_directory.mkdir(parents=True, exist_ok=True)
        if not layout.release_directory.resolve().is_relative_to(
            layout.repository_root.resolve()
        ):
            raise ReleaseError(
                f"Release directory escaped the repository: {layout.release_directory}.",
                ("Remove symlinks beneath artifacts and retry.",),
            )
        with TemporaryDirectory(
            prefix=".assets-",
            dir=layout.release_directory,
        ) as temporary_directory:
            staged = Path(temporary_directory)
            for asset, source in sources.items():
                shutil.copyfile(source, staged / asset.filename(version))
            (staged / "SHA256SUMS.txt").write_text(
                checksum_text,
                encoding="utf-8",
                newline="\n",
            )
            staged.replace(layout.release_asset_directory)
    except ReleaseError:
        raise
    except OSError as exc:
        raise ReleaseError(
            f"Release assets could not be written atomically: {exc}.",
            (
                "Check available disk space and permissions, then move any "
                "incomplete assets directory aside before retrying.",
            ),
        ) from exc


def _unreleased_has_entries(changelog: str) -> bool:
    heading = re.search(r"^## Unreleased\s*$", changelog, re.MULTILINE)
    if heading is None:
        return True
    next_heading = re.search(r"^## ", changelog[heading.end() :], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(changelog)
    section = changelog[heading.end() : end]
    return any(line.lstrip().startswith("- ") for line in section.splitlines())


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReleaseError(
            f"Cannot read {label} at {path}: {exc}.",
            ("Restore the reviewed UTF-8 file and retry.",),
        ) from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as asset_file:
            for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ReleaseError(
            f"Cannot hash release artifact {path}: {exc}.",
            ("Check artifact permissions and retry.",),
        ) from exc
    return digest.hexdigest()
