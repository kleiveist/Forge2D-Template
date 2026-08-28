## Summary

<!-- Describe the problem and the smallest complete solution. -->

## Related issue

<!-- Use a closing keyword only when this PR fully resolves the issue. -->

Closes #

## Behavior and compatibility

<!-- Describe user-visible behavior, platforms, compatibility, and limitations. -->

## Validation

<!-- List exact commands and results. Explain any check that was not run. -->

- Focused checks:
- `python tools/control.py style`:
- `python tools/control.py check`:

## Documentation

<!-- List updated docs/changelog, or explain why no documentation changed. -->

## Risk and recovery

<!-- Identify failure modes, security impact, rollout assumptions, and rollback. -->

Risk level: low / medium / high

Recovery:

## Checklist

- [ ] The change is focused and contains no unrelated generated files or caches.
- [ ] Tests cover changed behavior, or the validation section explains why not.
- [ ] Documentation and `CHANGELOG.md` are updated, or the reason is documented.
- [ ] `g2d check` passes, or every blocker is reported with a recovery step.
- [ ] No secret, token, credential, personal data, or machine path is committed.
- [ ] Every new dependency has a reviewed purpose, risk, license, and alternative.
- [ ] User-visible risks, compatibility limits, and recovery are explicit.
