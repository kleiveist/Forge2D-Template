<!-- AUTO-GENERATED:backlink START -->
[← Back](index.md)
<!-- AUTO-GENERATED:backlink END -->
# Publishing a GitHub Release

This procedure publishes an immutable Forge2D Template version only from a
reviewed commit on protected `main`. It deliberately separates release-asset
preparation, annotated tagging, and GitHub publication so an operator can audit
the selected commit at every irreversible boundary.

## Publication Gate

Do not create or push a version tag from a pull-request branch. Before starting,
the complete release pull request must be merged, `origin/main` must contain the
intended changes, and a push CI run for that exact commit must have all eight
required jobs green:

- `ubuntu-latest / Python 3.11`
- `ubuntu-latest / Python 3.14`
- `windows-latest / Python 3.11`
- `windows-latest / Python 3.14`
- `macos-latest / Python 3.11`
- `macos-latest / Python 3.14`
- `Linux / Debian 13`
- `Linux / Arch Linux`

Use a clean checkout with GitHub CLI authentication and no pre-existing release
or remote tag. Fetch without rewriting local work:

```text
git fetch --prune origin
git status --short --branch
gh auth status --hostname github.com
git ls-remote --tags origin refs/tags/v0.1.0
gh release view v0.1.0 --repo kleiveist/Forge2D-Template
```

The last two commands must report that the tag and release do not exist. If
either exists, stop: a published version tag must never move or be overwritten,
and it must not be silently reused.

## Select and Audit the Main Commit

Resolve the commit from the protected remote branch rather than from a local
topic branch:

```text
release_sha="$(git rev-parse origin/main)"
git show --no-patch --decorate "$release_sha"
gh api repos/kleiveist/Forge2D-Template/branches/main --jq .commit.sha
```

The API SHA and `release_sha` must be identical. Find the successful push run
for that exact SHA:

```text
gh api "repos/kleiveist/Forge2D-Template/actions/workflows/ci.yml/runs?branch=main&event=push&head_sha=${release_sha}&status=success" --jq '.workflow_runs[] | [.id, .head_sha, .status, .conclusion, .html_url]'
```

Select its run ID as `release_run_id`, then inspect every job and make the run's
exit status part of the operator record:

```text
gh run view "$release_run_id" --repo kleiveist/Forge2D-Template --json headSha,event,status,conclusion,jobs,url
gh run view "$release_run_id" --repo kleiveist/Forge2D-Template --exit-status
```

Stop unless the event is `push`, `headSha` equals `release_sha`, the conclusion
is `success`, and the eight job names above are all successful. A green
pull-request run alone is not sufficient evidence for the final `main` commit.

## Download and Prepare Assets

The native Python 3.11 jobs upload the exact validated Linux, Windows, and macOS
exports for seven days. Download all three artifacts from the selected run:

```text
gh run download "$release_run_id" --repo kleiveist/Forge2D-Template --name forge2d-template-Linux --name forge2d-template-Windows --name forge2d-template-macOS --dir artifacts/release/downloads
python tools/control.py release prepare --dry-run
python tools/control.py release prepare
```

`release prepare` independently checks the repository version, Godot version,
changelog heading, release-note date, empty `Unreleased` section, exact artifact
paths, non-zero sizes, and ELF/PE/ZIP signatures. It then copies the inputs to
fixed versioned filenames and writes `artifacts/release/assets/SHA256SUMS.txt`.
The dry-run writes nothing. A real run atomically creates the complete asset
directory and never overwrites a mismatched existing directory; an identical
second run succeeds without rewriting files.

Independently recompute all hashes with the standard library:

```text
python - <<'PY'
from pathlib import Path
import hashlib

root = Path("artifacts/release/assets")
expected = {
    filename: digest
    for digest, filename in (
        line.split("  ", 1)
        for line in (root / "SHA256SUMS.txt").read_text(
            encoding="utf-8"
        ).splitlines()
    )
}
actual = {
    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in root.iterdir()
    if path.name != "SHA256SUMS.txt"
}
if actual != expected:
    raise SystemExit("Release checksum verification failed")
print("Release checksums verified")
PY
```

Also run the repository gate at the exact selected commit before tagging:

```text
git switch --detach "$release_sha"
python tools/control.py check
```

Return to the normal branch after publication with `git switch
feat/release-readiness` or the operator's reviewed branch name. Do not use a
destructive reset to change branches.

## Create the Annotated Tag

Create the local tag with an explicit commit and verify that Git stored an
annotated tag object rather than a lightweight reference:

```text
git tag --annotate v0.1.0 --message "Forge2D Template v0.1.0" "$release_sha"
git cat-file -t refs/tags/v0.1.0
git rev-list --max-count=1 v0.1.0
```

The first verification must print `tag`; the second must print `release_sha`.
Only then push that one explicit reference:

```text
git push origin refs/tags/v0.1.0
```

Never use `--force` for a version tag. After the remote tag exists, leave it on
that commit permanently even if later publication steps fail.

## Publish and Verify the Release

`--verify-tag` prevents GitHub CLI from silently creating a lightweight tag on
the wrong commit. List every asset explicitly so an unrelated file cannot be
attached by a broad glob:

```text
gh release create v0.1.0 --repo kleiveist/Forge2D-Template --verify-tag --latest --title "Forge2D Template v0.1.0" --notes-file docs/releases/v0.1.0.md artifacts/release/assets/Forge2D-Template-v0.1.0-linux-x86_64 artifacts/release/assets/Forge2D-Template-v0.1.0-windows-x86_64.exe artifacts/release/assets/Forge2D-Template-v0.1.0-macos-universal.zip artifacts/release/assets/SHA256SUMS.txt
gh release view v0.1.0 --repo kleiveist/Forge2D-Template --json tagName,targetCommitish,isDraft,isPrerelease,url,assets
```

For an independent remote check, use a new temporary directory and download the
published assets:

```text
release_verify_dir="$(mktemp -d)"
gh release download v0.1.0 --repo kleiveist/Forge2D-Template --dir "$release_verify_dir"
(
  cd "$release_verify_dir"
  python - <<'PY'
from pathlib import Path
import hashlib

root = Path(".")
expected = {
    filename: digest
    for digest, filename in (
        line.split("  ", 1)
        for line in (root / "SHA256SUMS.txt").read_text(
            encoding="utf-8"
        ).splitlines()
    )
}
actual = {
    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in root.iterdir()
    if path.name != "SHA256SUMS.txt"
}
if actual != expected:
    raise SystemExit("Published release checksum verification failed")
print("Published release checksums verified")
PY
)
```

Confirm through the Git database API that the tag reference points to an
annotated tag object and that its target equals `release_sha`:

```text
test "$(gh api repos/kleiveist/Forge2D-Template/git/ref/tags/v0.1.0 --jq .object.type)" = "tag"
tag_object_sha="$(gh api repos/kleiveist/Forge2D-Template/git/ref/tags/v0.1.0 --jq .object.sha)"
test "$(gh api "repos/kleiveist/Forge2D-Template/git/tags/${tag_object_sha}" --jq .object.sha)" = "$release_sha"
```

Record the main commit SHA, CI run URL, release URL, asset names, and successful
checksum verification in the M03 report and Issue #4 comment.

## Recovery Without Rewriting History

- Before the tag is pushed, a mistaken local tag can be removed with `git tag
  --delete v0.1.0`, corrected, and rechecked.
- If the remote tag push succeeds but release creation fails, keep the tag and
  rerun `gh release create ... --verify-tag` after fixing only the publication
  problem.
- If publication succeeds with missing metadata, use `gh release edit` while
  leaving the tag and assets unchanged. A missing verified asset can be added
  with `gh release upload` after comparing its local checksum.
- Do not use `gh release upload --clobber`, force-push a tag, delete a published
  tag, or use `gh release delete --cleanup-tag` to disguise a bad release. If
  released code or an attached binary is wrong, disclose it and publish a new
  patch version such as `v0.1.1`.
- Workflow artifacts expire after seven days. If they expire before tagging,
  rerun CI on the unchanged protected-main commit and repeat the full audit; do
  not substitute an untracked local export.

GitHub release downloads do not convey a Unix executable permission bit. After
checksum verification, Linux users may need `chmod +x
Forge2D-Template-v0.1.0-linux-x86_64` before starting the binary.
