#!/usr/bin/env bash
# Render all D2 diagrams to SVG (source of truth) + PNG (for README embeds).
# D2 renders PNG natively, so no ImageMagick dependency is required.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
mkdir -p out

for src in *.d2; do
    name="${src%.d2}"
    echo ">>> $name"
    d2 --pad 20 "$src" "out/${name}.svg"
    d2 --pad 20 "$src" "out/${name}.png"
done

echo "Done. Outputs in ./out/"
