#!/usr/bin/env bash
# Reproduce the fabius paper (PDF) from source — figures, math, and proofs.
# Requires: python3 + numpy, a headless Google Chrome, and network once (MathJax).
set -euo pipefail
cd "$(dirname "$0")/.."                      # repo root
PAPER=paper

# 1 · self-host MathJax (crisp, offline SVG math in the PDF)
mkdir -p "$PAPER/lib"
if [ ! -f "$PAPER/lib/tex-svg.js" ]; then
  curl -sL https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js -o "$PAPER/lib/tex-svg.js"
fi

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
