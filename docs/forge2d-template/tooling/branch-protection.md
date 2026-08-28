<!-- AUTO-GENERATED:backlink START -->
[← Back](tooling.md)
<!-- AUTO-GENERATED:backlink END -->
# Main Branch Protection

The GitHub `main` branch accepts changes through pull requests only. Required CI
checks must succeed on a branch that is up to date with `main` before GitHub can
merge it. These controls live in GitHub, not in a clone, so maintainers of forks
and repositories created from this template must configure them separately.

The repository-owned policy payload is
[`../../../.github/branch-protection-main.json`](../../../.github/branch-protection-main.json).
It contains no credentials and is the reviewable reference for the live rule.

## Enforced Policy

The rule targets the exact branch name `main` and enables:

- **Require a pull request before merging**, with no bypass actors.
- Zero required approvals while this is a single-collaborator repository. A pull
  request is still mandatory; approval by the author would not count. Increase
  this to one approval when a second trusted reviewer is available.
- **Require status checks to pass before merging** and **Require branches to be
  up to date before merging**.
- All eight checks from `.github/workflows/ci.yml`, restricted to the GitHub
  Actions app:
  - `Linux / Arch Linux`
  - `Linux / Debian 13`
  - `macos-latest / Python 3.11`
  - `macos-latest / Python 3.14`
  - `ubuntu-latest / Python 3.11`
  - `ubuntu-latest / Python 3.14`
  - `windows-latest / Python 3.11`
  - `windows-latest / Python 3.14`
- **Require conversation resolution before merging**.
- **Require linear history**. Use squash or rebase merge; merge commits are not
  accepted on `main`.
- **Do not allow bypassing the above settings**, including for administrators.
- Force pushes and branch deletion remain disabled.

Signed commits, Code Owner approval, deployments, and a merge queue are not
required. They can be added later when the repository has the corresponding
signing, ownership, deployment, or multi-contributor workflow.

## Manual GitHub Setup

An administrator can reproduce the rule in the GitHub web interface:

1. Open **Settings → Branches → Branch protection rules → Add rule**.
2. Set **Branch name pattern** to `main`.
3. Enable **Require a pull request before merging**. Do not add bypass actors.
   Leave required approvals at zero for a solo repository; set it to one or more
   once an independent reviewer is available.
4. Enable **Require status checks to pass before merging** and **Require branches
   to be up to date before merging**. Select every check listed above and choose
   **GitHub Actions** as its expected source.
5. Enable **Require conversation resolution before merging**, **Require linear
   history**, and **Do not allow bypassing the above settings**.
6. Keep **Allow force pushes** and **Allow deletions** disabled, then save the
   rule.

GitHub only offers recently observed checks in the selector. Run the CI workflow
on `main` once before configuring a new repository if a check name is missing.

## API Application and Audit

Maintainers with repository administration permission can apply the checked-in
policy without copying credentials into the repository:

```text
gh auth status --hostname github.com
gh api --method PUT \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  repos/kleiveist/Forge2D-Template/branches/main/protection \
  --input .github/branch-protection-main.json
```

Use the fork owner's repository name in the API path when applying the template
elsewhere. Audit the effective server-side rule with:

```text
gh api repos/kleiveist/Forge2D-Template/branches/main/protection
```

The payload deliberately uses the app-bound `checks` form without the legacy
`contexts` field. With API version `2022-11-28`, sending both forms together was
rejected with HTTP 422 as conflicting schema alternatives, while the checked-in
`checks`-only form applied successfully. Keep that distinction when editing the
policy.

Never commit a token, `hosts.yml`, or another GitHub authentication file.

## Maintenance

Treat CI job names as a compatibility interface: renaming a matrix entry changes
its required check name. Update the workflow, policy payload, documentation, and
live GitHub rule together. Introduce and observe replacement checks before
removing old required checks so pull requests are not left waiting for a context
that can no longer run.

When a second trusted reviewer joins, manually require at least one approval and
consider enabling stale-review dismissal plus approval of the most recent push.
Do not enable those review controls while only the pull-request author can review,
because administrators cannot bypass this rule.
