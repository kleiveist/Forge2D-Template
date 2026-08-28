<!-- AUTO-GENERATED:backlink START -->
[← Back](index.md)
<!-- AUTO-GENERATED:backlink END -->
# Documentation

This index is the documentation entry point for Forge2D Template.

## Plans

- [M01 repository bootstrap](plans/M01_repository_bootstrap.md)
- [M02 tooling entrypoint](plans/M02_control_entrypoint.md)
- [M03 release v0.1.0](plans/M03_release_v0_1_0.md)
- [M04 CI integrity hardening](plans/M04_ci_integrity.md)
- [M05 game architecture baseline](plans/M05_game_architecture_baseline.md)
- [M06 cross-platform installer](plans/M06_cross_platform_installer.md)
- [M07 main branch protection](plans/M07_main_branch_protection.md)
- [M08 coding standards](plans/M08_coding_standards.md)
- [M09 cross-platform export system](plans/M09_export_system.md)
- [M10 semantic input baseline](plans/M10_input_baseline.md)
- [M11 community health](plans/M11_community_health.md)

## Architecture

- [Runtime architecture overview](architecture/runtime-overview.md)

## Reports

- [M01 repository bootstrap report](reports/M01_repository_bootstrap.md)
- [M02 control entrypoint report](reports/M02_control_entrypoint.md)
- [M03 release v0.1.0 report](reports/M03_release_v0_1_0.md)
- [M05 game architecture baseline report](reports/M05_game_architecture_baseline.md)

## Decisions

- [ADR-0001: Repository layout](decisions/ADR-0001-repository-layout.md)
- [ADR-0002: Runtime folder layout](decisions/ADR-0002-runtime-folder-layout.md)
- [ADR-0003: Application scenes and navigation](decisions/ADR-0003-application-scenes-and-navigation.md)
- [ADR-0004: Scoped Autoload services](decisions/ADR-0004-scoped-autoload-services.md)
- [ADR-0005: Runtime dependency rules](decisions/ADR-0005-runtime-dependency-rules.md)

Forge2D Template is licensed under the MIT License. See `LICENSE`.

## Community

- [Contribution workflow](../CONTRIBUTING.md)
- [Security policy and private reporting](../SECURITY.md)
- GitHub issue chooser: focused bug and feature forms; external blank issues are
  deliberately disabled.

## Tooling

- [Cross-platform installation](installation.md)
- [Cross-platform exports](exporting.md)
- [Semantic input baseline](input.md)
- [Publishing a GitHub release](releasing.md)
- [Forge2D Template v0.1.0 release notes](releases/v0.1.0.md)
- [Main branch protection and manual GitHub setup](branch-protection.md)
- [Mandatory Python coding standard](python-style-guide.md)
- [Mandatory GDScript coding standard](gdscript-style-guide.md)
- Repository-local control entry point: `python tools/control.py`
- Common bootstrap flow:
  - `python tools/control.py install --dry-run`
  - `python tools/control.py install --yes`
  - `python tools/control.py doctor`
  - `python tools/control.py style`
  - `python tools/control.py check`
  - `python tools/control.py export linux --dry-run`
  - `python tools/control.py release prepare --dry-run`
  - `python tools/control.py forge2d-template run`
