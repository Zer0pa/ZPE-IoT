<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-IoT Masthead" width="100%">
</p>

# Security Policy

<p>
  <img src=".github/assets/readme/section-bars/supported-versions.svg" alt="SUPPORTED VERSIONS" width="100%">
</p>

Security fixes are applied to the current development line and the latest private-stage release bundle in this repository.

The actively maintained security surface includes:

- the nested Python distribution in `python/`
- the bundled native wheel path from `python/native/`
- the Rust codec kernel in `core/`
- the repo-local CLI and release scripts

<p>
  <img src=".github/assets/readme/section-bars/reporting-a-vulnerability.svg" alt="REPORTING A VULNERABILITY" width="100%">
</p>

1. Do not open a public issue for suspected vulnerabilities.
2. Email `security@zer0pa.com` with subject `ZPE-IoT security report`.
3. Include:
   - affected commit SHA or bundle identifier
   - operating system, Python version, and Rust toolchain
   - reproduction steps
   - impact assessment
   - suggested mitigation if known

<p>
  <img src=".github/assets/readme/section-bars/response-commitment.svg" alt="RESPONSE COMMITMENT" width="100%">
</p>

- Initial acknowledgement within 2 business days.
- Triage decision within 7 business days.
- Remediation target for confirmed high severity within 30 days, or documented mitigation if patch timing differs.

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

- Coordinated disclosure is preferred.
- Public disclosure occurs only after a fix or mitigation exists.
- Security release notes should include affected versions, identifiers, and upgrade guidance when a public release exists.

This file does not create a public package publication claim. It governs the private-stage repo surface only.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-IoT Tertiary Masthead" width="100%">
</p>
