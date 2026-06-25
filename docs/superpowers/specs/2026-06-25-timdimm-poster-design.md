# timDIMM SPIE 2026 A0 Poster — Design

**Date:** 2026-06-25
**Author:** Timothy E. Pickering
**Topic:** "Upgraded seeing monitor for the South African Astronomical Observatory"

## Goal

Produce a print-ready A0 (841 × 1189 mm, portrait) poster for SPIE 2026, by
porting the self-contained HTML/CSS → headless-Chrome → PDF framework already
built in `../pypeit/poster`, then re-skinning and re-contenting it for the
timDIMM / SAAO seeing-monitor work.

## Approach

Reuse the pypeit/poster framework verbatim where possible:

- Same render pipeline: `index.html` + `styles.css` + `palette.css`, rendered to
  A0 PDF by `scripts/render.sh` (headless Chrome `--print-to-pdf`), verified A0
  by `scripts/check_pdf.py`, previewed as PNG by `scripts/preview.sh`, all driven
  by `Makefile` targets (`make`, `make poster`, `make check`, `make preview`,
  `make open`, `make clean`).
- Same fonts: Inter (body) + Space Grotesk (display), bundled as woff2.
- Same overall page grid: header → gradient rule → 3 columns → footer.

## Directory structure

```
timdimm/poster/                 # git-initialized (main branch); remote added later by user
  index.html
  styles.css                    # ported from pypeit, lightly adapted
  palette.css                   # regenerated to SAAO/SALT blue theme
  Makefile                      # ported as-is
  scripts/
    render.sh                   # ported as-is
    check_pdf.py                # ported as-is
    preview.sh                  # ported as-is
    fetch_fonts.sh              # ported as-is
    prepare_assets.sh           # rewritten for this poster's logos/photos
    make_plots.py               # NEW — builds result figures from the CSVs
  assets/
    fonts/                      # Inter + Space Grotesk woff2 (copied from pypeit)
    logos/                      # nrf_saao, salt, mmt, ua, spie
    figures/                    # photos + generated plots
  docs/superpowers/specs/       # this design doc
```

## Header & branding

Centered-title header with logos flanking on each side (no software wordmark
exists for this project):

- Center: full title, a short tagline, and the author/affiliation block, all
  center-aligned — content taken verbatim from `abstract.txt`.
  - Title: *Upgraded seeing monitor for the South African Astronomical Observatory*
  - Authors: Timothy E. Pickering (Univ. of Arizona/MMTO), Lisa A. Crause
    (SAAO/SALT), Encarni Romero Colmenero (SAAO/SALT), Rudi Kuhn (SAAO/SALT),
    Nico van der Merwe (SALT)
- Left side: host-institution logos — **NRF/SAAO**, **SALT**.
- Right side: author-affiliation logos — **MMTO**, **University of Arizona**.
- Three-zone header layout: `[left logos] [centered title block] [right logos]`,
  with logos vertically centered against the title block.
- Gradient rule under the header recolored to a blue ramp (from the new palette).

## Palette

SAAO/SALT blue theme. Derive a cohesive ramp programmatically from the SALT
hexagon blue (~cornflower `#2E6DAE`): a primary blue, a darker navy, and 2–3
supporting tints, with the NRF/SALT **red** retained as a sparing highlight
(section-rule accents, figure step markers). Written to `palette.css` keeping the
same variable names the styles already use (`--spec-violet … --spec-red`,
`--ink`, `--bg`, `--bg-alt`, `--muted`, `--hairline`) so `styles.css` needs no
structural change.

## Sections → column layout (3 columns)

- **Column 1**
  - **Abstract** — verbatim from `abstract.txt`.
  - **New Hardware** — mount + DIMM camera replacement, MASS-DIMM → simple DIMM
    mask. Drafted from the abstract with TODO gaps for specifics (exact
    mount/camera models, dates). Photos: `timdimm_closeup`, `timdimm_open_daytime`,
    `timdimm_night`, and the old-mount image for before/after contrast.
- **Column 2**
  - **New Software** — the rewritten control/analysis stack. Drafted from the
    abstract with clearly-marked TODO gaps. Optional repo QR code as a marked TODO
    (URL unknown).
  - **Ant Infestation** — the failure story. **Text is placeholder (TODO: user
    fills in).** Images: `ants_nuc`, `ants_motherboard` (only these two).
- **Column 3**
  - **Results & Comparisons** — the centerpiece; occupies the full right column.
    Holds the four generated figures (below).

## Figures — `make_plots.py`

Built with matplotlib using the project's conda env
(`/Users/tim/conda/envs/...`), styled to the poster palette, saved as PNG into
`assets/figures/`.

### timDIMM seeing (`seeing.csv` — columns: time, target, seeing, airmass, azimuth, exptime)

Rejection: drop non-physical values — sub-arcsec spikes and values above a
~10″ ceiling (exact thresholds tuned during implementation; the data has clear
outliers like 159.67 and 40.23).

1. **Global seeing histogram** — full cleaned distribution with median and
   quartiles (Q1/Q3) marked; median seeing called out numerically.
2. **Monthly violin plots** — per-month seeing distributions across the two years
   of operation, shown as violins (monthly chosen over nightly so the ~24 violins
   read cleanly at A0; revisit if a different binning reads better).

### Comparison vs SALT guider (`SALT_guider_data.csv` — columns: timestamp, ee50, fwhm)

- `fwhm` is already in arcsec, directly comparable to timDIMM `seeing`.
- Timestamps are **LabVIEW format: seconds since 1904-01-01 00:00:00 UTC**
  (per NI LabVIEW timestamp definition). Convert to UTC datetimes on that epoch.
- Rejection: drop negatives, zeros, and non-physical large values.

3. **Overlaid total histograms** — timDIMM seeing vs SALT-guider FWHM, normalized,
   on the same axes.
4. **2×2 seeing-vs-time grid** — four representative nights, one panel each, each
   panel overlaying timDIMM seeing and SALT-guider FWHM time series. Nights chosen
   to be representative (good/median/variable conditions where both datasets have
   coverage).

## Footer

SPIE logo (reused from pypeit) centered, flanked by acknowledgments
(NRF/SAAO, SALT, MMTO / Univ. of Arizona) and the SPIE paper number **14151-100**.

## Assets — sourcing

- **NRF/SAAO** logo ← `2020_HRS_poster.pptx` media `image3.jpeg` (high-res combined NRF | SAAO).
- **SALT** logo ← `2020_HRS_poster.pptx` media `image4.jpeg`.
- **MMTO** logo ← reuse `../pypeit/poster/assets/logos/mmt.png` (or convert
  `Logo_mmt_observatory.pdf`).
- **University of Arizona** logo ← reuse `../pypeit/poster/assets/logos/ua.png`
  (or `UA Logo.png`).
- **SPIE** logo ← reuse `../pypeit/poster/assets/logos/spie.jpg`.
- **Hardware photos** ← `timdimm_closeup.jpeg`, `timdimm_open_daytime.jpeg`,
  `timdimm_night.jpeg`, `timdimm_evening_oldmount.jpg` (others available if needed).
- **Ant photos** ← `ants_nuc.jpeg`, `ants_motherboard.jpeg`.
- `windy_setup.mp4` — **ignored** (cannot embed in print PDF).

## Out of scope / TODO markers left for the user

- Body text for New Hardware and New Software (drafted from abstract; gaps marked).
- **All Ant Infestation body text (placeholder).**
- Software repository URL / QR code.

## Risks

- **SALT timestamp epoch** — confirmed as LabVIEW (1904-01-01 UTC). Verify the
  converted date range overlaps the timDIMM 2024–2026 window before trusting
  per-night alignment for figure 4; if overlap is thin, pick representative nights
  from the overlapping span.
- Outlier thresholds for both datasets need a quick look at the distributions to
  set sensibly; defaults above are starting points.

## Verification

`make` renders `poster.pdf`, asserts the page box is A0, and builds `preview.png`
for visual QC. Success = A0 PDF renders cleanly with all five sections, correct
logos, the four figures, and no broken asset references.
