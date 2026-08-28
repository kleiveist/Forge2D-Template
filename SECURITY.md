# Security Policy

## Supported Versions

Security fixes target the actively maintained repository state:

| Version or ref | Receives security fixes |
| --- | --- |
| Protected `main` | Yes |
| Latest published `0.1.x` release | Yes |
| Older releases, commits, and downstream forks | No |

Before the first release is published, protected `main` is the only supported
ref. Downstream templates and games maintain their own security policies and
private reporting routes.

## Report a Vulnerability Privately

Do not disclose a suspected vulnerability in a public issue, pull request,
discussion, commit, or log. Submit a
[private GitHub vulnerability report](https://github.com/kleiveist/Forge2D-Template/security/advisories/new)
instead. GitHub Security Advisories restrict the report and follow-up discussion
to the reporter and authorized repository maintainers.

Include, when available:

- a concise description and expected security impact;
- the affected version, commit, platform, and component;
- reproducible steps or a minimal proof of concept;
- required privileges, configuration, and attack preconditions;
- relevant logs with credentials, tokens, personal data, and unrelated secrets
  removed; and
- known mitigations, workarounds, or disclosure constraints.

Do not access, retain, or alter third-party data while researching a report.
Stop testing if it could disrupt a service or expose another person's data.

## Response and Disclosure

Maintainers target an acknowledgement within three business days, initial
triage within seven business days after acknowledgement, and a status update at
least every seven days while coordinated remediation is active. These are
response targets, not a guarantee; severity, reproducibility, upstream work,
and release safety can change remediation time.

The advisory is the source of truth for severity, affected versions, credit,
patch coordination, and an agreed disclosure date. Please keep details private
until maintainers confirm that affected users have a reasonable mitigation or
the parties agree on another disclosure plan. Maintainers will explain a
rejection or duplicate classification in the private advisory.

## Maintainers of Forks

GitHub private vulnerability reporting is a repository setting and is not
inherited automatically by every copy of this template. Fork and template
owners must enable **Settings → Code security → Private vulnerability
reporting**, replace the canonical link above with their repository route, and
verify it from a non-maintainer account. If they cannot enable that feature,
they must publish an organization-managed private contact before claiming
security-report support; never commit a personal credential or access token.
