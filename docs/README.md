# Documentation

This index is the documentation entry point for Forge2D Template.

## Plans

- [M01 repository bootstrap](plans/M01_repository_bootstrap.md)
- [M02 tooling entrypoint](plans/M02_control_entrypoint.md)
- [M03 release v0.1.0](plans/M03_release_v0_1_0.md)
- [M04 CI integrity hardening](plans/M04_ci_integrity.md)

## Reports

- [M01 repository bootstrap report](reports/M01_repository_bootstrap.md)
- [M02 control entrypoint report](reports/M02_control_entrypoint.md)
- [M03 release v0.1.0 report](reports/M03_release_v0_1_0.md)

## Decisions

- [ADR-0001: Repository layout](decisions/ADR-0001-repository-layout.md)

Forge2D Template is licensed under the MIT License. See `LICENSE`.

## Tooling

- Repository-local control entry point: `python tools/control.py`
- Common bootstrap flow:
  - `python tools/control.py doctor`
  - `python tools/control.py install`
  - `python tools/control.py check`
  - `python tools/control.py forge2d-template run`
