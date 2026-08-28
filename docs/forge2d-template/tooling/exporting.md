<!-- AUTO-GENERATED:backlink START -->
[← Back](tooling.md)
<!-- AUTO-GENERATED:backlink END -->
# Cross-Platform Exports

`g2d export` creates reviewed Godot release exports for Linux, Windows, and
macOS without changing system Python. All output stays below the ignored
repository directory `artifacts/exports/`.

## Prerequisites

Run the normal repository setup first:

```text
python tools/control.py install --yes
python tools/control.py doctor
```

The exporter requires Godot 4 and export templates that exactly match the
installed Godot version. Godot 4.7.2 is the repository-tested version. Because
the official cross-platform template archive is approximately 1.2 GB,
`g2d install` does not download it automatically.

Install templates through **Editor > Manage Export Templates** in Godot. A
manual download should come only from the official
[Godot 4.7.2 build release](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable)
and should be checked against that release's `SHA512-SUMS.txt` before import.
Do not copy templates into the repository or commit them.

## Commands and Outputs

Validate every prerequisite and show the exact command first:

```text
python tools/control.py export linux --dry-run
python tools/control.py export windows --dry-run
python tools/control.py export macos --dry-run
```

Create one release export by omitting `--dry-run`:

```text
python tools/control.py export linux
python tools/control.py export windows
python tools/control.py export macos
```

An installed CLI can use the equivalent `g2d export ...` commands.

| Target | Godot preset | Exact local output |
| --- | --- | --- |
| `linux` | `Linux` | `artifacts/exports/linux/Forge2D-Template.x86_64` |
| `windows` | `Windows` | `artifacts/exports/windows/Forge2D-Template.exe` |
| `macos` | `macOS` | `artifacts/exports/macos/Forge2D-Template.zip` |

The preset paths in `game/export_presets.cfg` and the CLI destinations are the
same canonical locations. Arbitrary output paths are intentionally unsupported.
This prevents accidental writes outside the checkout and gives CI exact artifact
names to validate.

## Safety Contract

`--dry-run` performs read-only repository, preset, Godot-version, template, and
path checks. It prints the release command but does not start an export, create
directories, delete stale output, or modify Godot project data.

A real export creates only the selected output directory. It removes an existing
regular file at that exact artifact path so stale output cannot hide a failure.
It refuses to replace a directory or symbolic link, never recursively clears the
artifact root, and times out after ten minutes. A successful Godot process is
still rejected unless the exact output exists, is non-empty, and has a valid ELF,
PE, or ZIP signature for the selected target.

The Linux and Windows presets embed the project pack in one executable. The
macOS preset produces a universal x86_64/arm64 ZIP application bundle; the
required ETC2/ASTC import format is enabled in `game/project.godot`. Generated
exports, templates, editor state, signing identities, and credential files must
remain outside Git.

Godot 4.4 and newer also creates `*.gd.uid` sidecars for scripts. Those small,
stable UID files are versioned source metadata rather than cache and must remain
beside their scripts. Only the generated `game/.godot/` editor data is ignored.

## Signing, Notarization, and Distribution

CI outputs are test artifacts, not production releases:

- The Linux artifact has no distribution signature.
- Windows Authenticode signing is disabled in the reviewed preset. Unsigned
  downloads can trigger Microsoft Defender SmartScreen or other reputation
  checks.
- macOS uses Godot's built-in ad-hoc signature and disables notarization. An
  ad-hoc signature is not a Developer ID signature; downloaded builds can be
  blocked by Gatekeeper.

Before public distribution, configure platform signing in a controlled release
workflow. Store certificates, passwords, Apple team identifiers, API keys, and
notarization credentials in a secret manager or GitHub Actions secrets. Godot's
local secret values belong in `game/.godot/export_credentials.cfg`, which is
already excluded through `.godot/`; never add those values to
`export_presets.cfg`.
Apple notarization also requires an appropriate Developer ID identity and Apple
credentials. Those production release steps are deliberately not automated by
`g2d export`.

## CI Validation and Retention

The native Ubuntu, Windows, and macOS jobs install the official Godot editor.
On the Python 3.11 job for each host, CI additionally downloads the matching
cross-platform template archive, verifies its SHA-512 entry, checks all three
required release templates, and exports the host's native target. The Python
3.14 jobs continue to run the complete repository gate without repeating the
large template download.

CI independently checks the exact artifact name and non-empty size before
`actions/upload-artifact@v7` uploads it with seven-day retention. GitHub Actions
archives do not preserve executable permission bits; after downloading the
Linux artifact, run:

```text
chmod +x Forge2D-Template.x86_64
```

Uploaded workflow artifacts are temporary validation evidence. The reviewed
[GitHub release procedure](releasing.md) explains how to select the exact green
protected-main run, revalidate and checksum all three exports, create an
annotated immutable tag, publish, and independently verify the assets.

## Troubleshooting

- **Godot 4 is unavailable:** run `python tools/control.py install`, then
  `python tools/control.py doctor`. If Godot is installed in a non-standard
  location, set `GODOT4_BIN` to that executable for the command.
- **A release template is missing:** compare `godot4 --version` with the template
  directory named in the error. Install the exact matching archive through
  Godot's template manager; a template for another patch or stability channel
  is not interchangeable.
- **A preset is missing or invalid:** restore the reviewed
  `game/export_presets.cfg`. Do not work around the fixed path by adding an
  absolute machine-specific destination.
- **The destination is a directory or symlink:** move it aside manually. The
  exporter intentionally does not recursively delete or follow it.
- **Godot exits unsuccessfully:** open the project and review
  **Project > Export** for import, preset, or template errors. The CLI includes
  the last useful process messages and recovery steps.
- **The output is missing, empty, or has an invalid signature:** reinstall the
  official templates, verify free disk space, and retry. A zero exit code alone
  does not make an artifact valid.
- **The export times out:** close other Godot processes, allow project imports to
  finish in the editor, verify disk space, and rerun the printed command for
  detailed observation.
