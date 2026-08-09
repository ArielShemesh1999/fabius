#!/usr/bin/env bash
# Reproduce the fabius paper (PDF) from source — figures, math, and proofs.
# Requires: python3 + numpy, a headless Google Chrome, and network once (MathJax).
set -euo pipefail
cd "$(dirname "$0")/.."                      # repo root
PAPER=paper

# 1 · self-host MathJax (crisp, offline SVG math in the PDF) — pinned + integrity-checked:
#     this file is EXECUTED by headless Chrome to render the shipped PDF, so a floating
#     tag with no hash would let a CDN compromise or upstream release silently change
#     the build. Version and sha256 recorded here; a mismatch deletes the file and fails.
MATHJAX_VERSION=3.2.2
MATHJAX_SHA256=d4295dc33744836935c1399feece5159577b34c5c8ffb9f1c6324cd82e03a882
mkdir -p "$PAPER/lib"
if [ ! -f "$PAPER/lib/tex-svg.js" ]; then
  curl -fsSL "https://cdn.jsdelivr.net/npm/mathjax@${MATHJAX_VERSION}/es5/tex-svg.js" -o "$PAPER/lib/tex-svg.js"
fi
echo "${MATHJAX_SHA256}  $PAPER/lib/tex-svg.js" | shasum -a 256 -c - >/dev/null || {
  rm -f "$PAPER/lib/tex-svg.js"
  echo "MathJax integrity check FAILED — file deleted; re-run to refetch" >&2
  exit 1
}

# 2 · (re)compute the figures  →  assets/fig-*.svg
python3 assets/charts/render_figures.py

# 3 · assemble the HTML — inlines the vector figures, the adversarially-verified
#     proofs (proofs.json), and the coherence capstone (coherence.html)
python3 "$PAPER/build.py"

# 4 · render the PDF via headless Chrome
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=45000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="$PAPER/fabius-as-a-system.pdf" \
  "file://$PWD/$PAPER/fabius-system.html"

echo "wrote $PAPER/fabius-as-a-system.pdf"
