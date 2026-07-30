# Scenario 04 — CRA conformity mapping

The bridge between the **as-built security posture of Clone Systems' SEUXDR** and the **CRA framework as it is actually represented in CyberFort**.

Scenarios 01–03 map *seeded vulnerabilities* in a teaching target to framework controls. This scenario is different in kind: SEUXDR is a real product, so the mapping runs in **both directions** — the conformity evidence the manufacturer can legitimately claim, and the non-conformities that block a Declaration of Conformity. A real conformity assessment is not a bug list; it is a defensible position on every essential requirement, including the ones you pass.

**The question texts quoted below are verbatim from the platform's CRA conformity seed** (52 product-level questions, read from the live `CRA Extended` tenant on 2026-07-29). Every product claim is anchored to a file path in `t4.4_siem_ai_remediation` @ `00a95ad`.

---

## How the CRA framework is structured in CyberFort

CyberFort ships the Cyber Resilience Act as a built-in framework with two assessment types (**Conformity** and **Audit**) and an objective tree of Chapters → Articles → Annex I objectives → Vulnerability Handling objectives. Scoped to a single asset, the tree holds **30 objectives across 6 chapters**:

| Chapter | Objectives | Content |
|---------|-----------|---------|
| Chapter I — General Provisions | 2 | Art. 1–2 (scope), Art. 6 + Annex I (essential requirements) |
| Chapter II — Obligations of Economic Operators | 4 | Art. 13 (manufacturers), Art. 14 (reporting), Art. 25 (internal processes), Art. 26 (guidance) |
| Chapter III — Conformity of the Products | 1 | conformity assessment procedure |
| Chapter V — Market Surveillance | 2 | Art. 52 + 54, Art. 70 |
| **ANNEX I** | **13** | objectives `1`, `2`, `3a`–`3k`, grouped into seven subchapters |
| **Vulnerability Handling** | **8** | objectives `1`–`8`, grouped into three subchapters |

The Annex I subchapters are *Secure Product Design and Development* (`1`, `2`), *Secure Configuration Management* (`3a`), *Access Control and Authentication* (`3b`), *Data Protection* (`3c`, `3d`, `3e`), *Availability and Resilience* (`3f`, `3g`), *Attack Surface and Incident Mitigation* (`3h`, `3i`), *Security Logging* (`3j`) and *Security Update Management* (`3k`). Vulnerability Handling splits into *Vulnerability Identification and Testing* (`1`–`3`), *Vulnerability Disclosure* (`4`–`6`) and *Security Update Distribution* (`7`–`8`).

Each objective carries pre-seeded **Objective Utilities** (the policy documents that would satisfy it), the **Policies** actually linked in the tenant with their approval state, an **Evidence** upload action, and a **Compliance Status** selector. The Conformity assessment sits alongside as a **52-question** natural-language questionnaire. The engineer answers the questionnaire; the objective tree is where the position is recorded and evidenced.

![CRA objective tree for SEUXDR — 30 objectives across 6 chapters](screenshots/step8-01-objectives-cra-seuxdr.png)

Two platform-specific notes that matter for reading the tables below:

* Questions **36** and **37** correspond to the secure-data-removal and secure-transfer limbs of Annex I. The platform's objective tree stops at `3k` and folds both into the *Data Protection* subchapter, so they are mapped here to `3e` and `3c` respectively.
* The engineer never sees "Annex I objective 3b" next to question 20 — only the natural-language text. The mapping in this document is what lets the assessor verify the right questions were answered against the right evidence.

---

## Product classification

SEUXDR is an **Annex III important product with digital elements, Class I**, selectable in CyberFort under *Criticality* as the verbatim option **"Security information and event management (SIEM) systems"**.

![Registering SEUXDR with its CRA classification](screenshots/step1-03-add-asset-modal-filled.png)

The classification is over-determined — three independent Annex III Class I limbs apply:

| Limb | Evidence |
|------|----------|
| **SIEM system** | Bundles Wazuh 4.11 SIEM inside its own image (`Dockerfile:53`, `startup.sh:19`); centralised multi-tenant event collection, storage and query (`manager/api/websocketservice/logstore.go:30-91`, `manager/routes/routes.go:68`); MITRE ATT&CK enrichment and STIX 2.1 export (`manager/handlers/stix_handler.go:11-52`); ships branded `SECUR-EU SIEM` (`manager_front/index.html:7`) |
| **Intrusion detection and prevention system** | Self-declared HIDS (`readme.md:3`, `CLAUDE.md:7`); prevention is implemented, not just detection — `BLOCK_IP` installs firewall DROP rules (`agent/active-response/firewall-drop.sh:142-143`) |
| **Software that searches for, removes or quarantines malicious software** | Malware-triggered `DELETE_FILE` on endpoints (`agent/active-response/delete-file.sh:32`, dispatch `agent/monitoring/monitoring.go:475`) |

Three aggravating characteristics support arguing **Class II**, or at minimum documenting why Class I was chosen: the agent is a fleet-wide privileged remote-execution capability (`agent/monitoring/monitoring.go:446-484`); the manager **operates a real X.509 certificate authority** (RSA-4096, `IsCA: true`, `KeyUsageCertSign|CRLSign` — `manager/mtls/mtls.go:601-615`); and it generates and distributes agent installers with embedded private keys through an unauthenticated download endpoint (`manager/routes/routes.go:69-70`).

> The practical consequence is the single most important output of the scope step: **an Annex III product cannot self-assess against Module A alone.** Article 32(2) requires a notified-body route (or full application of harmonised standards where available), and Annex I Part II vulnerability handling applies in full.

---

## Part A — Conformity evidence, one card per claim

These are the positions Clone Systems can defend from code. They are the reason the pilot is worth running: a manufacturer who only files bugs has an incident report, not a conformity assessment.

### Claim 1 — Modern authenticated encryption throughout, no legacy crypto anywhere

**Where:** `agent/comms/utils.go:93-99,124-129` · `manager/api/agentauthenticationservice/authentication_service.go:222-240` · `agent/storage/storage.go:36-40,70-75` · `manager/utils/dbutils.go:152-157` · key wrapping `agent/encryptionservice/encryptionservice.go:91,100`.

**Substance:** AES-**GCM** with a random per-message nonce for every encrypted payload; RSA-**OAEP-SHA256** for key wrapping, not PKCS#1 v1.5. A repository-wide review found **no ECB, no unauthenticated CBC and no static IV**. Per-agent key isolation means compromise of one agent's key does not expose another's traffic (`manager/database/migrations/000001_init_mg.up.sql:66`).

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3c** *(confidentiality through encryption)* | Q24 — "Do you use state-of-the-art mechanisms for encrypting relevant data at rest or in transit?" |
| **3d** *(integrity of data, commands, programs, configuration)* | Q25 — "Do you protect the integrity of stored, transmitted or otherwise processed data, commands, programs and configuration?" |

### Claim 2 — TLS 1.2 floor enforced in every server and client, with no agent-side bypass

**Where:** `manager/main.go:181-182,212-213` · `manager/mtls/mtls.go:244-245` · `agent/comms/tlsconfig.go:63-64,141-142` · `manager_front/nginx.conf:8`.

**Substance:** No downgrade path exists. The agent additionally **fails closed** if the CA PEM will not append (`agent/comms/tlsconfig.go:56-57`) and **validates CA and client certificate expiry before use** (`:111-113,136-138`). `InsecureSkipVerify` appears four times, all on manager→loopback backend calls (OpenSearch `:9200`, Wazuh API `:55000`) and never on an agent path.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3c** *(confidentiality)* | Q23 — "Do you protect the confidentiality of stored, transmitted or otherwise processed data through encryption?" |
| **3h** *(limit attack surfaces, external interfaces)* | Q32 — "Are your products designed, developed and produced to limit attack surfaces, including external interfaces?" |

### Claim 3 — Two-factor agent enrolment over mTLS on a dedicated, minimal listener

**Where:** `manager/main.go:176-183` (`tls.RequireAndVerifyClientCert`, CA pool `:154-162`) · `manager/api/registrationservice/registration_service.go:78,86,88-92` · rate limiter `manager/middlewares/ratelimiter.go:14-16,32` · key generation `manager/helpers/helpers.go:467-478`.

**Substance:** Enrolment requires a valid X.509 client certificate **at the transport** *and* an organisation API key plus group licence key **in the payload**, cross-validated for org/group consistency. API keys are 256-bit from `crypto/rand`. The listener on `:8081` exposes exactly two routes, architecturally separated from the operational API on `:8443` — genuine port separation by trust level.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3b** *(protection from unauthorised access)* | Q20 — "Do you ensure protection from unauthorized access by appropriate control mechanisms?" *(supports the enrolment limb only — see Non-conformity 1)* |
| **3h** *(limit attack surfaces)* | Q32 — "Are your products designed, developed and produced to limit attack surfaces, including external interfaces?" |

### Claim 4 — Availability and resilience: failed-alert queue, dead-letter queue, resume-after-restart

**Where:** schema `manager/database/migrations/000005_failed_alert_queue.up.sql:3-104` · `manager/api/failedAlertManager/failed_alert_manager.go:133-139` · state resume `manager/api/activeresponseservice/active_response_service.go:560-612` · keepalive `manager/handlers/handlers.go:18-27` · reaper `manager/api/connectionmanager/connection_manager.go:473-504`.

**Substance:** Alerts that fail processing retry with exponential backoff and, after three attempts, move to a dead-letter queue for analyst review rather than being silently lost. A manager restart resumes from the last completed timestamp instead of losing or re-processing the alert window. Bounded channels prevent unbounded memory growth; stale WebSocket connections are reaped on a 54 s ping / 60 s pong-wait cycle with a 512 KB read limit. This is the best-engineered subsystem in the product.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3f** *(availability of essential functions, DoS resilience)* | Q29 — "Do you protect the availability of essential and basic functions, also after an incident?" &middot; Q30 — "Do you implement resilience and mitigation measures against denial-of-service attacks?" |

### Claim 5 — Security-event recording, including a full AI decision narrative

**Where:** `manager/logging/logging.go:31-52` · correlation IDs `manager/middlewares/logger.go:24-49` · `manager/database/migrations/000004_soc_analyst_storage.up.sql:2-22` · written `manager/api/socanalystservice/soc_analyst_service.go:244-256` · command lifecycle `000003_active_response_persistence.up.sql:2-19`.

**Substance:** Structured JSON logging with a per-request UUID echoed as `X-Request-Id`, separated by trust domain into `server.log`, `registrations.log` and `mtls.log`. Every AI analysis persists its `reasoning`, `extracted_evidence`, `severity_factors`, `mitre_tactics` and the complete `react_history` iteration log — **explainability that is better than typical for this product class**. Every remediation command persists status, stdout/stderr, message and `executed_at`.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3j** *(security-relevant information recording)* | Q34 — "Do you provide security-related information by recording and monitoring relevant internal activity?" |
| **3j** *(monitoring access/modification)* | Q35 — "Do you monitor access to or modification of data, services or functions with an opt-out mechanism for users?" *(monitoring limb only; the opt-out is not evidenced)* |

### Claim 6 — Structural blast-radius limitation: remediation is strictly per-agent

**Where:** `manager/api/messageprocessor/message_processor.go:430` · dispatch gating `:441-449` · `manager/handlers/agent_actions.go:417-420` · `NOT_FOUND` sentinel `:1190` · duplicate suppression `manager/api/socanalystservice/react_service.go:389-394`.

**Substance:** Each alert resolves to exactly one agent, and **no fleet-wide or group-wide action primitive exists anywhere in the codebase**. A single bad AI decision cannot cascade across the estate. This limit is structural rather than configurational, which makes it a much stronger claim than a policy setting. Actions dispatch only to agents with a live verified connection, and an unresolvable target diverts to manual review instead of guessing.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3g** *(minimise negative impact on other devices/networks)* | Q31 — "Do you minimize the negative impact by your products on the availability of services provided by other devices or networks?" |
| **3i** *(reduce impact of an incident)* | Q33 — "Are your products designed to reduce the impact of an incident using appropriate exploitation mitigation mechanisms?" |

### Claim 7 — Secure-by-default AI safety posture and fail-fast configuration validation

**Where:** `manager/manager.yaml:49` (`action_mode: "manual_only"`) enforced at `manager/api/messageprocessor/message_processor.go:1176,1191` · config validation `manager/config/config.go:252-288`.

**Substance:** On the as-shipped configuration **no AI-initiated destructive action reaches an endpoint without a human step**; analyses land as `manual_action_required`. Configuration is validated at load with fail-fast semantics, rejecting out-of-range rule levels, non-positive batch sizes, negative cooldowns and any illegal `action_mode`. This is the right default for an autonomous-remediation product and should be presented as a deliberate design choice.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3a** *(secure by default configuration)* | Q14 — "Are your products made available on the market with a secure by default configuration?" |

> ⚠ **The claim has three documented limits** and must be answered *Partially*, not *Yes*: the operator endpoint never reads `ACTION_MODE` (Non-conformity 1); `retryCommandsForAgent` does not read it either (`message_processor.go:1377-1440`); and `manager/config/config.go:384-386` **defaults to `"automatic"` when the key is unset**, which the shipped `manager/test.yaml:39-44` profile does. A secure default that fails open when absent is a partial control.

### Claim 8 — Local-only AI inference: customer telemetry never leaves the deployment

**Where:** `manager/manager.yaml:71-74` · `manager/api/socanalystservice/llm_service.go:142` · `CyberGuard_Stripped_Documentation.md:39`.

**Substance:** The LLM runs in-network via Ollama (`phi4:14b`). Endpoint log content — which routinely contains usernames, hostnames, IPs, file paths and command lines — is **never sent to a third-party cloud model**. For an EU-market security product this is a demonstrable data-protection property and a commercial differentiator.

| Annex I objective | Conformity question the engineer answers |
|-------------------|------------------------------------------|
| **3c** *(confidentiality)* | Q23 — "Do you protect the confidentiality of stored, transmitted or otherwise processed data through encryption?" |
| **3e** *(data minimisation)* | Q28 — "Do you process only data that is adequate, relevant and limited to what is necessary for the intended purpose?" *(no third-party disclosure limb only — see Non-conformity 5)* |

### Claim 9 — Agent update integrity: SHA-256 verification with automatic rollback

**Where:** checksum computed `manager/api/configurationservice/configuration_service.go:916-917` → served `manager/handlers/agent_actions.go:271` → verified `agent/agentd/update.go:224-250` · rollback `agent/main.go:288-293,304-309,349-352` · semver floor `manager/api/updateservice.go/update_service.go:115-145`.

**Substance:** Downloaded agent binaries are SHA-256 verified before installation. The updater backs up the current binary, restores SELinux `bin_t` context on Linux, and **rolls back on either replace failure or restart failure** — a real integrity-preservation control. Staged-rollout and version-deactivation controls exist in the schema. Client certificates are short-lived (1 month, 7-day refresh) with automated re-signing (`manager/mtls/mtls.go:886-894`).

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 3k** *(vulnerabilities addressable through updates)* | Q16 — "Do you ensure that vulnerabilities can be addressed through security updates?" |
| **Vuln-Handling 7** *(secure update distribution)* | Q47 — "Do you provide mechanisms to securely distribute updates for your products with digital elements?" |

> ⚠ Answer both *Partially*. Integrity verification **fails open** — `agent/agentd/update.go:225-228` installs the binary when the expected checksum is empty, and the field is commented out in two of three manager response paths. Nothing is **signed**: no GPG, Authenticode, notarisation or Sigstore anywhere. A hash delivered over the same channel as the binary defends against corruption, not against a compromised manager. And the manager itself has **no update mechanism at all**.

---

## Part B — Non-conformities, one card per finding

### Non-conformity 1 — Unauthenticated remote file deletion, process termination and network blocking across the agent fleet

**Where:** route registered with no auth middleware — `manager/routes/routes.go:86` (the `/api` group applies only `CustomLogger`, `:64-65`); handler `manager/handlers/agent_actions.go:357-491` validates the action verb at `:385-388` and nothing else, dispatching at `:454`; endpoint executes `rm -f "${FILEPATH}"` as root (`agent/active-response/delete-file.sh:32`).

**Detected by:** **Semgrep** (missing-authentication patterns) + manual route review + the product's own **Postman collection**, which declares `auth: None` on all 31 requests.

**Substance:** Any party with TCP reach to port 8443 can delete any file, kill any process or firewall-block any IP on any connected agent — unauthenticated, unrate-limited (the limiter covers only `/api/register`) and **unattributed**, because no operator identity is recorded (`:424-435`). It bypasses `action_mode: manual_only` entirely, since the handler never reads `ACTION_MODE`. This is a shipped, remotely exploitable vulnerability, which is what makes Q13 answerable only as *No*.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 3b** *(protection from unauthorised access)* | Q20 — "Do you ensure protection from unauthorized access by appropriate control mechanisms?" |
| **Annex I 2** *(no known exploitable vulnerabilities)* | Q13 — "Are your products with digital elements delivered without any known exploitable vulnerabilities?" |
| **Annex I 3d** *(protection against unauthorised modification)* | Q26 — "Do you protect against manipulation or modification not authorized by the user?" |

### Non-conformity 2 — No user authentication, authorisation or accountability anywhere in the product

**Where:** `manager/middlewares/middleware.go` is 13 lines and defines no auth function; no login route in `manager/routes/routes.go`; no `users` / `roles` / `sessions` tables in any of the five migrations. JWT code exists but is dead (`manager/config/auth_config.go:102-153`, zero call sites); the password validator is dead (`manager/validators/validators.go`, zero importers).

**Detected by:** **Semgrep** + migration review + `grep` for call sites.

**Substance:** All 22 TLS routes are open, including `POST /api/create/org`, `POST /api/create/agent`, `GET /api/download/agent` (which hands out installers containing embedded private keys) and `POST /api/view/alerts` (full endpoint log content). This was removed deliberately on 2025-10-29 and is documented as such; `CLAUDE.md:18-19,45` still claims RBAC and JWT are present, so the documentation contradicts the artefact.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 3b** *(authentication, identity, access management)* | Q21 — "Do you implement authentication, identity or access management systems?" |
| **Annex I 3b** *(reporting unauthorised access)* | Q22 — "Do you report on possible unauthorized access?" |
| **Chapter II, Art. 25** *(internal processes)* | Q10 — "Do you systematically document relevant cybersecurity aspects concerning your products with digital elements?" |

### Non-conformity 3 — Unvalidated LLM output becomes a root-privileged destructive command argument

**Where:** the unbroken chain is model output → `manager/api/socanalystservice/react_service.go:318-320` → `ActionDecision.Target` `:397-402` → DB `soc_analyst_service.go:217-226` → `message_processor.go:1257-1266` → encrypted WebSocket frame `connection_manager.go:301-310` → `agent/monitoring/loglisten.go:479` → `ExecuteAction` `agent/monitoring/monitoring.go:446` → `executeEmbeddedScript(..., actionMsg.Target)` → `rm -f` / `pkill -x` / `pfctl`.

**Detected by:** manual data-flow review. **The only validation of the target is non-emptiness** — `react_service.go:99-101` and `agent/monitoring/monitoring.go:463-467`.

**Substance:** No IP validation for `BLOCK_IP`, no path canonicalisation or protected-path denylist for `DELETE_FILE`, no PID or protected-process list for `KILL_PROCESS`, no length limit, no newline stripping. **Prompt injection is unmitigated**: attacker-controlled log text is interpolated raw into the prompt via `text/template` (`prompt_service.go:206`), so anyone who can write a log line — a crafted User-Agent, filename or SSH username — can influence which host action runs. Up to three distinct actions may be emitted per alert. The documented agent-side whitelist, dangerous-pattern blocklist and execution timeout (`agent/helpers/helpers.go:523-583,467-472`) protect a **different, dead code path** and never run on the live one, which has no timeout at all.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 1** *(appropriate level of cybersecurity based on risks)* | Q12 — "Are your products with digital elements designed, developed and produced to ensure an appropriate level of cybersecurity based on the risks?" |
| **Annex I 3d** *(integrity of commands and programs)* | Q25 &middot; Q26 |
| **Annex I 3i** *(reduce impact of an incident)* | Q33 — "Are your products designed to reduce the impact of an incident using appropriate exploitation mitigation mechanisms?" |

### Non-conformity 4 — The entire Annex I Part II apparatus is absent

**Where:** no `SECURITY.md`; `readme.md:394` contains the literal empty placeholder `contact [] or open an issue`; `CyberGuard_Stripped_Documentation.md:893` points at `github.com/SecureEU/seuxdr/issues`, a **different repository** from the actual remote. No CycloneDX or SPDX artefact. No `.github/`, `.gitlab-ci.yml` or any CI configuration. No `govulncheck`, `trivy`, `grype`, `osv-scanner`, `npm audit` or Dependabot. No `CHANGELOG.md`. **No git tags at all** — eight unstructured commits on `main`.

**Detected by:** **OSV Dependency Check** (surfaces the unscanned dependency tree) + **SBOM Generator** (produces the missing artefact) + repository review.

**Substance:** The closest thing to a component inventory is `licenses/credits.txt`, a hand-maintained 26-entry list that still contains the template placeholder `<Include your full license text here>`, declares MIT while `readme.md:390` points at Apache-2.0, and omits nearly all ~100 indirect Go modules and **all** front-end dependencies. Six of eight Vulnerability Handling objectives have no supporting artefact whatsoever.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Vuln-Handling 1** *(component inventory, SBOM)* | Q38 — "Do you identify and document vulnerabilities and components contained in your products with digital elements?" &middot; Q39 — "Do you draw up a software bill of materials in a commonly used and machine-readable format?" &middot; Q40 — "Does your software bill of materials cover at least the top-level dependencies of the products?" |
| **Vuln-Handling 3** *(regular tests and reviews)* | Q41 — "Do you apply effective and regular tests and reviews of the security of your products with digital elements?" |
| **Vuln-Handling 4** *(public disclosure of fixed vulnerabilities)* | Q42 &middot; Q43 |
| **Vuln-Handling 5** *(coordinated vulnerability disclosure policy)* | Q44 — "Do you have a policy on coordinated vulnerability disclosure in place and enforced?" |
| **Vuln-Handling 6** *(contact address)* | Q45 &middot; Q46 — "Do you provide a contact address for reporting vulnerabilities discovered in your products?" |
| **Vuln-Handling 2 / 8** *(timely remediation, dissemination)* | Q48 &middot; Q50 &middot; Q52 |

### Non-conformity 5 — No data minimisation over endpoint log content

**Where:** raw log lines persisted verbatim to `soc_analyst_analyses.full_log` (`000004_soc_analyst_storage.up.sql:11`); written to **world-readable** queue files at mode `0644` (`manager/api/websocketservice/logstore.go:36,72`); interpolated into LLM prompts (`prompt_service.go:206`).

**Detected by:** **Semgrep** (permissive file modes) + schema review.

**Substance:** This content routinely contains usernames, hostnames, source IPs, file paths and command lines — personal data under GDPR. There is no pseudonymisation, no field redaction, and **no retention policy at all** on `soc_analyst_analyses` or `active_response_commands`; both grow without bound. Queue-file rotation exists (3 most recent daily files per agent, `manager/crons/log_cleanup.go:89-106`) and is the one genuine minimisation control.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 3e** *(data minimisation)* | Q28 — "Do you process only data that is adequate, relevant and limited to what is necessary for the intended purpose?" |
| **Annex I 3c** *(confidentiality of stored data)* | Q23 — "Do you protect the confidentiality of stored, transmitted or otherwise processed data through encryption?" |

### Non-conformity 6 — Secrets exposure: committed credential, plaintext KEK, world-readable keys

**Where:** live Wazuh/OpenSearch admin credential `admin` / `S1lMfWxh1HB6SbKg.9fmkoq.P5W+07M5` committed in three tracked files (`main.go:176-177`, `stix_service_integration_test.go:167-168`, `opensearch_service_integration_test.go:256-257`) · group KEK RSA private key stored **unwrapped** in the unencrypted SQLite DB (`configuration_service.go:130,134,142` → `groups.key_encryption_key`) · private keys written `0644` via `os.Create` (`manager/helpers/helpers.go:314-337,137-152`; `keys.json` explicitly `0644` at `configuration_service.go:957,1016`) · storage and cert directories created `0777` (`manager/main.go:36,53`) · **enrolment API key and licence key logged in cleartext** (`manager/handlers/agent_actions.go:62`).

**Detected by:** **Semgrep** `hardcoded-password` / permissive-permissions rules.

**Substance:** Because the KEK sits unwrapped beside the `agents.encryption_key` values it protects, the per-agent key wrapping provides **no protection against file-level database theft**. The `0777` directories and `0644` key files mean any local user on the manager host can read the PKI.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 3a** *(secure by default)* | Q14 — "Are your products made available on the market with a secure by default configuration?" |
| **Annex I 3c** *(confidentiality of stored data)* | Q23 &middot; Q24 |
| **Annex I 2** *(no known exploitable vulnerabilities)* | Q13 |

### Non-conformity 7 — Outdated and unpinned dependencies, unpinned base images

**Where:** `go.mod:5-35` — `golang-migrate v3.5.4+incompatible` (2018; upstream is v4), **`gorilla/websocket v1.4.2`** (2020 — this carries the remediation command channel), `patrickmn/go-cache v2.1.0+incompatible` (2019), `kardianos/service` and `tkanos/gonfig` pinned to 2021 commits with no tagged release, `golang/mock` and `pkg/errors` archived upstream. `manager_front/package.json:13,17,18` ships **three faker libraries in production dependencies**, including the sabotaged `faker@6.6.6`. `Dockerfile:1` uses `redhat/ubi9` with **no tag at all**; `docker-compose.yml:36` uses `ollama/ollama:latest`. **Not one image is digest-pinned.** `manager_front/Dockerfile:11` runs `npm install --frozen-lockfile` — a Yarn flag that is a no-op for npm, so the lockfile is not enforced.

**Detected by:** **OSV Dependency Check** on `go.mod` and `package-lock.json` + **SBOM Generator** (Syft) on the container images.

**Substance:** Compounded by Non-conformity 4 — with no dependency scanning in the repository, the manufacturer has no mechanism to learn that any of these carry advisories. The Wazuh installer and Go toolchain are also fetched and executed **without checksum or signature verification** (`Dockerfile:13-22,53`).

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 2** *(no known exploitable vulnerabilities)* | Q13 |
| **Vuln-Handling 1** *(identify and document components)* | Q38 &middot; Q39 &middot; Q40 |
| **Vuln-Handling 2** *(remediate without delay)* | Q48 — "Do you ensure vulnerabilities are fixed or mitigated in a timely manner through updates?" |

### Non-conformity 8 — Safety controls that are configured, validated, documented and never enforced

**Where:** each verified to have no enforcement site — `min_rule_level` (`manager.yaml:30`, used only to build a prompt string at `message_processor.go:415`), `max_alerts_batch` (`:31`, query hard-codes `"size": 10000` at `opensearch_service.go:110`), `cooldown_period` (`:32`, no timestamp comparison or dedup key anywhere), `command_timeout` (`:33`, hard-coded 30 at `message_processor.go:1214`), `confidence_thresholds` (`:55-67`, **not in the config struct at all** — zero non-test hits for `confidence`), `analysis_timeout` (`:51`, overridden by a hard-coded 60 s at `:1065`), `llm.temperature` / `max_tokens` (`:77-78`, silently ignored for Ollama), `fallback_to_rules` (`:53`, plumbed and never read).

**Detected by:** manual configuration-to-code tracing.

**Substance:** The net effect is that **every alert of any severity that resolves to a connected agent is sent to the LLM and may yield up to three host actions, with no cooldown, no batch cap and no confidence gate.** For a regulatory submission this is the most dangerous class of finding, because it invites an assessor to accept assurance the artefact does not provide — and it undermines the credibility of the eight genuine claims in Part A.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Annex I 1** *(appropriate cybersecurity based on risks)* | Q12 |
| **Annex I 3a** *(secure by default)* | Q14 |
| **Chapter II, Art. 13** *(technical documentation accuracy)* | Q8 &middot; Q10 |

### Non-conformity 9 — No risk assessment, no support-period declaration, no technical documentation

**Where:** no threat model, no attack-surface analysis, no data-flow diagram, no risk-assessment artefact anywhere in the repository. No `CHANGELOG.md`, no support-lifecycle or EOL statement, no declared support period. `agent_versions.release_notes` is seeded with the placeholder `'Bug fixes and improvements'` (`000001_init_mg.up.sql:57`).

**Detected by:** repository review against the CRA Technical File page checklists.

**Substance:** CRA Article 13 requires the cybersecurity risk assessment to be **drawn up, documented, kept updated during the support period, and included in the technical documentation** placed on the market. None of the nine questions in that block (Q1–Q9) has a supporting artefact. The CRA also requires a support period of **at least five years**; SEUXDR declares none. This is the block the pilot most directly fixes — the CyberFort risk register, objective tree and technical-file pages *are* the missing documentation, which is why the pilot's output is itself Annex V evidence.

| Objective | Conformity question the engineer answers |
|-----------|------------------------------------------|
| **Chapter II, Art. 13** *(manufacturer obligations)* | Q1 – Q9 (all nine risk-assessment questions) |
| **Annex I 3k** *(security updates)* | Q17 &middot; Q18 &middot; Q19 |
| **Vuln-Handling 8** *(advisory messages with updates)* | Q52 — "Do you accompany security updates with advisory messages providing users with relevant information?" |

---

## Annex I and Vulnerability Handling coverage matrix

Every one of the 30 objectives in the SEUXDR scope is addressed by this pilot — that is the point of a conformity assessment as opposed to a penetration test. The matrix records the **baseline position** established on 2026-07-29.

<style>
table.cov { width: 100%; border-collapse: collapse; margin: 10px 0; }
table.cov th, table.cov td { border: 1px solid #c9c9c9; padding: 5px 8px; text-align: left; vertical-align: top; font-size: 9.5pt; }
table.cov th { background: #1a3260; color: #fff; }
table.cov td.yes { background: #e1f3df; color: #1b5e20; font-weight: 600; text-align: center; width: 90px; }
table.cov td.partial { background: #fdf6c8; color: #6b5400; font-weight: 600; text-align: center; }
table.cov td.no { background: #fbe3e3; color: #8a2020; font-weight: 600; text-align: center; }
table.cov tr td:first-child { width: 80px; font-weight: 600; color: #1a3260; text-align: center; }
</style>

<table class="cov">
<thead><tr><th>Objective</th><th>Title (paraphrased)</th><th>Baseline</th><th>Evidence / reason</th></tr></thead>
<tbody>
<tr><td>1</td><td>Appropriate level of cybersecurity based on the risks</td><td class="no">No</td><td>Non-conformities 1, 3, 8 &mdash; unauthenticated destructive endpoint and unvalidated LLM output</td></tr>
<tr><td>2</td><td>Delivered without known exploitable vulnerabilities</td><td class="no">No</td><td>Non-conformity 1 is remotely exploitable as shipped; dependency tree unscanned (7)</td></tr>
<tr><td>3a</td><td>Secure by default configuration, resettable</td><td class="partial">Partially</td><td>Claim 7 (<code>manual_only</code>, fail-fast config) vs. fail-open default, <code>0777</code> dirs, privileged container</td></tr>
<tr><td>3b</td><td>Protection from unauthorised access</td><td class="no">No</td><td>Claim 3 covers agent enrolment only; Non-conformities 1 and 2 defeat the operational API</td></tr>
<tr><td>3c</td><td>Confidentiality through encryption</td><td class="partial">Partially</td><td>Claims 1, 2, 8 in transit; unencrypted SQLite, plaintext KEK, <code>0644</code> logs at rest (5, 6)</td></tr>
<tr><td>3d</td><td>Integrity of data, commands, programs, configuration</td><td class="partial">Partially</td><td>Claim 1 AEAD gives transit integrity; commands unsigned, no replay protection (Non-conformity 3)</td></tr>
<tr><td>3e</td><td>Data minimisation</td><td class="no">No</td><td>Non-conformity 5 &mdash; raw log content persisted verbatim, no redaction, no retention on AI tables</td></tr>
<tr><td>3f</td><td>Availability of essential functions, DoS resilience</td><td class="yes">Yes</td><td>Claim 4 &mdash; failed-alert queue, DLQ, resume-after-restart, keepalive reaper</td></tr>
<tr><td>3g</td><td>Minimise negative impact on other devices/networks</td><td class="partial">Partially</td><td>Claim 6 per-agent scoping; but <code>BLOCK_IP</code> has no TTL and no reachable <code>UNBLOCK_IP</code></td></tr>
<tr><td>3h</td><td>Limit attack surfaces, external interfaces</td><td class="partial">Partially</td><td>Claims 2, 3 port separation; undermined by privileged container and published Ollama port</td></tr>
<tr><td>3i</td><td>Reduce impact of an incident (exploit mitigation)</td><td class="partial">Partially</td><td>Claim 6 + update rollback; no sandboxing, temp-file TOCTOU, no protected-path denylist</td></tr>
<tr><td>3j</td><td>Security-relevant information recording</td><td class="yes">Yes</td><td>Claim 5 &mdash; structured logging, correlation IDs, full AI reasoning trail, STIX export</td></tr>
<tr><td>3k</td><td>Vulnerabilities addressable through security updates</td><td class="partial">Partially</td><td>Claim 9 agent channel with rollback; manager has no update mechanism, verification fails open</td></tr>
<tr><td>VH-1</td><td>Identify and document components (SBOM)</td><td class="no">No</td><td>Non-conformity 4 &mdash; no SBOM; <code>credits.txt</code> incomplete and self-contradictory</td></tr>
<tr><td>VH-2</td><td>Address and remediate vulnerabilities without delay</td><td class="no">No</td><td>Non-conformity 4 &mdash; no CI, no scanning, no tags, no changelog, no SLA</td></tr>
<tr><td>VH-3</td><td>Effective and regular security tests and reviews</td><td class="no">No</td><td>Non-conformity 4 &mdash; no automated test run, no pen-test records. This pilot is the first review</td></tr>
<tr><td>VH-4</td><td>Public disclosure of fixed vulnerabilities</td><td class="no">No</td><td>Non-conformity 4 &mdash; no advisory channel</td></tr>
<tr><td>VH-5</td><td>Coordinated vulnerability disclosure policy</td><td class="no">No</td><td>Non-conformity 4 &mdash; no <code>SECURITY.md</code></td></tr>
<tr><td>VH-6</td><td>Facilitate vulnerability sharing, contact address</td><td class="no">No</td><td>Non-conformity 4 &mdash; <code>readme.md:394</code> has an empty placeholder; docs cite the wrong repository</td></tr>
<tr><td>VH-7</td><td>Secure update distribution mechanisms</td><td class="partial">Partially</td><td>Claim 9 &mdash; SHA-256 over TLS with rollback, but fails open and nothing is signed</td></tr>
<tr><td>VH-8</td><td>Updates disseminated without delay, free, with advisories</td><td class="no">No</td><td>Non-conformity 9 &mdash; no release process; <code>release_notes</code> is a placeholder</td></tr>
<tr><td>Ch. I</td><td>Scope and essential requirements (2 objectives)</td><td class="partial">Partially</td><td>Scope determined and classification justified by this pilot; essential requirements not met</td></tr>
<tr><td>Ch. II</td><td>Economic-operator obligations (4 objectives)</td><td class="no">No</td><td>Non-conformity 9 &mdash; no risk assessment, no technical documentation, no Art. 14 reporting procedure</td></tr>
<tr><td>Ch. III</td><td>Conformity of the product (1 objective)</td><td class="no">No</td><td>Annex III Class I requires a notified-body route; none engaged</td></tr>
<tr><td>Ch. V</td><td>Market surveillance (2 objectives)</td><td class="no">No</td><td>No internal audit procedure or corrective-action process linked to the product</td></tr>
</tbody>
</table>

**Coverage summary:** 2 objectives **Yes**, 10 **Partially**, 18 **No** — 2 Yes and 7 Partially across the 13 Annex I objectives, 1 Partially across the 8 Vulnerability Handling objectives, and Chapter I's 2 objectives Partially. Across the 52 conformity questions the baseline is **2 Yes / 19 Partially / 31 No**. Every one of the 30 objectives is evidenced either way, so the assessment is complete even though the product is not conformant.

> ℹ️ The **7%** figure is what the platform's EU Declaration of Conformity page displays at baseline. It aggregates across every product registered in the tenant (270 CRA objectives, 30 compliant, 1 assessment, 0 completed) and weights 60% objective compliance against 40% assessment completion. Scoped to SEUXDR alone the position is **2 of 30 objectives compliant with the conformity assessment unstarted** — report both numbers, because the aggregated one is the one on screen.

**A complete assessment showing a low score is a regulatory asset; an incomplete assessment showing nothing is a liability.**

---

## The 52 conformity questions — recommended baseline answers

This is the working sheet. Question numbers match the position in the CyberFort UI (paginated 10 per page). Answers are the defensible baseline for the as-built stripped variant; the *Evidence to attach* column names the artefact the engineer uploads.

| # | Question (verbatim from CyberFort) | Answer | Objective | Evidence to attach |
|---|-------------------------------------|--------|-----------|--------------------|
| 1 | Have you undertaken an assessment of the cybersecurity risks associated with your product with digital elements? | No | Ch. II Art. 13 | The pilot risk register itself is the first one |
| 2 | Do you take the outcome of the cybersecurity risk assessment into account during the planning, design, development, production, delivery and maintenance phases? | No | Ch. II Art. 13 | No SDLC gate evidenced; no CI |
| 3 | Is your cybersecurity risk assessment documented and updated as appropriate during the support period? | No | Ch. II Art. 13 | No support period declared |
| 4 | Does your cybersecurity risk assessment comprise an analysis based on the intended purpose and reasonably foreseeable use of the product? | No | Ch. II Art. 13 | No threat model in repository |
| 5 | Does your risk assessment take into account the conditions of use, operational environment, and assets to be protected? | No | Ch. II Art. 13 | No attack-surface analysis |
| 6 | Does your risk assessment consider the length of time the product is expected to be in use? | No | Ch. II Art. 13 | No EOL or support-lifecycle statement |
| 7 | Does your cybersecurity risk assessment indicate whether and how the security requirements are applicable to your product? | No | Ch. II Art. 13 | Objective tree provides this once populated |
| 8 | Do you include the cybersecurity risk assessment in the technical documentation when placing the product on the market? | No | Ch. II Art. 13 | Technical File pages are empty at baseline |
| 9 | Where certain essential cybersecurity requirements are not applicable, do you include clear justification in the technical documentation? | No | Ch. II Art. 13 | No N/A justifications recorded |
| 10 | Do you systematically document relevant cybersecurity aspects concerning your products with digital elements? | Partially | Ch. II Art. 25 | Extensive docs exist but **contradict the code** (Non-conformity 8) |
| 11 | Do you document vulnerabilities of which you become aware and relevant information provided by third parties? | No | VH-1 | No advisory tracking, no CVE process |
| 12 | Are your products with digital elements designed, developed and produced to ensure an appropriate level of cybersecurity based on the risks? | No | Annex I 1 | Non-conformities 1, 3, 8 |
| 13 | Are your products with digital elements delivered without any known exploitable vulnerabilities? | No | Annex I 2 | Non-conformity 1 + OSV scan output |
| 14 | Are your products made available on the market with a secure by default configuration? | Partially | Annex I 3a | Claim 7 vs. Non-conformity 6; Semgrep permissive-permissions findings |
| 15 | Do you provide the possibility to reset the product to its original state? | Partially | Annex I 3a | `clear-db.sh`, `delete-certs.sh` — operator scripts, not a product feature |
| 16 | Do you ensure that vulnerabilities can be addressed through security updates? | Partially | Annex I 3k | Claim 9; manager has no update path |
| 17 | Are automatic security updates installed within an appropriate timeframe enabled as a default setting? | Partially | Annex I 3k | Agent polls (`update.go:265`, a 10 s defect); manager none |
| 18 | Do you provide a clear and easy-to-use opt-out mechanism for automatic updates? | No | Annex I 3k | Not evidenced |
| 19 | Do you notify users of available updates with the option to temporarily postpone them? | No | Annex I 3k | `release_notes` placeholder; no notification |
| 20 | Do you ensure protection from unauthorized access by appropriate control mechanisms? | No | Annex I 3b | Non-conformities 1, 2 |
| 21 | Do you implement authentication, identity or access management systems? | No | Annex I 3b | Non-conformity 2 — removed 2025-10-29 |
| 22 | Do you report on possible unauthorized access? | Partially | Annex I 3b | Claim 5 logging; no user auth to fail, no alerting |
| 23 | Do you protect the confidentiality of stored, transmitted or otherwise processed data through encryption? | Partially | Annex I 3c | Claims 1, 2, 8 vs. Non-conformities 5, 6 |
| 24 | Do you use state-of-the-art mechanisms for encrypting relevant data at rest or in transit? | Partially | Annex I 3c | In transit yes (Claim 1); at rest no |
| 25 | Do you protect the integrity of stored, transmitted or otherwise processed data, commands, programs and configuration? | Partially | Annex I 3d | Claim 1; commands unsigned, no replay protection |
| 26 | Do you protect against manipulation or modification not authorized by the user? | No | Annex I 3d | Non-conformity 1 |
| 27 | Do you report on corruptions of data, commands, programs and configuration? | No | Annex I 3d | Not evidenced |
| 28 | Do you process only data that is adequate, relevant and limited to what is necessary for the intended purpose? | No | Annex I 3e | Non-conformity 5 |
| 29 | Do you protect the availability of essential and basic functions, also after an incident? | **Yes** | Annex I 3f | Claim 4 — DLQ schema + resume-after-restart |
| 30 | Do you implement resilience and mitigation measures against denial-of-service attacks? | Partially | Annex I 3f | Bounded channels, read limits; rate limiter covers only `/api/register` |
| 31 | Do you minimize the negative impact by your products on the availability of services provided by other devices or networks? | Partially | Annex I 3g | Claim 6; no block TTL, no reachable unblock |
| 32 | Are your products designed, developed and produced to limit attack surfaces, including external interfaces? | Partially | Annex I 3h | Claims 2, 3; privileged container, published Ollama port |
| 33 | Are your products designed to reduce the impact of an incident using appropriate exploitation mitigation mechanisms? | Partially | Annex I 3i | Claim 6 + rollback; no sandboxing or denylist |
| 34 | Do you provide security-related information by recording and monitoring relevant internal activity? | **Yes** | Annex I 3j | Claim 5 |
| 35 | Do you monitor access to or modification of data, services or functions with an opt-out mechanism for users? | Partially | Annex I 3j | Monitoring yes; opt-out not evidenced |
| 36 | Do you provide the possibility for users to securely and easily remove all data and settings on a permanent basis? | Partially | Annex I 3e | Reset scripts + log-retention cron; not user-facing |
| 37 | Where data can be transferred to other products or systems, do you ensure this is done in a secure manner? | Partially | Annex I 3c | STIX 2.1 export over TLS, but the API is unauthenticated |
| 38 | Do you identify and document vulnerabilities and components contained in your products with digital elements? | No | VH-1 | Non-conformity 4; OSV + SBOM Generator output |
| 39 | Do you draw up a software bill of materials in a commonly used and machine-readable format? | No | VH-1 | No SBOM ships. **Fix in Step 3 of the runbook** |
| 40 | Does your software bill of materials cover at least the top-level dependencies of the products? | No | VH-1 | Same |
| 41 | Do you apply effective and regular tests and reviews of the security of your products with digital elements? | No | VH-3 | No CI, no pen-test records |
| 42 | Once a security update is made available, do you share and publicly disclose information about fixed vulnerabilities? | No | VH-4 | No advisory channel |
| 43 | Do you provide a description of vulnerabilities, affected products, impacts, severity and remediation information? | No | VH-4 | No advisories published |
| 44 | Do you have a policy on coordinated vulnerability disclosure in place and enforced? | No | VH-5 | No `SECURITY.md` |
| 45 | Do you facilitate the sharing of information about potential vulnerabilities in your product and third-party components? | No | VH-6 | No channel; SBOM absent |
| 46 | Do you provide a contact address for reporting vulnerabilities discovered in your products? | No | VH-6 | `readme.md:394` empty placeholder |
| 47 | Do you provide mechanisms to securely distribute updates for your products with digital elements? | Partially | VH-7 | Claim 9 — fails open, nothing signed |
| 48 | Do you ensure vulnerabilities are fixed or mitigated in a timely manner through updates? | No | VH-2 | No SLA, no changelog, no tags |
| 49 | Where applicable, are security updates distributed in an automatic manner? | Partially | VH-7 | Agent yes, manager no |
| 50 | Do you disseminate security updates without delay when they are available to address identified security issues? | No | VH-8 | No release process |
| 51 | Are security updates provided free of charge (unless otherwise agreed for tailor-made products)? | Partially | VH-8 | Implied by licensing but undeclared |
| 52 | Do you accompany security updates with advisory messages providing users with relevant information? | No | VH-8 | `release_notes` = `'Bug fixes and improvements'` |

> 💡 Use **Suggest from Scans** and **AI Suggest Answers** in the Assessments toolbar on at least Q13, Q38 and Q39 — the OSV and SBOM Generator results feed them directly, and demonstrating that the platform pre-populates answers from scanner output is a core part of the pilot.

---

## What the engineer actually clicks (assessment flow)

1. **Assessments → + New Assessment** — Framework: `CRA`, Assessment Type: `Conformity`, Scope Type: `Asset / Product`, Asset: `SEUXDR`, Name: `SEUXDR CRA Conformity Assessment`.
2. **Click the new card** under *Active Assessments* — the questionnaire opens with 52 questions paginated 10 per page. Each question shows `Mandatory: YES`, a `Completed` flag, `Yes` / `No` / `Partially` / `N/A` radios, an **Assign Policy** selector, an **Evidence Description** box and **Attach File(s)**.
3. **For each of the 52 questions** pick the answer from the table above, write the evidence description, assign the governing policy, attach the scan output or document, then **Save Answer**. The `Completed` flag flips to `YES`.
4. **Frameworks → Objectives** — select `CRA`, scope `Asset / Product → SEUXDR`, and set the **Compliance Status** for all 30 objectives per the coverage matrix. Upload evidence against each.
5. **Export PDF** from the Assessments toolbar, and **Export PDF** from Compliance Chain → Gap Analysis.

The combined exports — conformity questionnaire, objective tree, risk register, gap analysis, SBOM and VEX statements — form the **Annex V technical documentation skeleton** and the input to the Article 28 EU Declaration of Conformity.

---

## Why this matters in the proposal context

The CYBERFORT project (DIGITAL-ECCC-2024-DEPLOY-CYBER-06) targets micro and small enterprises that must demonstrate CRA compliance before placing products on the EU market. Clone Systems is exactly that profile, and SEUXDR is exactly that product: an **Annex III Class I** important product with digital elements, built by an SME, aimed at the EU SME security market.

The value the pilot demonstrates is not that the platform found bugs — Semgrep and OSV find bugs. It is that a **two-person engineering team produced, in a day, a complete and defensible regulatory position** on all 30 CRA objectives and all 52 conformity questions, with every answer traceable to a file and line, a quantified readiness score, the SBOM the Regulation requires, a VEX statement set, a technical-file structure, and a ranked remediation backlog with the four items that block market placement at the top. Reaching the same position through a consulting engagement is several weeks of work and a five-figure fee, and it produces a document rather than a live compliance chain that can be re-run after every release.

The uncomfortable half of the result is the honest half: the product as it stands cannot be CE-marked. Learning that from your own platform, before a notified body or a market-surveillance authority learns it, is precisely the outcome CYBERFORT exists to produce.
