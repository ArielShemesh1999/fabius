#!/usr/bin/env python3
"""Render the fabius research figures (F1..F7) to ../*.svg.

Every figure is a CONCEPTUAL shape of a documented principle, not a fabius
measurement. The honesty captions live next to each figure in RESEARCH.md.
Run:  python3 assets/charts/render_figures.py
"""
import os
import numpy as np
from svgplot import plot

OUT = os.path.join(os.path.dirname(__file__), "..")
B, G, R, GR = "#1f6feb", "#2ea44f", "#cf222e", "#8c959f"
def p(name): return os.path.join(OUT, name)

# F1 — capability ladder: capability = 1 - e^(-k·cost); knee where slope < 0.3·slope0
cost = np.linspace(0, 10, 220); cap = 1 - np.exp(-0.55*cost)
knee = np.log(1/0.30)/0.55
plot(p("fig-capability-ladder.svg"),
     "Capability vs machinery — diminishing returns",
     "machinery / cost   (tokens · latency · agent-count)  →", "task capability",
     [{"x": cost, "y": cap, "color": B}], (0, 10), (0, 1.06),
     xticks=[(0, "inline"), (knee, "knee"), (5.5, "+subagent"), (10, "swarm")],
     yticks=[(0, "0"), (0.5, "½"), (1, "1")],
     points=[{"x": knee, "y": 1-np.exp(-0.55*knee), "label": "fabius stops here", "color": G}],
     shade=[{"x0": 6.2, "x1": 10, "color": R, "opacity": 0.07, "label": "over-spend: swarm / long chains"}])

# F2 — tool-call value gate: step at threshold τ on expected error-reduction
dl = np.linspace(-1, 1, 400); keep = (dl >= 0).astype(float)
plot(p("fig-tool-value-gate.svg"),
     "Tool-call value gate  (Toolformer spirit, analogy)",
     "expected error reduction from the call   ΔL = loss(inline) − loss(call)", "route to the call?",
     [{"x": dl, "y": keep, "color": B, "width": 3}], (-1, 1), (-0.06, 1.12),
     xticks=[(-1, "−1"), (0, "τ"), (1, "+1")], yticks=[(0, "inline"), (1, "call")],
     vlines=[{"x": 0, "label": "threshold τ", "color": G}],
     shade=[{"x0": -1, "x1": 0, "color": R, "opacity": 0.09, "label": "pure overhead — answer inline"}])

# F3 — branching factor vs accuracy at fixed budget (informative vs no evaluator)
b = np.linspace(1, 8, 200)
info = 0.25 + 0.95*(1-np.exp(-1.0*(b-1)))*np.exp(-0.16*(b-1))
uninfo = 0.34 - 0.018*(b-1)
bstar = b[int(np.argmax(info))]
plot(p("fig-branching-accuracy.svg"),
     "Branching factor vs accuracy at a fixed budget",
     "branching factor b   (usable depth d ≈ budget / b)", "task accuracy",
     [{"x": b, "y": info, "color": B}, {"x": b, "y": uninfo, "color": GR, "dash": "5 4"}],
     (1, 8), (0, 0.95),
     xticks=[(1, "1"), (bstar, "b*"), (8, "8")], yticks=[(0, "0"), (0.5, "½"), (0.9, ".9")],
     points=[{"x": bstar, "y": info.max(), "label": "informative evaluator", "color": G}],
     notes=[{"x": 4.6, "y": 0.30, "t": "no evaluator → stay single-path (b=1)", "color": GR}])

# F4 — reflection quality vs iteration: hard oracle vs soft self-critique
k = np.arange(1, 7)
hard = np.array([0.45, 0.66, 0.80, 0.87, 0.90, 0.92])
soft = np.array([0.40, 0.60, 0.59, 0.57, 0.56, 0.55])
plot(p("fig-reflection-iteration.svg"),
     "Reflection quality vs iteration  (hard vs soft signal)",
     "iteration / retry  k", "cumulative success",
     [{"x": k, "y": hard, "color": B}, {"x": k, "y": soft, "color": G}],
     (1, 6), (0, 1.0),
     xticks=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6")],
     yticks=[(0, "0"), (0.5, "½"), (1, "1")],
     vlines=[{"x": 2, "label": "soft cap", "color": G}, {"x": 3, "label": "hard cap", "color": B}],
     legend=[("hard oracle (test/compiler) — Reflexion", B), ("soft self-critique — Self-Refine", G)])

# F5 — recall quality vs context tokens loaded (retrieve-slice vs stuff-everything)
x = np.linspace(0, 10, 260)
recall = 0.92*(1-np.exp(-0.95*x))
stuff = recall - np.maximum(x-7, 0)*0.055
infl = 3.0
plot(p("fig-recall-context.svg"),
     "Recall vs context loaded  (retrieve the slice, don't stuff)",
     "context tokens loaded   (index-matched slice → whole directory)", "answer recall quality",
     [{"x": x, "y": recall, "color": B}, {"x": x, "y": stuff, "color": R, "dash": "5 4"}],
     (0, 10), (0, 1.0),
     xticks=[(0, "0"), (infl, "slice"), (7, "window"), (10, "dir")],
     yticks=[(0, "0"), (0.5, "½"), (0.9, ".9")],
     vlines=[{"x": infl, "label": "stop here", "color": G}, {"x": 7, "label": "context limit", "color": GR}],
     legend=[("load matching slice", B), ("stuff everything (degrades)", R)])

# F6 — end-to-end latency: serial chain vs plan-then-bind
n = np.linspace(1, 8, 200)
serial = 0.5 + n*1.0
planbind = 1.8 + 0.06*n
plot(p("fig-plan-then-bind.svg"),
     "Latency: serial chain vs plan-then-bind  (analogy)",
     "number of independent tool / sub-agent calls", "end-to-end latency",
     [{"x": n, "y": serial, "color": R}, {"x": n, "y": planbind, "color": B}],
     (1, 8), (0, 9),
     xticks=[(1, "1"), (4, "4"), (8, "8")], yticks=[(0, "0"), (4, "4"), (8, "8")],
     legend=[("serial: prompt→tool→prompt→tool", R), ("plan-then-bind (parallel)", B)],
     notes=[{"x": 4.4, "y": 1.0, "t": "converge when every call depends on the last", "color": GR}])

# F7 — instruction emphasis: adherence rises, breadth falls; product has a sweet spot
e = np.linspace(0, 10, 260)
adh = 1-np.exp(-0.5*e)
breadth = np.exp(-0.28*e)
prod = adh*breadth
estar = e[int(np.argmax(prod))]
plot(p("fig-emphasis-tradeoff.svg"),
     "Instruction emphasis: adherence vs breadth  (CFG analogy)",
     "instruction emphasis   (say once → repeat / stack / rubric-load)", "normalized",
     [{"x": e, "y": adh, "color": B}, {"x": e, "y": breadth, "color": G},
      {"x": e, "y": prod, "color": GR, "dash": "4 3"}],
     (0, 10), (0, 1.05),
     xticks=[(0, "breadth"), (estar, "sweet spot"), (10, "narrow")],
     yticks=[(0, "0"), (0.5, "½"), (1, "1")],
     vlines=[{"x": estar, "label": "state once", "color": GR}],
     legend=[("constraint adherence", B), ("output breadth / coverage", G), ("product (effectiveness)", GR)])

print("rendered 7 figures to", os.path.abspath(OUT))
