# CI and Branch Policy

Date: 2026-02-19

## Required Checks on `main`

The following checks are required before merge:

1. `Rust Test + Clippy`
2. `Python Test + Build`
3. `Strict DT Smoke`
4. `Benchmark + Report Sanity`
5. `Packaging warnings treated as errors`

No direct pushes to `main` are allowed when branch protection is enabled.

## Workflow Files

- `.github/workflows/ci.yml`
- `.github/workflows/packaging_warnings.yml`

## Release Tagging

Conventional tags:

- `vMAJOR.MINOR.PATCH` (for release candidates and formal releases)

Example:

```bash
git tag -a v0.1.0 -m "ZPE-IoT v0.1.0"
git push origin v0.1.0
```

## Changelog Flow

Generate a changelog section from merged commits between tags:

```bash
git log --pretty=format:'- %h %s (%an)' v0.0.0..HEAD > docs/CHANGELOG_PENDING.md
```

Then promote curated content into release notes during RC packaging.

## Fail-Fast Packaging Rule

`packaging_warnings.yml` fails the pipeline if Python build output contains packaging warnings or deprecation warnings. This prevents shipping warning-tainted artifacts.
