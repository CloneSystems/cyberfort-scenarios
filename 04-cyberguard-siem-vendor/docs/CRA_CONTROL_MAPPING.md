# Scenario 04 — CRA control mapping (SIEM manufacturer)

The bridge between the **evidence bundle** shipped with this scenario and the **CRA framework as it is actually represented in CyberFort**.

> **Different from scenarios 1–3:** those linked *findings* to CRA controls. This scenario is about a *manufacturer demonstrating conformity*, so this document links **evidence artefacts** to CRA controls instead.

---

## How the CRA framework is structured in CyberFort

![CRA framework structure in CyberFort](screenshots/diagram-cra-hierarchy.png)

CyberGuard SIEM Manager v1.0 is classified under CRA **Annex III Class II** — *important product with digital elements — security software (intrusion detection)*. This classification triggers:

* Full **Annex I** essential cybersecurity requirements (1, 2, 3a–3k).
* Full **Vulnerability Handling** requirements (VH-1 through VH-8).
* **Conformity path:** internal audit + **notified-body review of the technical documentation** (Annex VII Module B/C).
* Support period of **60 months** (Article 13(8)).

---

## Evidence bundle → CRA question mapping

### `cyberguard-sbom.spdx.json` — Software Bill of Materials

SPDX 2.3 machine-readable SBOM covering the manager binary, Go standard library and Alpine base image.

| CRA question (verbatim from seed) | Annex I objective |
|-----------------------------------|-------------------|
| Q38 — *"Do you identify and document vulnerabilities and components contained in your products with digital elements?"* | **VH-1** *(component inventory + SBOM)* |
| Q39 — *"Do you draw up a software bill of materials in a commonly used and machine-readable format?"* | **VH-1** |
| Q40 — *"Does your software bill of materials cover at least the top-level dependencies of the products?"* | **VH-1** |

---

### `penetration-test-report.md` — Independent penetration test

Black-box + grey-box test by Aegean Cyber Testing Ltd, June 2026.

| CRA question | Annex I objective |
|--------------|-------------------|
| Q1 — *"Have you undertaken an assessment of the cybersecurity risks associated with your product with digital elements?"* | **1** *(designed to ensure appropriate level of cybersecurity)* |
| Q13 — *"Are your products with digital elements delivered without any known exploitable vulnerabilities?"* | **2** *(no known exploitable vulnerabilities)* |
| Q20 — *"Do you ensure protection from unauthorized access by appropriate control mechanisms?"* | **3b** *(protection from unauthorised access)* |
| Q21 — *"Do you implement authentication, identity or access management systems?"* | **3b** |
| Q41 — *"Do you apply effective and regular tests and reviews of the security of your products with digital elements?"* | **VH-3** *(effective and regular security tests)* |

---

### `secure-development-lifecycle.md` — SDLC + patch policy

Vendor's SDLC covering design → implementation → testing → release → post-release.

| CRA question | Annex I objective |
|--------------|-------------------|
| Q10 — *"Do you systematically document relevant cybersecurity aspects concerning your products with digital elements?"* | **VH-1** |
| Q14 — *"Are your products made available on the market with a secure by default configuration?"* | **3a** *(secure by default configuration)* |
| Q16 — *"Do you ensure that vulnerabilities can be addressed through security updates?"* | **3k** *(updates address vulnerabilities)* |
| Q17 — *"Are automatic security updates installed within an appropriate timeframe enabled as a default setting?"* | **3k** |
| Q23 — *"Do you protect the confidentiality of stored, transmitted or otherwise processed data through encryption?"* | **3c** *(confidentiality)* |
| Q25 — *"Do you protect the integrity of stored, transmitted or otherwise processed data, commands, programs and configuration?"* | **3d** *(integrity)* |
| Q34 — *"Do you provide security-related information by recording and monitoring relevant internal activity?"* | **3j** *(security-relevant info recording)* |

---

### `coordinated-vulnerability-disclosure-policy.md` — CVD policy

Vendor's PSIRT contact, SLAs, disclosure procedure, and market-surveillance-authority contact.

| CRA question | Annex I / Vuln-Handling objective |
|--------------|------------------------------------|
| Q42 — *"Once a security update is made available, do you share and publicly disclose information about fixed vulnerabilities?"* | **VH-4** *(publicly disclose fixed vulnerabilities)* |
| Q43 — *"Do you provide a description of vulnerabilities, affected products, impacts, severity and remediation information?"* | **VH-4** |
| Q44 — *"Do you have a policy on coordinated vulnerability disclosure in place and enforced?"* | **VH-5** *(coordinated disclosure policy)* |
| Q46 — *"Do you provide a contact address for reporting vulnerabilities discovered in your products?"* | **VH-6** *(facilitate sharing of vulnerability info)* |

---

## Annex I + Vulnerability Handling coverage matrix

<style>
table.cov { width: 100%; border-collapse: collapse; margin: 10px 0; }
table.cov th, table.cov td { border: 1px solid #c9c9c9; padding: 5px 8px; text-align: left; vertical-align: top; font-size: 9.5pt; }
table.cov th { background: #0c6b60; color: #fff; }
table.cov td.yes { background: #e1f3df; color: #1b5e20; font-weight: 600; text-align: center; width: 90px; }
table.cov td.partial { background: #fdf6c8; color: #6b5400; font-weight: 600; text-align: center; }
table.cov td.no  { background: #ececec; color: #777; text-align: center; }
table.cov tr td:first-child { width: 80px; font-weight: 600; color: #0c6b60; text-align: center; }
</style>

<table class="cov">
<thead><tr><th>Annex I obj.</th><th>Title (paraphrased)</th><th>Covered?</th><th>Evidence artefact</th></tr></thead>
<tbody>
<tr><td>1</td><td>Designed for appropriate level of cybersecurity</td><td class="yes">✓</td><td>Pen-test report — STRIDE threat model</td></tr>
<tr><td>2</td><td>Delivered without known exploitable vulnerabilities</td><td class="yes">✓</td><td>Pen-test report — 0 critical, retests attached</td></tr>
<tr><td>3a</td><td>Secure by default configuration</td><td class="yes">✓</td><td>SDLC §2 — secure-coding checklist</td></tr>
<tr><td>3b</td><td>Protection from unauthorised access</td><td class="yes">✓</td><td>Pen-test — RBAC + MFA</td></tr>
<tr><td>3c</td><td>Confidentiality (encryption)</td><td class="yes">✓</td><td>SDLC — TLS 1.3 + mTLS</td></tr>
<tr><td>3d</td><td>Integrity protection</td><td class="yes">✓</td><td>SDLC — Sigstore-signed releases</td></tr>
<tr><td>3e</td><td>Data minimisation</td><td class="partial">partial</td><td>Trainee notes agent log-retention rules</td></tr>
<tr><td>3f</td><td>Availability / DoS resilience</td><td class="partial">partial</td><td>Pen-test out of scope for load testing</td></tr>
<tr><td>3g</td><td>Limit impact on other devices / networks</td><td class="yes">✓</td><td>SDLC — rate-limits on agent → manager comms</td></tr>
<tr><td>3h</td><td>Limit attack surfaces / external interfaces</td><td class="yes">✓</td><td>SDLC — mTLS-only agent registration</td></tr>
<tr><td>3i</td><td>Reduce impact of incident (exploit mitigation)</td><td class="yes">✓</td><td>Alpine + non-root container user</td></tr>
<tr><td>3j</td><td>Security-relevant info recording</td><td class="yes">✓</td><td>The product is itself a SIEM</td></tr>
<tr><td>3k</td><td>Updates can address vulnerabilities</td><td class="partial">partial</td><td>Auto-updates on manager; agents pull on check-in (documented gap on Q17)</td></tr>
<tr><td>VH-1</td><td>Component inventory + SBOM</td><td class="yes">✓</td><td>SBOM (SPDX 2.3)</td></tr>
<tr><td>VH-2</td><td>Address &amp; remediate without delay</td><td class="yes">✓</td><td>SDLC §5 — 7-day patch SLA for High/Critical</td></tr>
<tr><td>VH-3</td><td>Effective and regular security tests</td><td class="yes">✓</td><td>Pen-test + continuous fuzzing</td></tr>
<tr><td>VH-4</td><td>Publicly disclose fixed vulnerabilities</td><td class="yes">✓</td><td>CVD policy — Publication</td></tr>
<tr><td>VH-5</td><td>Coordinated disclosure policy</td><td class="yes">✓</td><td>CVD policy — main body</td></tr>
<tr><td>VH-6</td><td>Facilitate sharing of vulnerability info</td><td class="yes">✓</td><td>CVD policy — Contact</td></tr>
<tr><td>VH-7</td><td>Secure distribution of updates</td><td class="yes">✓</td><td>SDLC — Sigstore/cosign + secure channels</td></tr>
<tr><td>VH-8</td><td>Free-of-charge disseminated patches</td><td class="yes">✓</td><td>SDLC — patches free during 60-month support</td></tr>
</tbody>
</table>

**Coverage summary:** **18 of 21** Annex I + Vulnerability-Handling objectives are directly covered by the evidence bundle. Three are marked partial and should trigger a compensating-control note in the assessment:

* **3e** *(data minimisation)* — retention rules for agent logs need explicit documentation.
* **3f** *(availability / DoS resilience)* — load testing is not part of the pen-test scope; add before the notified-body review.
* **3k** *(automatic updates)* — the air-gapped-agent case (documented on Q17).

---

## What the trainee actually clicks (assessment flow)

1. **Assessments → + New Assessment** — Framework: `CRA`, Type: `Conformity`, Scope: `Asset / Product → CyberGuard SIEM Manager`.
2. **Open the assessment card** — the 52-question questionnaire opens.
3. **For each of the 16 target questions** in Step 3 of the handbook: pick the verdict, write the Evidence Description, click **Attach File(s)**, upload the matching artefact from `evidence/`, click **Save Answer**.
4. **Export PDF** from the toolbar — that PDF plus the four evidence files form the CRA technical documentation submission.

---

## Why this matters in the proposal context

The CYBERFORT proposal targets SME manufacturers who face CRA obligations before placing products on the EU market. **CyberGuard Labs SME s.à r.l.** is exactly that profile — a small Cypriot vendor placing a security product (Annex III Class II) into the single market. Producing the CRA conformity pack end-to-end in an hour, with CyberFort orchestrating the questionnaire and evidence flow, is the entire value proposition of the platform for this audience.
