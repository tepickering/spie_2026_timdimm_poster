#!/usr/bin/env bash
# Stage logos + photos for the timDIMM poster with semantic names.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=".."                       # …/timdimm
PYPEIT="../../pypeit/poster"    # reuse MMT / UA / SPIE logos
LOGO="assets/logos"; FIG="assets/figures"
mkdir -p "$LOGO" "$FIG"

# --- host-institution logos from the 2020 HRS deck ---
SCRATCH="$(mktemp -d)"; cp "$ROOT/2020_HRS_poster.pptx" "$SCRATCH/deck.pptx"
( cd "$SCRATCH" && unzip -o -q deck.pptx -d deck )
cp "$SCRATCH/deck/ppt/media/image3.jpeg" "$LOGO/nrf_saao.png"   # NRF | SAAO
cp "$SCRATCH/deck/ppt/media/image4.jpeg" "$LOGO/salt.png"       # SALT hexagon
rm -rf "$SCRATCH"

# --- affiliation + SPIE logos reused from the pypeit poster ---
cp "$PYPEIT/assets/logos/mmt.png"  "$LOGO/mmt.png"
cp "$PYPEIT/assets/logos/ua.png"   "$LOGO/ua.png"
cp "$PYPEIT/assets/logos/spie.jpg" "$LOGO/spie.jpg"

# --- photos ---
cp "$ROOT/timdimm_and_monet.jpg"         "$FIG/timdimm_and_monet.jpg"
cp "$ROOT/timdimm_closeup.jpeg"          "$FIG/timdimm_closeup.jpeg"
cp "$ROOT/timdimm_open_daytime.jpeg"     "$FIG/timdimm_open_daytime.jpeg"
cp "$ROOT/tim_and_nico.jpg"              "$FIG/tim_and_nico.jpg"
cp "$ROOT/ants_nuc.jpeg"                 "$FIG/ants_nuc.jpeg"
cp "$ROOT/ants_motherboard.jpeg"         "$FIG/ants_motherboard.jpeg"

echo "assets staged."
