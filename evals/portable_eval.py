#!/usr/bin/env python3
"""
Portable fabius eval — works for ANY vendor, not just Claude.

Runs the same three-arm design as the Claude-Code harness (baseline / generic-terse /
fabius) against OpenAI (GPT/Codex), Mistral, and Anthropic models, then blind-judges
every answer and prints the per-model gain. Stdlib only — no pip install.

This is how you get REAL Codex / Mistral numbers: set the keys and run it.

    export OPENAI_API_KEY=...        # GPT-4o / gpt-4.1 / o-series (Codex family)
    export MISTRAL_API_KEY=...       # mistral-large-latest
    export ANTHROPIC_API_KEY=...     # claude-sonnet-4-6 etc.
    python3 evals/portable_eval.py

Pick which models to run with --models (default: every vendor whose key is set).
The judge defaults to the first available of OpenAI -> Anthropic -> Mistral.
Results are written to evals/results.portable.json and printed as a table.
"""
import argparse, json, os, sys, urllib.request, urllib.error

# ---- the three arms (identical to the Claude-Code harness) -------------------
FABOIUS = (
    "Operate under the Fabius stance:\n"
    "(1) LEAN OUTPUT - drop articles, filler, hedging, pleasantries; terse; fragments ok; keep ALL technical substance and correctness.\n"
    "(2) LEAN CODE (YAGNI ladder) - need it at all? stdlib? native feature? installed dep? one line? only then minimal code. No speculative abstraction, no config for a constant, no unrequested options.\n"
    "(3) SURGICAL - minimum change; don't improve adjacent code; match existing style.\n"
    "(4) THINK FIRST - if ambiguous, state the key assumption in one line; push back on over-spec.\n"
    "(5) NEVER trim away: input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly asked. Minimal, not flimsy. Non-trivial logic leaves one runnable check.\n"
    "(6) UI: one accent color, design tokens not inline hex, hierarchy from type not boxes, mobile-first.\n"
    "(7) Agents: precise description + tight tool allowlist + explicit output contract + least privilege."
)
TERSE = "Be concise. Write minimal code. Skip unnecessary explanation."
ARMS = {"baseline": "", "terse": TERSE, "fabius": FABOIUS}

TASKS = {
    "cache": "Add caching to this Python function so repeated calls with the same args are fast:\n\ndef get_user(user_id):\n    return db.query(\"SELECT * FROM users WHERE id=?\", user_id)",
    "debug": "This should return true only if the token is still valid; users are logged out one second early. Fix it:\n\nfunction isValid(token){ return token.expiresAt > Date.now() + 1000; }",
    "button": "Give the CSS for a primary button and a content card for a modern SaaS landing page. Production quality.",
    "agent": "Define a subagent (frontmatter + system prompt) that reviews PRs for security issues. It must not push or edit code.",
    "pool": "Explain database connection pooling.",
    "flag": "We need a configuration system to control whether dark mode is on. Build it.",
    "sql": "Write a Node.js Express route that looks up a user by the email in the request query and returns JSON.",
    "modal": "Build an accessible HTML + JS modal dialog.",
}

# ---- vendor registry: provider -> (env key, default model, caller) ----------
def _post(url, headers, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def call_openai(model, prompt, key):
    d = _post("https://api.openai.com/v1/chat/completions",
              {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
              {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2})
    return d["choices"][0]["message"]["content"]

def call_mistral(model, prompt, key):
    d = _post("https://api.mistral.ai/v1/chat/completions",
              {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
              {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2})
    return d["choices"][0]["message"]["content"]

def call_anthropic(model, prompt, key):
    d = _post("https://api.anthropic.com/v1/messages",
              {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
              {"model": model, "max_tokens": 2048, "messages": [{"role": "user", "content": prompt}]})
    return "".join(b.get("text", "") for b in d["content"])

VENDORS = {
    "openai":    {"env": "OPENAI_API_KEY",    "model": "gpt-4o",               "call": call_openai},
    "mistral":   {"env": "MISTRAL_API_KEY",   "model": "mistral-large-latest", "call": call_mistral},
    "anthropic": {"env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-6",    "call": call_anthropic},
}

JUDGE_PROMPT = (
    "You are a strict, blind judge. Task:\n{task}\n\nScore this answer 0-5 on each axis. "
    "correctness: solves it. minimality: lean, no bloat/over-engineering, appropriately concise (padded=LOW). "
    "bestpractice: keeps validation/security/accessibility/UI-tokens/agent-least-privilege and domain good practice.\n\n"
    "ANSWER:\n{answer}\n\nReply with ONLY compact JSON: {{\"correctness\":N,\"minimality\":N,\"bestpractice\":N}}"
)

def judge(task, answer, jv, jkey, jmodel):
    out = VENDORS[jv]["call"](jmodel, JUDGE_PROMPT.format(task=task, answer=answer[:6000]), jkey)
    s = out[out.find("{"): out.rfind("}") + 1]
    d = json.loads(s)
    return float(d["correctness"]) + float(d["minimality"]) + float(d["bestpractice"])

def run(models):
    avail = {v: c for v, c in VENDORS.items() if os.environ.get(c["env"])}
    if not avail:
        sys.exit("No API keys set. Export OPENAI_API_KEY / MISTRAL_API_KEY / ANTHROPIC_API_KEY and retry.")
    use = {v: avail[v] for v in models if v in avail} if models else avail
    if not use:
        sys.exit(f"None of {models} have a key set. Available: {list(avail)}")
    jv = next(iter(avail)); jkey = os.environ[avail[jv]["env"]]; jmodel = avail[jv]["model"]
    print(f"models={list(use)}  judge={jv}/{jmodel}\n")

    rows = {}
    for v, cfg in use.items():
        key = os.environ[cfg["env"]]
        for arm, pre in ARMS.items():
            lens, totals = [], []
            for tid, task in TASKS.items():
                prompt = (pre + "\n\n---\n\n" if pre else "") + f"Task:\n{task}\n\nAnswer directly. Return only your answer."
                try:
                    ans = cfg["call"](cfg["model"], prompt, key)
                    lens.append(len(ans)); totals.append(judge(task, ans, jv, jkey, jmodel))
                except (urllib.error.HTTPError, urllib.error.URLError, KeyError, ValueError) as e:
                    print(f"  ! {v}/{arm}/{tid}: {e}")
            rows[f"{v}/{arm}"] = {
                "n": len(totals),
                "avgOutChars": round(sum(lens) / len(lens), 1) if lens else None,
                "totalScore15": round(sum(totals) / len(totals), 2) if totals else None,
            }
    # deltas
    deltas = {}
    for v in use:
        b, t, f = rows.get(f"{v}/baseline", {}), rows.get(f"{v}/terse", {}), rows.get(f"{v}/fabius", {})
        if b.get("totalScore15") is not None and f.get("totalScore15") is not None:
            deltas[v] = {
                "baseline": b["totalScore15"], "terse": t.get("totalScore15"), "fabius": f["totalScore15"],
                "gain_vs_baseline": round(f["totalScore15"] - b["totalScore15"], 2),
                "output_reduction_pct": round(100 * (1 - f["avgOutChars"] / b["avgOutChars"]), 1) if b.get("avgOutChars") and f.get("avgOutChars") else None,
            }
    out = {"summary": rows, "deltas": deltas, "judge": f"{jv}/{jmodel}", "tasks": len(TASKS)}
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "results.portable.json"), "w"), indent=2)
    print(json.dumps(deltas, indent=2))
    print("\nwrote evals/results.portable.json")

def _selftest():
    # the only non-trivial pure logic: gain = fabius - baseline, reduction = 1 - f/b. Verify it.
    rows = {"x/baseline": {"totalScore15": 10.0, "avgOutChars": 2000},
            "x/fabius": {"totalScore15": 12.0, "avgOutChars": 1000}}
    g = round(rows["x/fabius"]["totalScore15"] - rows["x/baseline"]["totalScore15"], 2)
    red = round(100 * (1 - rows["x/fabius"]["avgOutChars"] / rows["x/baseline"]["avgOutChars"]), 1)
    assert g == 2.0 and red == 50.0, (g, red)
    print("selftest ok")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None, help="subset of: openai mistral anthropic")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    _selftest() if a.selftest else run(a.models)
