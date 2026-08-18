# Secure Development Lifecycle (SDLC) — CyberGuard Labs

**Document version:** 2.0 &middot; **Effective date:** 1 January 2026 &middot; **Owner:** CyberGuard R&D

---

## Purpose

This document describes how CyberGuard Labs integrates security throughout the design, development, testing, release, and end-of-support phases of every product with digital elements — currently the **CyberGuard SIEM Manager**, agents, and Console web UI. It is provided as evidence to CRA Annex I objective **3(k)** (updates address vulnerabilities) and **Article 13** (manufacturer obligations).

---

## 1. Design phase

* Threat model produced against STRIDE and CWE Top 25; reviewed by two engineers not on the feature team.
* Security requirements captured in the feature ticket before implementation starts.
* Data flow diagram maintained in `/docs/dfd/` and reviewed at each major release.

## 2. Implementation

* Mandatory secure-coding checklist attached to every PR (input validation, output encoding, no `os/exec` on user-supplied strings, no `InsecureSkipVerify`, no hardcoded secrets).
* Semgrep `p/default`, `p/golang`, and `p/security-audit` run on every push; merge blocked on High or Critical findings.
* Dependencies gated by `govulncheck` and OSV; PRs adding a dependency with a Known-Exploited advisory are auto-rejected.

## 3. Testing

* Unit tests targeting all authorization branches (>85% branch coverage).
* Integration tests using ephemeral SIEM instances.
* Quarterly independent penetration test (see `penetration-test-report.md`).
* Continuous fuzzing on parser code paths (`gofuzz`).

## 4. Release

* SBOM (SPDX 2.3) generated for every release — see `cyberguard-sbom.spdx.json`.
* Release notes include a security summary.
* Signed release artefacts (Sigstore/cosign).
* Container images scanned by Trivy + Grype before publication.

## 5. Post-release

* Security advisories published per the CVD policy (`coordinated-vulnerability-disclosure-policy.md`).
* Patches shipped within **7 days** for High/Critical vulnerabilities, **30 days** for Medium.
* Support period: 60 months from release, aligned with CRA Article 13(8).
* End-of-support notice published at least 12 months in advance.

## 6. Roles

| Role | Owner |
|------|-------|
| SDLC policy owner | R&D Director |
| PSIRT lead | Head of Security |
| Release manager | Product Owner |
| Board oversight | CTO, quarterly report |

---

*Reviewed annually. Last review: 15 December 2025.*
