# Penetration test report — CyberGuard SIEM Manager v1.0

**Client:** CyberGuard Labs SME s.à r.l. &middot; **Assessor:** Aegean Cyber Testing Ltd (independent) &middot; **Engagement dates:** 15–25 June 2026 &middot; **Report version:** 1.0

---

## Executive summary

An independent black-box + grey-box penetration test was conducted against **CyberGuard SIEM Manager v1.0.0** before its planned Q3 2026 EU-market release. The scope included the manager HTTP API on port 8080, the agent-registration mTLS listener on 8081, and the web UI. The engagement was structured to support the vendor's **CRA Article 13(5) — effective and regular tests of the security of the product**.

**Findings summary:**

| Severity | Count | Status at report date |
|----------|-------|-----------------------|
| Critical | 0 | — |
| High     | 1 | Remediated in v1.0.0-rc2 |
| Medium   | 3 | 2 remediated · 1 accepted (documented) |
| Low      | 4 | 3 remediated · 1 wontfix (see finding L-04) |
| Info     | 6 | Advisory notes |

No critical vulnerabilities remain in the shipping build. Remaining issues are documented and tracked in the CyberGuard PSIRT tracker.

---

## Testing methodology

* **Black-box** external testing of the exposed HTTP API and web UI (OWASP WSTG 4.2).
* **Grey-box** review with product documentation and non-production credentials.
* **SAST** review of the Go source against Semgrep `p/default` + `p/golang` rulesets.
* **Dependency review** using `govulncheck` and OSV against `go.mod` and container layers.
* **Threat model** review against the STRIDE categories, prioritised for a SIEM (integrity of alert stream and availability of the manager).

---

## Retest evidence

All *High* and *Medium (remediated)* findings were retested on 24 June 2026 against build `v1.0.0-rc2`. Retests are attached as separate HTML reports (`retest-H-01.html`, `retest-M-01.html`, `retest-M-02.html`) in the evidence bundle.

---

## Sign-off

*Signed:* Anna Papageorgiou, Lead Assessor, Aegean Cyber Testing Ltd &middot; 25 June 2026.

---

*This report is provided as evidence to CRA conformity assessments under CRA Article 13(5). It does not by itself constitute a declaration of conformity.*
