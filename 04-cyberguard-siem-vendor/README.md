# Scenario 04 — CyberGuard SIEM Manager (CRA conformity for a security product)

A **1-hour, CRA-first** training scenario. The trainee plays the compliance officer at a small EU cybersecurity vendor (**CyberGuard Labs SME s.à r.l.**) preparing to place **CyberGuard SIEM Manager v1.0** on the EU market.

Unlike scenarios 1–3 (which audit vulnerable targets), this scenario is **not** about finding vulnerabilities. The engineering work is assumed complete; the trainee's job is to run the **CRA conformity assessment** on CyberFort and produce the readiness pack for the notified-body review.

## Topology

Two VMs on the training subnet:

* **`cyberfort.range.local`** — CyberFort compliance platform (VM1).
* **`siem.range.local`** — The **real CyberGuard SIEM** installed from [`github.com/CyberGuardEU/t4.4_siem_ai_remediation`](https://github.com/CyberGuardEU/t4.4_siem_ai_remediation) (VM2).

The trainee **does not** install the SIEM — the range admin does that before the session. The trainee accesses `siem.range.local` from a browser, notes the product's version and endpoint, and then uses CyberFort to conduct the CRA conformity assessment.

## What's in this folder

```
04-cyberguard-siem-vendor/
├── README.md                          ← this file
├── evidence/                          ← pre-baked artefacts trainees attach to CRA answers
│   ├── cyberguard-sbom.spdx.json           SBOM (SPDX 2.3)
│   ├── penetration-test-report.md          independent pen-test
│   ├── secure-development-lifecycle.md     SDLC policy
│   └── coordinated-vulnerability-disclosure-policy.md
└── docs/
    ├── TRAINEE_HANDBOOK.md            ← step-by-step walkthrough (with CyberFort screenshots)
    ├── INSTRUCTOR_GUIDE.md            ← answer key + scoring rubric
    └── CRA_CONTROL_MAPPING.md         ← evidence → CRA control mapping
```

There is **no `docker-compose.yml`** and no application source in this scenario — the product being assessed is the real CyberGuard SIEM running on its own VM.

## Range-admin deployment (once per range)

On the SIEM VM (`siem.range.local`):

```bash
# 1. Prerequisites: Docker + Docker Compose + OpenSSL, ~16 GB RAM,
#    NVIDIA GPU recommended for the AI SOC-analyst.
git clone https://github.com/CyberGuardEU/t4.4_siem_ai_remediation.git
cd t4.4_siem_ai_remediation
./setup-docker.sh                # ~10–15 min; interactive prompts
```

The setup script prints the final Web UI URL. Use that URL — or the DNS name `https://siem.range.local:8080` — in the trainee handbook's Step 0.

Verify from the CyberFort VM:

```bash
curl -k -s https://siem.range.local:8080/ | head          # landing page HTML
curl -k -s https://siem.range.local:8443/api/version      # if API version endpoint is public
```

## Trainee flow (60 minutes)

1. Open the CyberGuard web console at `https://siem.range.local:8080/` — note the product name, version, and vendor.
2. In CyberFort, register the SIEM as an asset — **CRA Annex III Class II** (security software).
3. Create a **CRA Conformity assessment** scoped to the asset.
4. Answer 16 target CRA questions with evidence from `evidence/`.
5. Export the CRA readiness PDF.

Full walkthrough in [`docs/TRAINEE_HANDBOOK.md`](docs/TRAINEE_HANDBOOK.md).

## Safety

`siem.range.local` runs a real, working SIEM. Host it on an isolated cyber-range network — never on a network reachable from the public internet or a corporate LAN. See the CyberGuard repository's own security notes for its "stripped auth" caveat: the reference build is designed for internal / development networks only.
