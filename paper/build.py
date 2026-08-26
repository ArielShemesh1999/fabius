#!/usr/bin/env python3
"""Assemble the fabius paper: inline the vector figures, math-safe the proofs,
group them into section 4, inject the coherence capstone. Writes fabius-system.html.

    python3 paper/build.py        # from the repo root
    python3 paper/build.py --write-artifact  # after rendering the PDF
"""
import hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
ASSETS = os.path.join(ROOT, "assets")

# Every repository file that can change the rendered PDF. Keep this list in
# lockstep with scripts/verify-paper-artifact.mjs: the verifier owns an
# independent allowlist so an accidentally omitted input cannot bless itself.
ARTIFACT_SOURCES = (
    "assets/architecture.svg",
    "assets/charts/render_figures.py",
    "assets/charts/svgplot.py",
    "assets/fabius-pixel.svg",
    "assets/fig-branching-accuracy.svg",
    "assets/fig-capability-ladder.svg",
    "assets/fig-plan-then-bind.svg",
    "assets/fig-recall-context.svg",
    "assets/fig-reflection-iteration.svg",
    "assets/fig-tool-value-gate.svg",
    "paper/build.py",
    "paper/build.sh",
    "paper/coherence-ext.html",
    "paper/coherence.html",
    "paper/proofs.json",
    "paper/template.html",
)
PDF_FILE = "paper/fabius-as-a-system.pdf"
ARTIFACT_FILE = "paper/artifact.json"


def _sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_entries():
    return [{"file": path, "sha256": _sha256(path)}
            for path in ARTIFACT_SOURCES]


def _source_digest(entries):
    payload = "".join("%s\0%s\n" % (entry["file"], entry["sha256"])
                      for entry in entries).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _paper_version_and_markers():
    template = open(os.path.join(PAPER, "template.html"), encoding="utf-8").read()
    patterns = (
        r"Whitepaper · v(\d+\.\d+\.\d+)",
        r'<div class="meta-row">Version (\d+\.\d+\.\d+)',
        r'<div class="footer-tag">Fabius v(\d+\.\d+\.\d+)',
    )
    versions = [re.search(pattern, template) for pattern in patterns]
    if any(match is None for match in versions):
        raise SystemExit("paper template is missing a canonical version marker")
    values = [match.group(1) for match in versions]
    if len(set(values)) != 1:
        raise SystemExit("paper template version markers disagree: " + ", ".join(values))
    version = values[0]
    return version, [
        "Whitepaper · v" + version,
        "Version " + version,
        "Fabius v" + version,
    ]


def _mathjax_source():
    build = open(os.path.join(PAPER, "build.sh"), encoding="utf-8").read()
    version = re.search(r"^MATHJAX_VERSION=([^\s]+)$", build, re.M)
    digest = re.search(r"^MATHJAX_SHA256=([0-9a-f]{64})$", build, re.M)
    if not version or not digest:
        raise SystemExit("paper/build.sh is missing the pinned MathJax version or digest")
    return {
        "name": "MathJax tex-svg.js",
        "version": version.group(1),
        "sha256": digest.group(1),
    }


def _pdf_page_count(data):
    return len(re.findall(rb"/Type\s*/Page\b", data))


def write_artifact():
    pdf_path = os.path.join(ROOT, PDF_FILE)
    data = open(pdf_path, "rb").read()
    if not data.startswith(b"%PDF-") or not re.search(rb"%%EOF\s*$", data):
        raise SystemExit(PDF_FILE + " is not a complete PDF")
    pages = _pdf_page_count(data)
    if pages < 1:
        raise SystemExit(PDF_FILE + " contains no pages")
    version, markers = _paper_version_and_markers()
    sources = _source_entries()
    artifact = {
        "schema": "fabius-paper-artifact/v1",
        "version": version,
        "file": PDF_FILE,
        "sha256": hashlib.sha256(data).hexdigest(),
        "pages": pages,
        "source_sha256": _source_digest(sources),
        "sources": sources,
        "external_sources": [_mathjax_source()],
        "rendered_markers": markers,
    }
    destination = os.path.join(ROOT, ARTIFACT_FILE)
    temporary = destination + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(artifact, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, destination)
    print("wrote", destination, "(%d sources, %d pages)" % (len(sources), pages))

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
 "fig-capability-ladder": "<b>Figure 1.</b> Capability scales sub-linearly with machinery; fabius adds the smallest sufficient rung and targets the <em>knee</em> (R2), never the tail. The shape fabius's value-of-information threshold predicts — a schematic of the principle, not a fitted curve.",
 "fig-tool-value-gate": "<b>Figure 2.</b> The value-of-information gate (R3): route to the call only when expected error-reduction clears its cost; below threshold is pure overhead. At routing time fabius asks which wrong answer the call prevents.",
 "fig-branching-accuracy": "<b>Figure 3.</b> With an informative evaluator, accuracy peaks at an interior branching factor (R7); with none, more branches only cost depth — the shape fabius's branch-value gate predicts.",
 "fig-plan-then-bind": "<b>Figure 4.</b> Bind-as-you-go grows latency linearly with the number of tool calls; plan-then-bind (R6) stays near-flat by overlapping independent calls; the lines converge when every call depends on the last.",
 "fig-reflection-iteration": "<b>Figure 5.</b> A hard oracle (test, compiler) keeps improving and saturates late; soft self-critique plateaus and dips after two passes (R8). The ~2 soft / ~3 hard caps are fabius's operational heuristics.",
 "fig-recall-context": "<b>Figure 6.</b> Recall rises as the index-matched slice loads, then plateaus; stuffing everything degrades past the context window (R9) — the shape fabius's retrieval-budget gate predicts.",
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
 ("4.6", "Operational heuristics",
    ["R4", "R10", "M8b"],
    {}),
]

BADGE = {"real-math": ("real", "real-math"),
         "qualitative": ("qualitative", "qualitative")}
CARDMOD = {"real-math": "", "qualitative": " qualitative"}

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
                        '<span class="ruletitle">The theorem over twenty-two rules — R11–R13 and M9 in the pipeline</span>'
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
    if sys.argv[1:] == ["--write-artifact"]:
        write_artifact()
    elif sys.argv[1:]:
        raise SystemExit("usage: python3 paper/build.py [--write-artifact]")
    else:
        main()
