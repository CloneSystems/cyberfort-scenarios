# Scenario 04 — Clone Systems SEUXDR

## Trainee handbook

> ⏱ Estimated time: **2 hours** &middot; 🎯 Level: **Intermediate** &middot; 🛡 Sector: **ICT security vendor (CRA manufacturer)**

---

## Scenario brief

You have been brought in as an **independent conformity assessor**.

Clone Systems manufactures **SEUXDR**, a self-hosted SIEM/XDR platform with local-LLM remediation. It is classified under the Cyber Resilience Act as an **Annex III important product with digital elements, Class I**. The company has just finished a remediation programme and is telling its board that the product is **70% CRA ready — 21 of 30 objectives compliant**.

Your job is not to take that on trust. It is to **verify the claim from the artefacts, and find what is still missing.**

You have:

* CyberFort credentials for a tenant with **CRA mode enabled** (`https://access.cyber-fort.eu`).
* The product source at the release under assessment — `SEUXDR 3.4.0`, branch `cra/remediation-sprint-1`. Your instructor will give you `seuxdr-3.4.0-src.zip` or repository access.
* The manufacturer's own compliance pack in `docs/cra/` inside that source.

> ℹ️ **This scenario uses the remediated product only.** There is a deliberately broken baseline of the same product (`00a95ad`) used elsewhere in the pilot; you are not looking at it. Assessing a *compliant* product is the harder and more realistic skill — anyone can write up a product that fails everything. The discipline being taught here is evidencing a pass and being honest about what still fails.

---

## Learning outcomes

By the end of this scenario you will be able to:

1. Verify a manufacturer's CRA product classification and say why self-assessment is or is not available.
2. Use the **SBOM Generator** to confirm a component-inventory claim rather than accept it.
3. Use **Dependency Check** and **Code Analysis** to test claims made in a compliance document against the code.
4. Confirm that Annex I Part II vulnerability-handling artefacts exist *and* say something useful about their quality.
5. Test an access-control claim behaviourally, not just by reading a policy.
6. Set the compliance status of all **30 CRA objectives** with evidence attached.
7. Identify the **residual gaps** a manufacturer's own summary tends to soften.
8. Export a conformity pack and write an assessor's opinion that a notified body could act on.

---

## Step 0 — Get the source and confirm what you are assessing

You do **not** need the product running for most of this scenario. CyberFort's three source-side scanners take an archive or a repository URL, and they carry the bulk of the assessment.

```bash
unzip seuxdr-3.4.0-src.zip -d ~/assess && cd ~/assess
cat VERSION                       # expect: 3.4.0
head -20 CHANGELOG.md             # expect: [3.4.0] - 2026-07-30
git log --oneline -3              # if you were given repo access
```

> 🛑 **Check the version claim first.** A Declaration of Conformity has to identify the product. Confirm `VERSION` exists and that the manager, agent and front end are reconcilable to it. Note what you find — the agent still declares `1.0.1` in its own configuration and the front end `package.json` still says `0.0.0`. Decide for yourself whether one `VERSION` file is sufficient *Product Identification* under Annex V, and write down your reasoning.

Sign in to CyberFort. The modules you will use are **Assets / Products**, **Security Tools**, **Frameworks → Objectives**, **Documents** and **Compliance Chain**.

![CyberFort dashboard after sign-in](screenshots/step0-03-dashboard.png)

---

## Step 1 — Confirm the classification, and its consequence

Open **Assets / Products → Manage Assets** and find `SEUXDR`. Check the **Criticality** field.

![Asset registered with its CRA classification](screenshots/step1-03-add-asset-modal-filled.png)

It should read *Security information and event management (SIEM) systems*, under the group header **ANNEX III – IMPORTANT PRODUCTS WITH DIGITAL ELEMENTS – Class I**.

Now do the assessor's job: **test the classification instead of accepting it.** Read the product description and satisfy yourself that it is a SIEM. Then look for the other limbs — search the source for what the remediation actions actually do:

```bash
grep -rn "iptables -I INPUT\|netsh advfirewall\|pfctl" agent/active-response/ | head
grep -rn "rm -f\|DEL /F" agent/active-response/ | head
```

> 🛑 **Residual gap #1 — the conformity route.** SEUXDR qualifies as an important product on three independent Annex III limbs: it is a SIEM, it is an intrusion detection and prevention system, and it removes or quarantines malicious software. Under **Article 32(2)** that means a notified body must be involved — a Module A internal-control self-declaration is **not** available. Check whether the manufacturer has engaged one. They have not. This is the single largest open item and no amount of engineering closes it.

---

## Step 2 — Verify the SBOM claim

The manufacturer claims a machine-readable SBOM is generated on every build. Test it.

Go to **Security Tools → SBOM Generator**, upload the archive, accept the authorisation disclaimer and click **Generate SBOM**.

![SBOM Generator with a completed run](../presentation/assets/sbom2_result.png)

Expect roughly **300 components** across a handful of licences. Then check the claim properly:

```bash
cat .github/workflows/security.yml | grep -A4 -i "sbom\|cyclonedx"
cat docs/cra/SBOM_POLICY.md | head -40
```

> 💡 Compare what the scanner found against what the policy promises. The policy commits to CycloneDX 1.5 covering **both** the Go module and the front end. Look at the component list the platform produced and ask whether Go modules are actually represented, or whether the inventory is predominantly npm. Write down the answer — this is exactly the kind of gap a notified body will probe.

---

## Step 3 — Test the dependency and code claims

**Security Tools → Dependency Check**, same archive, **Run Scan**.

![Dependency Check after the run](../presentation/assets/dep_done_640.png)

Then **Security Tools → Code Analysis** with the same archive.

Now read `docs/cra/DEPENDENCY_POLICY.md` and check whether the code matches the policy:

```bash
grep -nE "golang-migrate|gorilla/websocket|go-cache" go.mod
grep -n "faker" manager_front/package.json
grep -n "npm ci\|npm install" manager_front/Dockerfile
grep -rn "S1lMfWxh1HB6SbKg" . --include=*.go
```

> 🛑 **Residual gap #2 — the committed credential is gone from the code, not from history.** The live admin password no longer appears in the working tree, but `docs/cra/SECRET_ROTATION.md` states plainly that it remains in git history and requires rotation plus a history rewrite. Verify the manufacturer has documented this rather than quietly dropped it. Credit them for the honesty; record it as open.

> 💡 The dependency policy names a blocked-component register. Check that `gorilla/websocket` — which carries the remediation command channel — is on it, and note its version against what upstream ships.

---

## Step 4 — Confirm the vulnerability-handling artefacts

Annex I Part II is where the baseline product failed hardest. Check each artefact exists and is real, not a stub:

```bash
ls -la SECURITY.md .well-known/security.txt CHANGELOG.md VERSION
ls .github/workflows/
ls docs/cra/
grep -n "24\|72\|ENISA" SECURITY.md | head
grep -n "support period\|2031" docs/cra/PATCH_AND_SUPPORT_POLICY.md | head -5
```

You are looking for six things, and all six should be present:

| Artefact | What good looks like |
|----------|----------------------|
| Security contact | A monitored address, not a placeholder |
| Disclosure timeline | Acknowledgement, triage and remediation windows by severity |
| Article 14 procedure | The 24-hour, 72-hour and 14-day ENISA deadlines named explicitly |
| SBOM in CI | Generated per build and attached to releases |
| Scanning in CI | `govulncheck`, `npm audit`, container scanning, secret scanning |
| Support period | At least five years, with an end date |

> 💡 Cross-check one claim against the platform. Open **Documents → Technical File → Vulnerability Disclosure** and compare the six numbered requirements the CRA expects against what `SECURITY.md` actually commits to. A document that exists is not the same as a document that satisfies the requirement.

![Technical File — Vulnerability Disclosure](screenshots/step6-05-tf-vuln-disclosure.png)

---

## Step 5 — Test the access-control claim behaviourally

This is the only step that needs the product running. Your instructor will give you the target host.

The manufacturer claims the manager API is now authenticated. **Test it rather than reading about it.**

```bash
# no credential at all — expect 401
curl -sk -o /dev/null -w '%{http_code}\n' -X POST \
  -H 'Content-Type: application/json' -d '{}' \
  https://<TARGET>:8443/api/agent/1/execute-action

# the CA download must stay open: agents need it before they hold a credential
curl -sk -o /dev/null -w '%{http_code}\n' https://<TARGET>:8443/api/certs/server-ca.crt
```

A `401` on the first and a `200` on the second is the correct result. Then read how it is implemented:

```bash
wc -l manager/middlewares/auth.go
grep -n "Authenticate()\|RequireRole" manager/routes/routes.go
grep -n "initiated_by\|initiated_from" manager/models/models.go
```

> 🛑 **Residual gap #3 — authentication is not authorisation.** Read `manager/middlewares/auth.go` carefully and check how many routes are gated by `RequireRole`. You should find exactly one. Then look for organisation scoping in the handlers — there is none, which is why `docs/cra/RISK_ASSESSMENT.md` records risk R-12 with a **single-tenant deployment requirement**. Decide whether Annex I 2(b) is met by authentication alone when any authenticated principal can read across organisations. Say so in your opinion either way.

> 💡 There is a second-order consequence worth spotting: agents authenticate with `Authorization: ID <agentID>`, which is an identifier and not a credential. With authentication enforced, enrolled agents receive 401 until they carry a real token. Check whether the manufacturer has documented that rollout.

---

## Step 6 — Test the remediation-safety claim

The product lets a language model choose targets for destructive actions. Verify the guardrails.

```bash
go test ./manager/helpers/ -run TestValidateActionTarget -v 2>&1 | tail -20
grep -n "ACTION_MODE" manager/config/config.go
```

Read `manager/helpers/targets.go` and answer three questions for your report:

1. What happens if the model returns a private RFC1918 address for `BLOCK_IP`? *(It is refused — which also means the product cannot block an internal attacker. Is that the right trade?)*
2. What happens if it returns `/etc/passwd` for `DELETE_FILE`?
3. Is the same validation applied on the agent, or only on the manager?

> 🛑 **Residual gap #4 — deletion is still deletion.** Target validation stops the wrong file being chosen, but `DELETE_FILE` is still an unrecoverable `rm -f` with no quarantine and no restore, and `BLOCK_IP` still has no expiry and no reachable `UNBLOCK_IP` path. Check `docs/cra/RISK_ASSESSMENT.md` for whether the manufacturer scored these honestly.

---

## Step 7 — Score all 30 objectives yourself

Go to **Frameworks → Objectives**, select framework `CRA`, scope `Asset / Product`, asset `SEUXDR`.

![Selecting the CRA framework](../presentation/assets/framework_select.png)

Work down all 30 objectives and set a **Compliance Status** based on the evidence *you* gathered, uploading it as you go. Do not copy the manufacturer's grading — the point of the exercise is to arrive at your own and then compare.

The manufacturer's position is 21 compliant, 8 partially compliant, 1 not compliant. When you are done, compare yours against theirs and be ready to defend every difference.

![The CRA objective tree for SEUXDR](screenshots/step8-01-objectives-cra-seuxdr.png)

> 💡 Two objectives should be straightforward passes and are worth understanding as examples of good evidence: Annex I **3f** (availability — the failed-alert queue, dead-letter queue and resume-after-restart) and **3j** (security-event recording — structured logging with correlation IDs and a persisted AI reasoning trail). Read the code behind both. This is what a defensible *Yes* looks like.

---

## Step 8 — Complete the conformity assessment

**Assessments → + New Assessment**: framework `CRA`, type `Conformity`, scope `Asset / Product → SEUXDR`, name it with your own surname so your instructor can find it.

![The conformity questionnaire](../presentation/assets/questions.png)

Answer all 52 questions. For each one, write an **Evidence Description** naming the file or the platform artefact you relied on, and attach the scan output where you have it.

> ⚠️ Answer honestly. The temptation on a remediated product is to mark things `Yes` because the documentation says so. Six of these questions cannot honestly be `Yes` on this release — find them. If your distribution comes out dramatically better than the manufacturer's own, you have probably accepted a document at face value somewhere.

---

## Step 9 — Write the assessor's opinion

Export the pack: **Assessments → Export PDF**, **Frameworks → Objectives → Export PDF**, and **Compliance Chain → Gap Analysis → Export PDF**.

![Gap analysis for the CRA framework](screenshots/step9-01-gap-analysis-cra.png)

Then write **one page** answering three questions:

1. **Is the manufacturer's 70% claim supportable?** Give a number of your own and justify the difference.
2. **What blocks a Declaration of Conformity today?** Rank them.
3. **What would you require before signing?** Be specific enough that an engineer could act on it.

> 🛑 **Residual gap #5 — the score is not the conclusion.** Read `docs/PILOT_TIMELINE.md` and note that the platform exposes three different CRA percentages measuring three different things. If your opinion quotes a percentage, say which one and at what scope. An assessor who quotes a number without its denominator has not finished the job.

---

## Step 10 — Stretch goals (optional)

* Deploy the **baseline** product (`00a95ad`) alongside and run the same `curl` from Step 5. Watch the same request succeed with no credential, then re-run the objectives checklist against it and see the position collapse to 2 of 30.
* Draft the missing **organisation-scoping** requirement as a risk-register entry with a treatment plan.
* Use **Security Tools → VEX Statements** to publish a CycloneDX VEX for one advisory the dependency scan raised, and explain why VEX matters more than the SBOM alone.
* Use the **AI Assistant** to draft the assessor's opinion, then mark up everything it overstated. That exercise is the point, not the draft.

---

## Checklist

Tick these off before declaring the scenario complete.

* [ ] Product version and classification verified, Article 32(2) consequence stated
* [ ] SBOM generated and compared against the manufacturer's SBOM policy
* [ ] Dependency and code scans run; policy claims tested against `go.mod` and `package.json`
* [ ] All six vulnerability-handling artefacts confirmed present and assessed for quality
* [ ] Access control tested behaviourally with `curl`, not just read about
* [ ] Remediation-safety guardrails read and the three questions answered
* [ ] All 30 objectives graded independently, with evidence attached
* [ ] All 52 conformity questions answered with evidence descriptions
* [ ] Readiness pack exported (assessment, objectives, gap analysis)
* [ ] One-page assessor's opinion written, with a defended number and a ranked blocker list
