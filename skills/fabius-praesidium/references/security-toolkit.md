# Fabius Praesidium — security toolkit

The arsenal for `fabius-praesidium`. The skill says *which step* (threat-model → audit → harden → prove); this file says *which tool* — the strongest, actively-maintained open-source instrument for each defensive job, so you reach for the vetted one instead of hand-rolling. Companion to the method in [security-playbook.md](security-playbook.md) and the deep how-to in [hardening-guides.md](hardening-guides.md); third-party AI-artifact vetting lives in [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md).

**Read this the fabius way.** Star counts are point-in-time (verified 2026-07-03 via the GitHub API) — they rank *adoption*, never *fit for your threat model*. Scout wide across the surface; strike narrow with the smallest set that closes it. Running ten scanners is not ten times the security — it is ten times the noise. **Defensive only.** The one dual-use exception (authorized red-team) is boxed at the bottom, behind an explicit authorization gate.

---

## Pick by job — the fast index

| Need | Reach for (strong → language-specific) |
|---|---|
| Flaws in your own code (SAST) | **Semgrep** → CodeQL → Bandit (Py) / gosec (Go) / Brakeman (Rails) |
| Dependency CVEs (SCA) | **Trivy** / OSV-Scanner / Grype |
| Leaked secrets | **Gitleaks** / TruffleHog |
| IaC + container misconfig | **Trivy** / Checkov |
| SBOM + artifact signing | **Syft** (SBOM) + **Cosign** (sign/verify) |
| Running web app (DAST) | **ZAP** (formerly OWASP ZAP); Nuclei (templated checks, own assets only) |
| LLM / AI-model weakness | **garak** → deepteam / PyRIT; **Guardrails** at runtime (not LLM Guard — archived) |
| Third-party AI artifact (skill/plugin/MCP) | → [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md) |

Default stack for most projects: **Semgrep + Trivy + Gitleaks** in CI, gate the merge on highs. Add the rest by surface.

---

## 1 · Static analysis (SAST) — flaws in your own source

- **Semgrep** — engine `semgrep/semgrep` · ⭐16.1k · LGPL-2.1 — **but the rules are on a different license, and the rules are what you actually consume.** 30+ languages, custom rules in readable YAML, scans a 500k-LOC repo in seconds. Still the default first SAST and CI gate; write project rules to enforce your own patterns (and flag where new code *deviates* from them — the §7 discipline). **Two flags before you ship it:**
  - **(1) The community ruleset is not LGPL.** `semgrep/semgrep-rules` carries the **Semgrep Rules License v1.0** (dated 2024-12-13): use "only for your own internal business purposes", and it "does not allow you to distribute the rules, or to make them available to others as a service". GitHub classifies that repo **`NOASSERTION`** — so a *block-known-bad-allow-the-rest* license gate waves it into a product and reports green, [hardening-guides.md](hardening-guides.md) §9(b) firing on this page's own default tool. Internal CI over your own code is clear; redistributing the rules or running them as a service for third parties is not. **Check the license of the artifact you consume, not the one on the repo you name.**
  - **(2) Depth is the paid tier.** Community Edition analyzes **within a single function** (intraprocedural); cross-function and cross-file analysis are Semgrep Code, the commercial product. Plan the gate around what CE actually sees.
  - If either line binds you, **Opengrep** — `opengrep/opengrep` · ⭐2.9k · **LGPL-2.1** — is the consortium fork created in 2025 for exactly this reason and is actively maintained. Rules you write yourself stay clean under either engine.
- **CodeQL** — `github/codeql` (GitHub) · free for open source. Semantic "code as a queryable database" — the deepest taint-tracking for the languages it covers; heavier to run, worth it for auth/parser-grade code.
- **Language depth** — **Bandit** (`PyCQA/bandit` ⭐8.1k, Python), **gosec** (Go), **Brakeman** (Rails). Cheap, precise, run alongside Semgrep.

## 2 · Dependencies & supply chain (SCA)

- **Trivy** — `aquasecurity/trivy` · ⭐36.7k · Apache-2.0 · Aqua Security. The all-in-one cloud-native scanner: OS packages, language deps, containers, IaC, secrets, and cloud accounts in one binary. The most-adopted OSS security scanner — the default here.
- **OSV-Scanner** — `google/osv-scanner` · ⭐10.6k · Apache-2.0 · Google. Deps checked against the open OSV vulnerability database; clean CI output.
- **Grype** — `anchore/grype` · ⭐12.5k · Apache-2.0. Pairs with **Syft** (`anchore/syft` ⭐9.2k) for SBOM → scan.
- Always: pin with a lockfile, run `npm/pip/cargo audit`, act on highs (the §5 supply-chain leg of the skill).

## 3 · Secrets

- **Gitleaks** — `gitleaks/gitleaks` · ⭐28k · MIT. Pre-commit hook + full-history scan; stop the leak before the push, find the ones already in history (a committed secret is a leaked secret — rotate it).
- **TruffleHog** — `trufflesecurity/trufflehog` · ⭐27k · AGPL-3.0. **Verifies** found secrets against the live provider (drops false positives); scans git, buckets, and CI logs.

## 4 · IaC & containers

- **Trivy** (above) + **Checkov** — `bridgecrewio/checkov` · ⭐8.8k · Apache-2.0. Terraform / Kubernetes / CloudFormation / Helm misconfig against hundreds of policies; fails the pipeline on the ones that matter.

## 5 · SBOM & artifact integrity

- **Syft** (SBOM) + **Cosign** — `sigstore/cosign` · ⭐6.1k · Apache-2.0 · sigstore. Sign build artifacts and **verify** provenance on the way in — the "verify anything you didn't write" leg of the supply chain, keyless via sigstore.

## 6 · DAST — the running application

- **ZAP** *(formerly OWASP ZAP)* — `zaproxy/zaproxy` · ⭐15.5k · Apache-2.0 · latest **v2.17.0** (2025-12-15). The OSS web app scanner + intercepting proxy; still the default DAST for your own staging. **It is no longer an OWASP project** — on 2023-08-01 it left OWASP as a founding project of the Linux Foundation's Software Security Project ("From now on 'OWASP ZAP' will be known as just 'ZAP'"), and it now ships as **"ZAP by Checkmarx"** — same repo, same Apache-2.0, same core team, actively developed. The move has a **pipeline consequence**, not just a naming one: the images left the OWASP org, and `owasp/zap2docker-*` is now **gone from Docker Hub** (404, checked 2026-08-06), so a legacy CI job naming it fails the pull. Pull `zaproxy/zap-stable` or `ghcr.io/zaproxy/zaproxy:stable`.
  - *The rule this row exists to teach: a tool's **steward** can change while its name, its repo slug and its license all stay put. "Who stands behind this, and where do its artifacts come from now?" is a fact to re-verify at adoption — never one to recall.*
- **Nuclei** — `projectdiscovery/nuclei` · ⭐29.5k · MIT. Fast, template-driven checks (thousands of community templates). **Dual-use** — point it only at assets you own; keep scope tight.

## 7 · AI / LLM security (defensive)

The newest surface — model, prompt, and agent, not just code.

- **garak** — `NVIDIA/garak` · ⭐8.3k · Apache-2.0 · NVIDIA. The "nmap for LLMs": probes *your* model for prompt-injection, jailbreak, data leakage, toxicity, and more. The default LLM vulnerability scanner.
- **PyRIT** — `microsoft/PyRIT` · ⭐4k · MIT · Microsoft. Battle-tested risk-identification harness for GenAI; automate red-team probes over your own AI system.
- **deepteam** — `confident-ai/deepteam` · ⭐1.9k · Apache-2.0. Red-team your LLM app / RAG / agent for jailbreak, prompt-injection, PII leakage, bias.
- **Guardrails** — `guardrails-ai/guardrails` · ⭐7.3k · Apache-2.0. Runtime input/output guardrails (the *fix*, not just the finding) — validators in the request path for injection, PII, and format violations. The maintained, cleanly-licensed default for this slot.
- **LLM Guard** — `protectai/llm-guard` · ⭐3.2k · MIT · **ARCHIVED upstream (read-only, last commit 2026-07)**. Still the clearest scanner taxonomy to *learn* from — prompt-injection, PII, toxicity, topic bans, canary leaks. Do not ship it as a live control: **a guardrail sits in the request path, so it is production security code, and an archived dependency ships you its future CVEs with nobody to patch them.** Read it, then implement against something maintained.

**The rule this row exists to teach:** a scanner that finds a hole may be stale and merely lose you coverage; a **runtime guardrail that is stale is an unpatched component inside your own boundary.** Hold in-path security dependencies to a maintenance bar you never demand of an offline scanner — check the archive flag and the last release *before* adopting, and re-check on every bump (the blind-window rule in [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md) §2).

*(Vetting a third-party skill/plugin/MCP server you want to install — the exec/data/net/creds gate, SHA-pinning, sandboxing — is its own leg: [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md).)*

---

## Israeli market — consume the owning localization layer

Praesidium owns technical threat-model controls, not mutable Israeli legal/localization facts. When the target is Israeli, load [`fabius-decor/references/israel-localization.md`](../../fabius-decor/references/israel-localization.md), re-verify the current requirement there, and map only its security-bearing consequences (data handling, access, incident response, consent enforcement, auditability) into this review. Accessibility presentation stays with `fabius-decor`; message wording stays with `fabius-mercatus`. Do not duplicate dates, thresholds, or statutory claims here: two owners drift.

## EU market — the Cyber Resilience Act reporting clock (from 11 September 2026)

**Settle scope first; most web work is out.** The CRA binds the **manufacturer** of a *product with digital elements* placed on the Union market — "a software or hardware product and its remote data processing solutions". A hosted service counts only where the manufacturer **designed and developed** it and the product cannot perform its function without it; a plain SaaS or an internal service is not a CRA product. Two carve-outs decide the rest: free and open-source software **not supplied as a commercial activity** is outside the regulation, and an **open-source steward** carries a reduced regime — the reporting duty applies, but stewards are **not subject to CRA penalties**. Fold open source into a commercial product and the commercial manufacturer inherits the duty. Answer *"am I the manufacturer of an in-scope product?"* before building any of the machinery below.

**If you are in scope, the clock is live from 11 September 2026** — and it reaches products **already on the market**, not only new releases. An actively exploited vulnerability or a severe security incident is reported through the **CRA Single Reporting Platform** to the CSIRT of your member state, reaching **ENISA** at the same time:

```
[ ] early warning      → 24 hours of becoming aware
[ ] full notification  → 72 hours
[ ] final report       → 14 days after a corrective measure is available
                         (a severe INCIDENT: one month)
```

**Treat 24 hours as an engineering requirement, not a legal one.** It buys nothing to know the deadline on the day: it means a **named owner**, a **pre-registered** reporting channel, and a path from *"a researcher just told us"* to *"submitted"* that someone has **walked end to end at least once**. Audit it like any other control — who receives the disclosure, who decides it is in scope, who files, and has the path ever been rehearsed. An unwalked path is an unchecked cell in the grid.

*Dates and deadlines above read from the Commission's own reporting page, checked 2026-08-06; the delegated act on CSIRT dissemination and the ENISA guidance still move — re-verify before you rely on it.* Defensive framing only — this hardens a product against its own compliance risk. Reach for it **only when the target is placed on the EU market**.

## The one gate — authorized offensive testing (red-team / adversary emulation)

> **⚠ Authorization first, always.** These tools attack. Run them **only** against systems you **own** or are **explicitly contracted and scoped** to test (a signed engagement / bug-bounty program). Fabius will not point them at systems the user does not own — that is not defense, it is intrusion, and it is out of scope (see the skill's boundary). Included here because a defender must know what the offense wields, and because authorized red-team of *your own* stack is legitimate security work.

- **Strix** — `usestrix/strix` · ⭐33.5k · Apache-2.0. Autonomous AI penetration tester: acts like a real attacker — runs your code dynamically, finds vulnerabilities, and **validates each with a real proof-of-concept** rather than a static guess. The most-adopted of the open AI-pentest agents.
- **CAI** — `aliasrobotics/cai` · ⭐9.7k · **split license — non-commercial** · Alias Robotics. Bug-bounty-ready AI security agent framework (evolved from PentestGPT), 300+ model backends. Only the `src/cai/agents` portion derived from `openai/openai-agents-python` is MIT; **every Alias Robotics addition — the framework itself — is a research-use license: non-commercial research and academic use only, with commercial, professional, or production use prohibited without a paid license.** That bars it from client engagements and from your own production red-teaming, not just from resale. GitHub classifies it `NOASSERTION`, so a *block-AGPL-allow-the-rest* policy gate waves it into a commercial product and reports green — the exact trap in [hardening-guides.md](hardening-guides.md) §6. Default-deny on the classification: verify the LICENSE text yourself, or don't run it on paid work.
- **PentestGPT** — `GreyDGL/PentestGPT` · ⭐14k · MIT. The USENIX'24 LLM pentest agent — reasoning / generation / parsing modules.
- **HexStrike-AI** — `0x4m4/hexstrike-ai` · ⭐10k · MIT. Exposes 150+ security tools as MCP endpoints for any MCP client (Claude included) — agentic recon → exploit orchestration.

**Run them the fabius way even here:** scout wide (recon/enumerate), then **strike narrow** — every reported vulnerability gets a real PoC (the §6 fix contract: *no finding without proof*) and is handed back as `severity → fix → regression test`. The moment you have the finding, you are back in defense: close it, prove it closed.

---

## Notes

- Metrics **verified 2026-07-03** via the GitHub API; treat as point-in-time. The §7 runtime-guardrail slot and the red-team **license and archive flags** were re-verified **2026-08-06** against the GitHub API and the repositories' own LICENSE text. That re-check covered the flags only — **every star count on this page is still the 2026-07-03 reading** and several have since drifted upward. Take the licence and maintenance flags as fresh; take the popularity numbers as a floor, not a figure. Adoption ≠ fit — choose by threat model and license (LGPL/AGPL/`NOASSERTION` licenses carry obligations; read before shipping).
- **A license flag is a finding, and it rots in both directions.** Re-read the LICENSE text, never the badge: a repo can relicense *toward* permissive as easily as away from it, and `NOASSERTION` means the classifier failed — not that the terms are mild. Under-flagging ships you a compliance breach; over-flagging costs you a tool you were entitled to use. Both are defects; verify the text.
- Cross-links: audit **method** → [security-playbook.md](security-playbook.md) · deep **how-to** → [hardening-guides.md](hardening-guides.md) · third-party **AI artifacts** → [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md) · mutable **Israeli-market** requirements → [`fabius-decor/references/israel-localization.md`](../../fabius-decor/references/israel-localization.md) · smart-contract / on-chain audit gate → `fabius-catena`.
