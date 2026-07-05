#!/usr/bin/env python3
"""Assemble the fabius paper: inline the vector figures, math-safe the proofs,
group them into section 4, inject the coherence capstone. Writes fabius-system.html.

    python3 paper/build.py        # from the repo root
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
ASSETS = os.path.join(ROOT, "assets")

# ---- math-safe: literal <,> inside \(...\) / \[...\] break the HTML parser ----
_INLINE = re.compile(r"\\\(.*?\\\)", re.S)
_DISPLAY = re.compile(r"\\\[.*?\\\]", re.S)
def _fix(span):
    s = span.group(0)
    return s.replace("<", r"\lt ").replace(">", r"\gt ")
def math_safe(html):
    html = _DISPLAY.sub(_fix, html)
    html = _INLINE.sub(_fix, html)
    return html

# ---- inline an svg file, stripping xml prologue ----
def load_svg(name, cls=None):
    raw = open(os.path.join(ASSETS, name + ".svg")).read()
    raw = re.sub(r"<\?xml.*?\?>\s*", "", raw, flags=re.S)
    raw = re.sub(r"<!DOCTYPE.*?>\s*", "", raw, flags=re.S)
    raw = raw.strip()
    if cls:
        raw = re.sub(r"<svg\b", '<svg class="%s"' % cls, raw, count=1)
    return raw

# ---- figures for section 4 (Figure N + honesty caption) ----
FIGCAP = {
 "fig-capability-ladder": "<b>Figure 1 — analogy.</b> Capability scales sub-linearly with machinery; fabius adds the smallest sufficient rung and targets the <em>knee</em> (R2), never the tail. The diminishing-returns shape is asserted directionally by the efficiency surveys — this exact curve is not fitted to fabius.",
 "fig-tool-value-gate": "<b>Figure 2 — analogy.</b> The value-of-information gate (R3): route to the call only when expected error-reduction clears its cost; below threshold is pure overhead. Toolformer computes its loss-reduction filter at training time, which fabius lacks at routing time — so it asks instead which wrong answer the call prevents.",
 "fig-branching-accuracy": "<b>Figure 3 — illustrative.</b> With an informative evaluator, accuracy peaks at an interior branching factor (R7); with none, more branches only cost depth. Tree of Thoughts demonstrates the evaluator-gated benefit empirically but does not publish this curve.",
 "fig-plan-then-bind": "<b>Figure 4 — analogy.</b> Bind-as-you-go grows latency linearly with the number of tool calls; plan-then-bind (R6) stays near-flat by overlapping independent calls. The flat curve is Chain-of-Abstraction's prediction, unmeasured in fabius's multi-agent fan-out; the lines converge when every call depends on the last.",
 "fig-reflection-iteration": "<b>Figure 5 — empirical shape.</b> A hard oracle (test, compiler) keeps improving and saturates late; soft self-critique plateaus and dips after two passes (R8). The curves are Reflexion's and Self-Refine's own reported finding; the ~2 soft / ~3 hard caps are fabius's operational heuristics, not derived constants.",
 "fig-recall-context": "<b>Figure 6 — illustrative.</b> Recall rises as the index-matched slice loads, then plateaus; stuffing everything degrades past the context window (R9). MemGPT shows paging beats stuffing once the corpus exceeds the window; the exact inflection is conceptual.",
 "fig-emphasis-tradeoff": "<b>Figure 7 — CFG analogy.</b> As instruction emphasis rises, constraint-adherence increases while output breadth falls; their product peaks at modest emphasis (R10). Classifier-free guidance measures this fidelity/diversity trade in image sampling — never about prompts or agents.",
}

def figure_html(name):
    return ('<figure>%s<figcaption>%s</figcaption></figure>'
            % (load_svg(name), FIGCAP[name]))

# ---- section 4 layout: (heading, [rules in order], {rule: figure-after-proof}) ----
GROUPS = [
 ("4.1", "Routing, and the value of spending",
    ["R1", "R2", "R3", "M1", "R7"],
    {"R2": "fig-capability-ladder", "R3": "fig-tool-value-gate", "R7": "fig-branching-accuracy"}),
 ("4.2", "Execution and scheduling",
    ["R5", "R6", "M2"],
    {"R6": "fig-plan-then-bind"}),
 ("4.3", "Refinement, and knowing when to stop",
    ["R8", "M3", "M4"],
    {"R8": "fig-reflection-iteration"}),
 ("4.4", "Learning and reuse",
    ["M5", "M6"],
    {}),
 ("4.5", "Memory as information theory",
    ["R9", "R9b", "R9c", "M7", "M8", "M8c"],
    {"R9": "fig-recall-context"}),
 ("4.6", "The analogies, stated honestly",
    ["R4", "R10", "M8b"],
    {"R10": "fig-emphasis-tradeoff"}),
]

BADGE = {"real-math": ("real", "real-math"), "analogy": ("analogy", "analogy"),
         "qualitative": ("qualitative", "qualitative")}
CARDMOD = {"real-math": "", "analogy": " analogy", "qualitative": " qualitative"}

def card(p):
    bmod, blabel = BADGE.get(p["class"], ("real", "real-math"))
    return ('<div class="rulecard%s">'
            '<div class="rulehead"><span class="ruleid">%s</span>'
            '<span class="ruletitle">%s</span>'
            '<span class="badge %s">%s</span></div>%s</div>'
            % (CARDMOD.get(p["class"], ""), p["rule"], p["title"],
               bmod, blabel, math_safe(p["html"])))

def build_math_section(proofs):
    by = {p["rule"]: p for p in proofs}
    out = []
    for num, title, rules, figs in GROUPS:
        out.append('<h3>%s · %s</h3>' % (num, title))
        for r in rules:
            if r not in by:
                raise SystemExit("missing proof for rule " + r)
            out.append(card(by[r]))
            if r in figs:
                out.append(figure_html(figs[r]))
    return "\n".join(out)

def main():
    proofs = json.load(open(os.path.join(PAPER, "proofs.json")))
    coherence = math_safe(open(os.path.join(PAPER, "coherence.html")).read().strip())
    html = open(os.path.join(PAPER, "template.html")).read()

    # inline the two template figures
    html = html.replace("<!--FIG:fabius-pixel-->", load_svg("fabius-pixel", cls="wordmark"))
    html = html.replace("<!--FIG:architecture-->", load_svg("architecture"))

    # section 4.7 extension cards + section 5 coherence extension
    by = {p["rule"]: p for p in proofs}
    ext_cards = "\n".join(card(by[r]) for r in ["R11", "R12", "R13", "M9"])
    html = html.replace("<!--MATH_EXT-->", ext_cards)
    coh_ext = math_safe(open(os.path.join(PAPER, "coherence-ext.html")).read().strip())
    html = html.replace("<!--COHERENCE_EXT-->",
                        '<div class="rulecard"><div class="rulehead">'
                        '<span class="ruleid">Extension</span>'
                        '<span class="ruletitle">R11–R13 and M9 join the pipeline — the theorem over twenty-two rules</span>'
                        '<span class="badge real">extension</span></div>%s</div>' % coh_ext)

    # section 4 + coherence capstone
    html = html.replace("<!--MATH_SECTION-->", build_math_section(proofs))
    html = html.replace("<!--COHERENCE-->",
                        '<div class="rulecard"><div class="rulehead">'
                        '<span class="ruleid">Theorem</span>'
                        '<span class="ruletitle">The policy is one coherent decision system</span>'
                        '<span class="badge real">capstone</span></div>%s</div>' % coherence)

    # sanity: no markers left
    leftover = re.findall(r"<!--(FIG:[^>]+|MATH_SECTION|MATH_EXT|COHERENCE|COHERENCE_EXT)-->", html)
    if leftover:
        raise SystemExit("unfilled markers: " + ", ".join(leftover))

    out = os.path.join(PAPER, "fabius-system.html")
    open(out, "w").write(html)
    print("wrote", out, "(%d KB)" % (len(html) // 1024))
    print("proofs inlined:", len(proofs), "| figures:", 2 + sum(len(g[3]) for g in GROUPS))

if __name__ == "__main__":
    main()
