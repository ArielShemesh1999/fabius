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
| Running web app (DAST) | **OWASP ZAP**; Nuclei (templated checks, own assets only) |
| LLM / AI-model weakness | **garak** → deepteam / PyRIT; LLM Guard at runtime |
| Third-party AI artifact (skill/plugin/MCP) | → [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md) |

Default stack for most projects: **Semgrep + Trivy + Gitleaks** in CI, gate the merge on highs. Add the rest by surface.

---

## 1 · Static analysis (SAST) — flaws in your own source

- **Semgrep** — `semgrep/semgrep` · ⭐15.7k · LGPL-2.1. 30+ languages, 3000+ community rules, custom rules in readable YAML, scans a 500k-LOC repo in seconds. The default first SAST and CI gate; write project rules to enforce your own patterns (and flag where new code *deviates* from them — the §7 discipline).
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

- **OWASP ZAP** — `zaproxy/zaproxy` · ⭐15.4k · Apache-2.0. The OSS web app scanner + intercepting proxy; the flagship OWASP dynamic tool for your own staging.
- **Nuclei** — `projectdiscovery/nuclei` · ⭐29.5k · MIT. Fast, template-driven checks (thousands of community templates). **Dual-use** — point it only at assets you own; keep scope tight.

## 7 · AI / LLM security (defensive)

The newest surface — model, prompt, and agent, not just code.

- **garak** — `NVIDIA/garak` · ⭐8.3k · Apache-2.0 · NVIDIA. The "nmap for LLMs": probes *your* model for prompt-injection, jailbreak, data leakage, toxicity, and more. The default LLM vulnerability scanner.
- **PyRIT** — `microsoft/PyRIT` · ⭐4k · MIT · Microsoft. Battle-tested risk-identification harness for GenAI; automate red-team probes over your own AI system.
- **deepteam** — `confident-ai/deepteam` · ⭐1.9k · Apache-2.0. Red-team your LLM app / RAG / agent for jailbreak, prompt-injection, PII leakage, bias.
- **LLM Guard** — `protectai/llm-guard` · ⭐3.1k · MIT. Runtime input/output guardrails (the *fix*, not just the finding). Verify maintenance before adopting.

*(Vetting a third-party skill/plugin/MCP server you want to install — the exec/data/net/creds gate, SHA-pinning, sandboxing — is its own leg: [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md).)*

---

## Israeli market — the legal surface a security review must cover

When the product serves the **Israeli market**, three *live, enforceable* obligations sit inside the threat model — a review that skips them is incomplete. The full layer (governing statutes, thresholds, data formats — all config-driven, verify current) is **Fabius Yisrael** (`fabius-decor` → `references/israel-localization.md`); pull only the obligation that bears on the surface you're reviewing:

- **Privacy — חוק הגנת הפרטיות + Amendment 13 (תיקון 13, in force 14 Aug 2025).** GDPR-adjacent and enforceable now: breach-notification duties, a DPO where triggered, administrative fines with a per-data-subject component. Fold it into the data-handling threat-model exactly as you would GDPR/CCPA.
- **Accessibility is statutory — IS 5568 (ת"י 5568 = WCAG 2.0 AA legal floor).** A missing/non-compliant הצהרת נגישות is grounds for immediate suit with no cure period — treat the accessibility statement + רכז נגישות as a compliance control, not a nicety.
- **Anti-spam — Chok HaSpam (§30א).** Commercial messaging is opt-in by law; each message labeled **"פרסומת"**, sender identified, free **הסרה** on the same channel. The *message* is `fabius-mercatus`'s; the *legal frame* is Yisrael's.

Defensive framing only — this hardens an Israeli product against its own compliance risk. Reach for it **only when the target is Israeli**.

## The one gate — authorized offensive testing (red-team / adversary emulation)

> **⚠ Authorization first, always.** These tools attack. Run them **only** against systems you **own** or are **explicitly contracted and scoped** to test (a signed engagement / bug-bounty program). Fabius will not point them at systems the user does not own — that is not defense, it is intrusion, and it is out of scope (see the skill's boundary). Included here because a defender must know what the offense wields, and because authorized red-team of *your own* stack is legitimate security work.

- **Strix** — `usestrix/strix` · ⭐33.5k · Apache-2.0. Autonomous AI penetration tester: acts like a real attacker — runs your code dynamically, finds vulnerabilities, and **validates each with a real proof-of-concept** rather than a static guess. The most-adopted of the open AI-pentest agents.
- **CAI** — `aliasrobotics/cai` · ⭐9.3k. Bug-bounty-ready AI security agent framework (evolved from PentestGPT), 300+ model backends. *Check its license before any commercial use.*
- **PentestGPT** — `GreyDGL/PentestGPT` · ⭐14k · MIT. The USENIX'24 LLM pentest agent — reasoning / generation / parsing modules.
- **HexStrike-AI** — `0x4m4/hexstrike-ai` · ⭐10k · MIT. Exposes 150+ security tools as MCP endpoints for any MCP client (Claude included) — agentic recon → exploit orchestration.

**Run them the fabius way even here:** scout wide (recon/enumerate), then **strike narrow** — every reported vulnerability gets a real PoC (the §6 fix contract: *no finding without proof*) and is handed back as `severity → fix → regression test`. The moment you have the finding, you are back in defense: close it, prove it closed.

---

## Notes

- Metrics **verified 2026-07-03** via the GitHub API; treat as point-in-time. Adoption ≠ fit — choose by threat model and license (LGPL/AGPL/`NOASSERTION` licenses carry obligations; read before shipping).
- Cross-links: audit **method** → [security-playbook.md](security-playbook.md) · deep **how-to** → [hardening-guides.md](hardening-guides.md) · third-party **AI artifacts** → [supply-chain-and-ai-artifacts.md](supply-chain-and-ai-artifacts.md) · **Israeli-market** legal obligations (privacy Amendment 13 · IS-5568 · Chok HaSpam) → **Fabius Yisrael** in `fabius-decor` · smart-contract / on-chain audit gate (Slither / Echidna / Foundry) is `fabius-catena`'s, not here.
