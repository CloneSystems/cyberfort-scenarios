# CyberFort cyber-range training scenarios

A set of three deliberately-vulnerable training exercises that showcase the **CyberFort** compliance platform on a three-VM cyber range, plus a **live pilot** run against a real commercial product. Each training scenario is from a **different sector** and is assessed against a **different compliance framework**, so they together demonstrate the full breadth of the platform; scenario 04 then proves it on a product that is actually going to market.

| # | Folder | Sector | Compliance framework | Target stack | Primary CyberFort capabilities |
|---|--------|--------|----------------------|--------------|--------------------------------|
| 1 | `01-portpilot-maritime/`         | **Maritime**             | **CRA** (Cyber Resilience Act, Annex I + Vuln. Handling) | Flask + PostgreSQL                          | Nmap + ZAP + Semgrep + OSV + CRA conformity assessment + AI assistant |
| 2 | `02-smartgrid-meter-energy/`     | **Energy**               | **NIS2** (Article 21(2) measures)                       | Flask admin + Mosquitto MQTT + Modbus TCP   | Nmap (OT ports) + ZAP + Semgrep + OSV + NIS2 assessment |
| 3 | `03-netlink-isp-digital-infra/`  | **Digital infrastructure** | **ISO 27001:2022** (Annex A gap analysis)            | Node.js Express + PostgreSQL                | Nmap + ZAP + Semgrep (Node.js) + OSV (npm) + ISO 27001 assessment + JWT-forgery chain |
| 4 | `04-clonesystems-seuxdr-siem/`   | **ICT security vendor** &middot; *pilot* | **CRA** (full manufacturer conformity route, Annex III Class I) | Go + React SIEM/XDR with local-LLM remediation | SBOM Generator + OSV + Semgrep + VEX + CRA Technical File + conformity assessment + gap analysis + EU DoC readiness + CE marking checklist |

## Range topology

```
                     ┌───────────────────────────────┐
                     │ VM1 — CyberFort               │
                     │   Frontend  :5173             │
                     │   Backend   :8000             │
                     │   Nmap      :8011             │
                     │   ZAP       :8010             │
                     │   Semgrep   :8013             │
                     │   OSV       :8012             │
                     │   Ollama    :11434            │
                     └───────────────┬───────────────┘
                                     │ scans
                ┌────────────────────┴────────────────────┐
                │                                         │
   ┌────────────▼─────────────┐               ┌───────────▼──────────────┐
   │ VM2 — scenario target    │               │ VM3 — scenario target    │
   │ docker compose up        │               │ docker compose up        │
   └──────────────────────────┘               └──────────────────────────┘
```

All three VMs sit on the same isolated training subnet. CyberFort reaches each scenario by IP. Scenarios run on either VM2 or VM3 depending on the day's session plan; only one scenario should be active per target VM at a time because their port mappings overlap (Postgres on 5432 in S1+S3).

## What the scenarios show together

* **Four sectors** — maritime port operator, energy distribution operator, ISP, and an ICT security vendor. These mirror the SME profiles the CYBERFORT proposal explicitly targets.
* **Three frameworks** — CRA (product-side regulatory compliance), NIS2 (operator-side essential-entity obligations), ISO 27001 (general ISMS gap analysis). Each one is seeded in CyberFort with question texts the trainee actually answers.
* **Four technology stacks** — Python + Flask, Python + OT protocols (Modbus + MQTT), Node.js + EJS, and Go + React. Different scanner footprints (Semgrep covers Python, Node and Go; OSV covers PyPI, npm and Go modules).
* **One workflow** — register product → run scanners → convert findings to risks → answer the assessment → attach evidence → export PDF readiness report.
* **Two altitudes.** Scenarios 01–03 are two-hour *training* exercises against seeded targets: the trainee learns the workflow, and the findings are known in advance. Scenario 04 is a six-month *pilot* against a real product with unknown findings. It exercises the CRA-specific modules the training scenarios never touch — SBOM Generator, VEX statements, the six CRA Technical File pages, the EU Declaration of Conformity readiness score and the CE Marking Checklist — and then closes the loop: remediate the product, re-assess, and show the movement (7% → 70%). Run 01 first to learn the platform; run 04 to prove it.

## How to use the scenarios

For each scenario the intended flow is:

1. Cyber range admin deploys the scenario stack on a target VM (`docker compose up -d --build`; for scenario 04, `range/deploy.sh`).
2. Trainee logs into CyberFort on VM1.
3. Trainee follows `docs/TRAINEE_HANDBOOK.md` for that scenario — register the target as a product, run the relevant scanners, fill in the assessment, export the PDF readiness report.
4. Instructor reviews the PDF and the risk-register entries against `docs/INSTRUCTOR_GUIDE.md`.

Each scenario is sized for **two hours** of trainee time at intermediate level.

## Repo layout

```
cyber-range-scenarios/
├── README.md                          ← this index
├── scripts/
│   └── md_to_pdf.py                   ← markdown → PDF helper used to render the docs
├── 01-portpilot-maritime/             ← Maritime / CRA / Flask
├── 02-smartgrid-meter-energy/         ← Energy / NIS2 / Flask + MQTT + Modbus
├── 03-netlink-isp-digital-infra/      ← Digital infra / ISO 27001 / Node.js
└── 04-clonesystems-seuxdr-siem/       ← ICT vendor / CRA pilot / Go + React (real product)
```

Scenarios 01–03 follow the same structure: `README.md`, `docker-compose.yml`, application source, `docs/` (handbook + instructor guide + control mapping). Scenario 04 carries no application source — its target is a shipping commercial product in its own repository — so instead of a `docker-compose.yml` it ships a `range/` deployment kit that fetches the product at a pinned reference and adapts it for a range VM, in either a baseline or a remediated mode. Its `docs/` set is `PILOT_RUNBOOK.md`, `CRA_CONFORMITY_MAPPING.md`, `ASSESSOR_GUIDE.md`, `REMEDIATION_BACKLOG.md` and `PILOT_TIMELINE.md`, plus the pilot presentation under `presentation/`. PDFs of all the markdown docs ship next to their `.md` counterparts and are regenerated via `python3 scripts/md_to_pdf.py <file>.md`.

## Safety

Scenarios 01–03 are intentionally vulnerable. Scenario 04's target is a real product whose remediation actions delete files, kill processes and rewrite host firewall rules as root. **Run all four only on an isolated cyber-range network** — never on the public internet or on a corporate LAN.

## Status

* ✓ Scenario 01 (PortPilot Maritime, CRA): complete, smoke-tested, PDFs rendered.
* ✓ Scenario 02 (SmartGrid Meter Energy, NIS2): complete, smoke-tested, PDFs rendered.
* ✓ Scenario 03 (NetLink ISP Digital Infrastructure, ISO 27001): complete, smoke-tested, PDFs rendered.
* ✓ Scenario 04 (Clone Systems SEUXDR, CRA pilot): complete, and closed the loop over a six-month engagement (Feb–Jul 2026). Baseline 2 of 30 CRA objectives compliant (2026-07-29, `t4.4_siem_ai_remediation` @ `00a95ad`); remediation sprint 1 committed 2026-07-30 (`c4ba16b`, `cbd092b`, 60 files, 8,261 lines); re-assessed at 21 of 30 — **7% → 70%**. Screenshots captured from the live `CRA Extended` tenant; 27-slide pilot deck rendered.
