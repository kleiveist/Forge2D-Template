# ADR-0001: Separate Repository Concerns by Top-Level Directory

- Status: Accepted
- Date: 2026-08-26

## Context

Forge2D needs a small starting structure that supports a Godot runtime and Python
maintenance tooling without prematurely coupling their architectures. Tests,
documentation, and shared policy also need obvious ownership.

## Decision

Use these top-level boundaries:

| Path | Responsibility |
| --- | --- |
| `game/` | Godot project source, scenes, and project settings |
| `tools/` | Installable Python package source and its Python tests |
| `docs/` | Plans, milestone reports, and architectural decisions |
| `config/` | Project identity and toolchain policy shared across components |

Repository-wide metadata and contributor rules remain at the root. Generated
state and machine-specific caches are ignored rather than assigned a source
directory.

## Consequences

- Runtime and maintenance tooling can be tested and packaged independently;
  Python tests remain inside the `tools/` ownership boundary.
- Cross-component policy has one discoverable location instead of being embedded
  in either implementation.
- Future directories require a demonstrated responsibility that does not fit an
  existing boundary.
- This decision does not define gameplay architecture, asset processing, release
  packaging, or an open-source license.
