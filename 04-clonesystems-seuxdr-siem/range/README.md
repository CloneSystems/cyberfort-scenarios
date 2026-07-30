# Scenario 04 — cyber-range deployment kit

Scenarios 01–03 ship their own `docker-compose.yml` because the target *is* the scenario — a purpose-built vulnerable app that exists only for the exercise. Scenario 04 is different: the target is **Clone Systems' real product**, which lives in its own repository with its own compose file and its own build. Vendoring a copy here would fork a shipping product and go stale on the first release.

So this directory is a **deployment kit**, not a stack: it fetches the product at a pinned reference, makes it survive a range VM, and gives the range admin a repeatable deploy / verify / reset cycle.

```
range/
├── README.md              ← this file
├── .env.example           ← host IP, ports, which product ref to deploy
├── deploy.sh              ← clone at a ref, generate certs, bring the stack up
├── verify.sh              ← health-check the four ports and the containers
├── reset.sh               ← wipe state between trainee sessions
└── docker-compose.range.yml  ← range overlay (see "The GPU problem" below)
```

---

## The two modes — this is the point of the scenario

The product has a **before** and an **after**, and both are deployable. That is what scenarios 01–03 cannot offer.

| Mode | Product ref | What a trainee sees |
|------|-------------|---------------------|
| `baseline` | `00a95ad` on `main` | The manager API is **completely unauthenticated**. `curl` the remediation endpoint with no credential and delete a file on an agent. All 22 TLS routes open. No SBOM, no `SECURITY.md`, no CI. This is the 2-of-30 (7%) product. |
| `remediated` | `cra/remediation-sprint-1` | The same endpoint returns **401**. Targets are validated, so a crafted path is refused. `SECURITY.md`, `VERSION`, `CHANGELOG.md`, `.github/workflows/` and nine `docs/cra/` documents exist. This is the 21-of-30 (70%) product. |

The exercise that makes this worth the range time: **run the same CyberFort conformity assessment against both, and watch the objective statuses move.** The trainee does not take the instructor's word that remediation changed the compliance position — they grade it themselves, twice.

```bash
RANGE_PRODUCT_REF=00a95ad ./deploy.sh                    # baseline
RANGE_PRODUCT_REF=cra/remediation-sprint-1 ./deploy.sh   # remediated
```

---

## What this target costs, honestly

This is a **much heavier** target than scenarios 01–03. Budget for it before scheduling a session.

| Requirement | Value | Why |
|-------------|-------|-----|
| RAM | **32 GB** | `phi4:14b` needs it; the compose file reserves 8 GB and caps Ollama at 16 GB |
| Architecture | **amd64** | the product's compose pins `platform: linux/amd64`; on ARM it runs under emulation and is unusably slow |
| Disk | ~25 GB | ~9 GB model, plus the Wazuh indexer and two container images |
| GPU | NVIDIA, optional | see below — without one, AI analysis times out |
| First bring-up | **25–40 minutes** | Wazuh all-in-one install is 10–15 min; the model pull is another 10–20 |
| Ports published | 8080, 8081, 8443, 11434 | front end, agent enrolment (mTLS), manager API, Ollama |

### The GPU problem

The product's compose declares a **hard NVIDIA device reservation**:

```yaml
reservations:
  devices:
    - driver: nvidia
      count: 1
      capabilities: [gpu]
```

On a range VM with no NVIDIA GPU, `docker compose up` **fails to start Ollama** rather than falling back to CPU. `deploy.sh` handles this: with `RANGE_GPU=off` it strips that reservation from the working copy and records what it changed, so the stack starts CPU-only.

Be aware of the consequence, because it changes what the trainee can demonstrate: the manager caps LLM analysis at a **hard-coded 60-second context** (`message_processor.go:1065`), overriding the configured 360 s. On CPU, `phi4:14b` will usually exceed that and analyses will time out. Detection, alerting and the manual remediation path all still work — only the AI analysis step is unreliable. For a session that needs the AI path, either use a GPU host or set `RANGE_MODEL=phi3:mini` to trade quality for latency.

### Two other range-hostile details

The compose file hard-codes `hostname: B650M-D3HP-AX` — a developer's motherboard model. `deploy.sh` replaces it with `RANGE_HOSTNAME`. And the manager runs `privileged: true`, which is required for systemd inside the container but means **the container boundary is not a security boundary**. That is one more reason this target belongs on an isolated subnet and nowhere else.

---

## Deploy

On the target VM (VM2 in the range topology):

```bash
cp .env.example .env
$EDITOR .env                      # set RANGE_HOST_IP at minimum
./deploy.sh
./verify.sh
```

`deploy.sh` will:

1. Clone `git@github.com:CyberGuardEU/t4.4_siem_ai_remediation.git` to `$RANGE_INSTALL_DIR` (default `/srv/seuxdr`) and check out `$RANGE_PRODUCT_REF`.
2. Write `$RANGE_HOST_IP` into `localhost.ext` and `manager/manager.yaml`, which otherwise carry a hard-coded `192.168.0.154`.
3. Apply the range adjustments — hostname, and the GPU reservation if `RANGE_GPU=off`.
4. Run `gen-certs.sh`, then `docker compose up --build -d`.
5. Run `startup.sh TEST` inside the manager to install Wazuh and register the systemd unit.

It is idempotent: re-running it re-checks out the ref and rebuilds without wiping trainee data. Use `reset.sh` for that.

> ⚠️ The product's remediation actions **delete files, kill processes and rewrite host firewall rules as root** on any enrolled agent. Enrol only throwaway endpoints, and leave `action_mode` at `manual_only` unless you are deliberately demonstrating the automatic path on a disposable host. In `baseline` mode the endpoint that triggers those actions needs no credential at all.

## Verify

```bash
./verify.sh
```

Checks container state and each published port, and reports which mode is deployed by testing whether the remediation endpoint answers without a credential — the single clearest behavioural difference between the two modes.

## Reset between sessions

```bash
./reset.sh            # clear DB + certs, keep the clone
./reset.sh --full     # also remove the clone and the Ollama model volume
```

`reset.sh` runs the product's own `clear-db.sh` and `delete-certs.sh`, drops the containers, and re-runs `gen-certs.sh`. `--full` additionally removes the `ollama_models` volume, which means the next deploy re-downloads ~9 GB — only do that if you need the disk.

## Generating detection evidence

The product ships eleven attack-simulation scripts that inject synthetic log entries into the host's own logging system. Nothing leaves the host and no real malware is created.

```bash
cd $RANGE_INSTALL_DIR
sudo ./test_quick_attacks.sh              # 18 events, 4 vectors, one source IP
sudo ./test_macos_process_threats.sh      # exercises KILL_PROCESS
sudo ./test_macos_malware_detection.sh    # exercises DELETE_FILE
```

Windows equivalents are `test_rdp_enhanced.ps1`, `test_windows_malware.ps1` and `test_windows_network_intrusion.ps1`, run as Administrator. Expect a **~60 second floor** before anything appears: alert polling is 30 s and the poller deliberately reads 30 s into the past to let Wazuh catch up.

---

## What CyberFort needs from this VM

Almost nothing, which is worth knowing when planning the range. The pilot's evidence comes from the three **source-side** scanners — Code Analysis, Dependency Check and SBOM Generator — which take a ZIP upload or a GitHub URL and never touch the running stack. The hosted CyberFort instance cannot reach a private range subnet anyway.

So the target VM is needed for two things only: demonstrating that the product *works* (detection and remediation, which is the evidence for Annex I `3j` and `3f`), and demonstrating the access-control finding live in `baseline` mode. Everything else in the runbook can be done from the source archive alone.

```bash
cd $RANGE_INSTALL_DIR
zip -r /tmp/seuxdr-src.zip . -x '*.git*' -x 'manager/manager' -x '*/node_modules/*'
```
