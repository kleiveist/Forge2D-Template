<!-- AUTO-GENERATED:backlink START -->
[← Back](tooling.md)
<!-- AUTO-GENERATED:backlink END -->
# GitHub Repository Metadata

GitHub description, homepage, topics, and template status are server-side
settings. They are not controlled by a checkout or copied back into Git history.
Forge2D Template keeps its reviewed desired values in
[`../../../.github/repository-metadata.json`](../../../.github/repository-metadata.json) so
maintainers can detect drift and template users can see what must be customized.

## Canonical Values

| Field | Value | Rationale |
| --- | --- | --- |
| Description | `Minimal Godot 4 2D game template with repository-local Python tooling for setup, checks, exports, and releases.` | Concisely identifies the engine, 2D purpose, template role, and local tooling. |
| Topics | `2d-game`, `game-development`, `game-template`, `gdscript`, `godot`, `godot-4`, `python` | Covers purpose, engine, and implementation languages without synonyms or promotional tags. |
| Homepage | Not configured | There is no maintained canonical website, documentation deployment, or playable destination outside this repository. A repository URL would be redundant. |
| Template repository | Enabled | The canonical project is intended to generate independent downstream repositories. |

GitHub topic names use lowercase letters, numbers, and hyphens, contain at most
50 characters, and are limited to 20 per repository. Topics are public even for
private repositories. Keep the smaller reviewed set above unless the project's
actual purpose changes.

## Apply and Audit the Canonical Repository

Repository administrators can edit the **About** panel on GitHub or use the API.
The following calls update only the reviewed description and exact topic set;
they do not modify visibility, branches, features, or the intentionally empty
homepage:

```text
gh auth status --hostname github.com
gh api --method PATCH \
  repos/kleiveist/Forge2D-Template \
  -f 'description=Minimal Godot 4 2D game template with repository-local Python tooling for setup, checks, exports, and releases.'
gh api --method PUT \
  repos/kleiveist/Forge2D-Template/topics \
  -f 'names[]=2d-game' \
  -f 'names[]=game-development' \
  -f 'names[]=game-template' \
  -f 'names[]=gdscript' \
  -f 'names[]=godot' \
  -f 'names[]=godot-4' \
  -f 'names[]=python'
```

Audit the complete result after every change:

```text
gh api repos/kleiveist/Forge2D-Template \
  --jq '{description, homepage, topics, is_template}'
```

The expected homepage value is `null`, the expected template value is `true`,
and description/topics must exactly match the versioned JSON contract. Never
write a token or GitHub CLI credential into that file or a command transcript.

## Customize a Repository Created from This Template

Server-side metadata describes the resulting project, not its source template.
After creating a repository from Forge2D Template, its owner should review:

1. Replace the repository name, GitHub description, and topics with accurate
   downstream-game identity and technology. Remove Forge2D-specific discovery
   topics that no longer apply.
2. Configure a homepage only when a maintained canonical website, documentation
   deployment, store page, or playable build exists. Leave it empty instead of
   linking to an abandoned or redundant destination.
3. Decide whether the downstream repository should itself remain a template.
   Most games should not enable the template setting.
4. Replace canonical owner/repository URLs in README badges, release commands,
   the private `security/advisories/new` route, and issue-form contact links.
5. Configure server-side branch protection and private vulnerability reporting;
   the versioned policy and `SECURITY.md` guidance cannot enable those settings
   for another repository automatically.
6. Re-run `python tools/control.py check`, inspect the rendered README/community
   templates on the default branch, and audit the API response before announcing
   the new project.

Do not claim a language, engine version, platform, release destination, security
contact, or maintenance status that the downstream repository does not actually
support.
