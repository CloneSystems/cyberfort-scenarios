# Scenario 04 — CyberGuard SIEM Manager (CRA conformity for a security product)

A **1-hour, CRA-first** training scenario. The trainee plays the compliance officer at a small EU cybersecurity vendor (CyberGuard Labs SME s.à r.l.) preparing to place **CyberGuard SIEM Manager v1.0** on the EU market.

Unlike scenarios 1–3, this scenario is **not** about finding vulnerabilities in a target. The engineering work is assumed complete; the trainee's job is to run the **CRA conformity assessment** on CyberFort and produce the readiness pack.

## What's in the box

```
04-cyberguard-siem-vendor/
├── README.md                          ← this file
├── docker-compose.yml                 ← 1 container
├── target/                            ← Go landing-page for the SIEM product
│   ├── Dockerfile
│   ├── go.mod
│   ├── main.go                        ← 60 LOC HTTP server
│   └── static/                        ← product landing page
├── evidence/                          ← pre-baked artefacts to attach to CRA answers
│   ├── cyberguard-sbom.spdx.json           SBOM (SPDX 2.3)
│   ├── penetration-test-report.md          independent pen-test
│   ├── secure-development-lifecycle.md     SDLC policy
│   └── coordinated-vulnerability-disclosure-policy.md
└── docs/
    ├── TRAINEE_HANDBOOK.md            ← step-by-step walkthrough (with CyberFort screenshots)
    ├── INSTRUCTOR_GUIDE.md            ← answer key + scoring rubric
    └── CRA_CONTROL_MAPPING.md         ← evidence → CRA control mapping
```

## Topology

* **VM1** runs CyberFort (or use the hosted reference instance at `https://access.cyber-fort.eu/`).
* **VM2** runs this scenario's stack — one container serving a product landing page.

## Deploy on VM2

```bash
git clone <repo-url> /srv/cyberguard-scenario
cd /srv/cyberguard-scenario/04-cyberguard-siem-vendor
docker compose up -d --build
```

Verify:

```bash
docker compose ps          # expect 1 container Up
curl http://localhost:8080/healthz     # {"status":"ok"}
```

Open `http://<VM2-IP>:8080/` — the product landing page tells the trainee what CyberGuard is, its CRA classification, and its vendor.

## Trainee flow (60 minutes)

1. Read the landing page (Step 0 of the handbook).
2. Register CyberGuard as an asset in CyberFort — **Annex III Class II**.
3. Create a **CRA Conformity assessment** scoped to the asset.
4. Answer 16 target CRA questions with evidence from `evidence/`.
5. Export the CRA readiness PDF.

Full walkthrough in [`docs/TRAINEE_HANDBOOK.md`](docs/TRAINEE_HANDBOOK.md).

## Safety

Unlike scenarios 1–3, this reference build is **not** deliberately vulnerable. It exists only to give the CyberFort scanners something to point at during the optional Step 5 exercise. Still, host it on an isolated cyber-range network as a matter of principle.
