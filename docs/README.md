# Documentation

This index is the documentation entry point until M02 expands the architecture
and testing guides.

## Plans

- [M01 repository bootstrap](plans/M01_repository_bootstrap.md)
- [M02 tooling entrypoint (in progress)](plans/M02_control_entrypoint.md)

## Reports

- [M01 repository bootstrap report](reports/M01_repository_bootstrap.md)

## Decisions

- [ADR-0001: Repository layout](decisions/ADR-0001-repository-layout.md)

The license choice is still open. See `config/project.toml` for its authoritative
status; do not infer a license from repository visibility.

## Tooling

- Repository-local control entry point: `python tools/control.py`
- Common bootstrap flow:
  - `python tools/control.py doctor`
  - `python tools/control.py install`
  - `python tools/control.py Forge2D run`
