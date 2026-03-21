# Security Policy

## Supported Surface

Security fixes are applied to the current development line and the latest private-stage release bundle in this repository.

The actively maintained security surface includes:

- the nested Python distribution in `python/`
- the bundled native wheel path from `python/native/`
- the Rust codec kernel in `core/`
- the repo-local CLI and release scripts

## Reporting a Vulnerability

1. Do not open a public issue for suspected vulnerabilities.
2. Email `security@zer0pa.com` with subject `ZPE-IoT security report`.
3. Include:
   - affected commit SHA or bundle identifier
   - operating system, Python version, and Rust toolchain
   - reproduction steps
   - impact assessment
   - suggested mitigation if known

## Response Targets

- Initial acknowledgement within 2 business days.
- Triage decision within 7 business days.
- Remediation target for confirmed high severity within 30 days, or documented mitigation if patch timing differs.

## Disclosure Process

- Coordinated disclosure is preferred.
- Public disclosure occurs only after a fix or mitigation exists.
- Security release notes should include affected versions, identifiers, and upgrade guidance when a public release exists.
