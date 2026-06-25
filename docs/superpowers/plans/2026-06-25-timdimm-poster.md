# timDIMM SPIE 2026 A0 Poster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a print-ready A0 poster for SPIE paper 14151-100 ("Upgraded seeing monitor for the South African Astronomical Observatory") by porting the `../pypeit/poster` HTML→A0-PDF framework and re-skinning/re-contenting it for the timDIMM work.

**Architecture:** Self-contained static `index.html` + `styles.css` + `palette.css`, rendered to an 841×1189 mm PDF by headless Chrome (`scripts/render.sh`), A0-verified by `scripts/check_pdf.py`, and previewed as PNG by `scripts/preview.sh`, all driven by `Makefile`. Result figures are generated from two CSVs by a new `scripts/make_plots.py`. Logos/photos are staged by `scripts/prepare_assets.sh`.

**Tech Stack:** HTML/CSS, headless Google Chrome, GNU Make, Python (matplotlib/pandas/numpy), ImageMagick (for any vector logo conversion).

## Global Constraints

- Page box MUST be A0 portrait: `@page{size:841mm 1189mm}` and `html,body{width:841mm;height:1189mm}`. `make check` asserts this within 3 mm.
- **All Python uses the `timdimm` conda env:** `/Users/tim/conda/envs/timdimm/bin/python` (Python 3.12; matplotlib 3.11, pandas 3.0, numpy 2.5). The `Makefile` `PYTHON` default points here.
- Fonts: Inter (body) + Space Grotesk (display), bundled woff2 — copied from `../pypeit/poster/assets/fonts/`.
- Palette: SAAO/SALT blue theme; keep the existing CSS variable names (`--spec-violet … --spec-red`, `--ink`, `--bg`, `--bg-alt`, `--muted`, `--hairline`) so `styles.css` needs no variable renames.
- Header: centered title block, host logos (NRF/SAAO, SALT) on the **left**, affiliation logos (MMTO, UArizona) on the **right**.
- Footer carries SPIE paper number **14151-100**.
- Sections, in order: **Abstract, New Hardware, New Software, Ant Infestation, Results & Comparisons**.
- Ant Infestation body text is a **placeholder** (author fills later); it uses only `ants_nuc.jpeg` and `ants_motherboard.jpeg`.
- Author-supplied content gaps are marked inline with `[TODO: …]`; do not invent specifics (mount/camera models, software stack details).
- `windy_setup.mp4` is **ignored** (cannot embed in a print PDF).
- Repo root for the poster: `/Users/tim/Library/Mobile Documents/com~apple~CloudDocs/MMTO/spie/2026/timdimm/poster` (git already initialized on `main`). Source data + raw assets live one level up in `…/timdimm/`. The pypeit poster to port from is at `…/spie/2026/pypeit/poster/`.

Paths below are written relative to the poster repo root unless absolute. Commit with author identity `Timothy E. Pickering <te.pickering@gmail.com>` and the standard `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.

---

## File map

- `Makefile` — build targets (ported; `PYTHON` default changed).
- `scripts/render.sh`, `scripts/check_pdf.py`, `scripts/preview.sh`, `scripts/fetch_fonts.sh` — ported as-is.
- `scripts/prepare_assets.sh` — **rewritten** to stage this poster's logos + photos.
- `scripts/make_plots.py` — **new**; generates the four result figures.
- `palette.css` — **new** SAAO/SALT blue ramp.
- `styles.css` — ported, with header three-zone layout + a few small additions (`.photo-pair`, `.subhead`).
- `index.html` — **new** content: header, five sections, footer.
- `assets/fonts/*` — copied from pypeit.
- `assets/logos/{nrf_saao.png,salt.png,mmt.png,ua.png,spie.jpg}` — staged by prepare_assets.sh.
- `assets/figures/*` — photos (staged) + generated plots.

---

### Task 1: Port the framework scaffold and confirm an A0 render

Stand up the build pipeline with a minimal placeholder page that renders to a valid A0 PDF. This isolates "does the toolchain work" from any content work.

**Files:**
- Create: `Makefile`, `scripts/render.sh`, `scripts/check_pdf.py`, `scripts/preview.sh`, `scripts/fetch_fonts.sh`, `styles.css`, `palette.css`, `index.html`
- Copy: `assets/fonts/{inter-400,inter-500,inter-600,inter-700,spacegrotesk-500,spacegrotesk-700}.woff2`

**Interfaces:**
- Produces: working `make poster` (renders + A0-checks `poster.pdf`) and `make preview` (writes `preview.png`). Later tasks only edit `index.html`, `styles.css`, `palette.css`, `scripts/prepare_assets.sh`, `scripts/make_plots.py`.

- [ ] **Step 1: Copy the ported pipeline files and fonts**

```bash
cd "/Users/tim/Library/Mobile Documents/com~apple~CloudDocs/MMTO/spie/2026/timdimm/poster"
SRC="../../pypeit/poster"
mkdir -p scripts assets/fonts assets/logos assets/figures
cp "$SRC/scripts/render.sh"      scripts/
cp "$SRC/scripts/check_pdf.py"   scripts/
cp "$SRC/scripts/preview.sh"     scripts/
cp "$SRC/scripts/fetch_fonts.sh" scripts/
cp "$SRC/assets/fonts/"*.woff2   assets/fonts/
chmod +x scripts/*.sh
```

- [ ] **Step 2: Write `Makefile` (ported; PYTHON default → timdimm env)**

```makefile
# timDIMM SPIE 2026 poster build
#   make            render the PDF, check it is A0, and build the preview
#   make poster     render poster.pdf and verify the page box is A0
#   make preview    build preview.png (override size: make preview SIZE=2400)
#   make check      assert poster.pdf has an A0 page box
#   make plots      regenerate result figures from the CSVs
#   make assets     stage logos + photos into assets/
#   make open       open the rendered PDF
#   make clean      remove generated artifacts

PYTHON ?= /Users/tim/conda/envs/timdimm/bin/python
SIZE   ?= 1600

SOURCES := index.html styles.css palette.css

.PHONY: all poster render check preview plots assets open clean

all: poster preview

poster: render check

render: poster.pdf

poster.pdf: $(SOURCES)
	bash scripts/render.sh

check: poster.pdf
	$(PYTHON) scripts/check_pdf.py

preview: preview.png

preview.png: $(SOURCES)
	bash scripts/preview.sh $(SIZE)

plots:
	$(PYTHON) scripts/make_plots.py

assets:
	bash scripts/prepare_assets.sh

open: poster.pdf
	open poster.pdf

clean:
	rm -f poster.pdf preview.png preview_full.png
```

- [ ] **Step 3: Write a minimal placeholder `palette.css`** (replaced properly in Task 3)

```css
:root{
  --spec-violet:#122F57; --spec-blue:#1E5A9C; --spec-green:#2E6DAE;
  --spec-yellow:#4A8FCB; --spec-orange:#79AED8; --spec-red:#C8362E;
  --ink:#16202B; --bg:#FFFFFF; --bg-alt:#F4F7FA; --muted:#54606E; --hairline:#DEE5EC;
}
```

- [ ] **Step 4: Write `styles.css`** — copy pypeit's `styles.css` verbatim, then make these edits (header restructure + small additions). Start from the copy:

```bash
cp "../../pypeit/poster/styles.css" styles.css
```

Then replace the `/* header */` block (the rules from `.head-top` through `.authors .affil`) with:

```css
/* header — centered title flanked by logos */
.head-row{display:grid;grid-template-columns:auto 1fr auto;align-items:center;
  gap:20mm;margin-bottom:7mm;}
.logos{display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:10mm;flex:none;}
.logos img{max-height:38mm;max-width:92mm;width:auto;height:auto;object-fit:contain;}
.titleblock{text-align:center;}
.titleblock h1{font-size:62pt;font-weight:700;letter-spacing:-0.5px;margin-inline:auto;}
.tagline{font-size:31pt;color:var(--muted);font-weight:500;margin-top:5mm;}
.authors{font-size:24pt;margin-top:7mm;line-height:1.35;}
.authors sup{font-size:0.62em;}
.authors .affil{display:block;font-size:19pt;color:var(--muted);margin-top:3mm;}
```

Then append these additions to the end of the file:

```css
/* poster-specific additions */
.photo-pair{display:grid;grid-template-columns:1fr 1fr;gap:6mm;margin-top:6mm;}
.photo-pair figure img{height:78mm;width:100%;object-fit:cover;}
.subhead{font-size:30pt;font-weight:700;margin:9mm 0 4mm;
  color:var(--spec-violet);}
.todo{color:var(--spec-red);font-style:italic;}
```

- [ ] **Step 5: Write a minimal placeholder `index.html`** (replaced in Tasks 6–7)

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>timDIMM — SPIE 2026 Poster (14151-100)</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div id="poster">
    <header id="header">
      <div class="head-row">
        <div class="logos"><span class="todo">[logos]</span></div>
        <div class="titleblock"><h1>timDIMM scaffold</h1></div>
        <div class="logos"><span class="todo">[logos]</span></div>
      </div>
    </header>
    <div id="spectrum-rule"></div>
    <main id="columns">
      <section class="col"><section class="section"><h2>Placeholder</h2>
        <p>Scaffold render check.</p></section></section>
      <section class="col"></section>
      <section class="col"></section>
    </main>
    <footer id="footer"><div class="foot-grid"><div>footer</div>
      <span class="todo">[SPIE]</span><div>14151-100</div></div></footer>
  </div>
</body>
</html>
```

- [ ] **Step 6: Render and verify the page box is A0**

Run:
```bash
make poster
```
Expected output ends with:
```
page box: 841.0 x 1189.0 mm
OK: page box is A0
```
(If `render.sh` errors, confirm Chrome exists at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.)

- [ ] **Step 7: Build the preview and eyeball it**

Run:
```bash
make preview
```
Then open `preview.png` and confirm a white A0 page with the placeholder header/section/footer (fonts load, no error boxes).

- [ ] **Step 8: Add a `.gitignore` entry for build artifacts and commit**

```bash
printf '.DS_Store\nposter.pdf\npreview.png\npreview_full.png\n' > .gitignore
git add -A
git commit -m "Scaffold A0 poster framework ported from pypeit/poster"
```
(Append the standard Co-Authored-By trailer to every commit message in this plan.)

---

### Task 2: Stage logos and photos (`prepare_assets.sh`)

**Files:**
- Create: `scripts/prepare_assets.sh`
- Produces (staged): `assets/logos/{nrf_saao.png,salt.png,mmt.png,ua.png,spie.jpg}`, `assets/figures/{timdimm_closeup.jpeg,timdimm_night.jpeg,timdimm_oldmount.jpg,ants_nuc.jpeg,ants_motherboard.jpeg}`

**Interfaces:**
- Consumes: `../2020_HRS_poster.pptx` (media `image3.jpeg`=NRF/SAAO, `image4.jpeg`=SALT), `../../pypeit/poster/assets/logos/{mmt.png,ua.png,spie.jpg}`, and photos in `../`.
- Produces: the asset filenames referenced by `index.html` in Tasks 6–7.

- [ ] **Step 1: Write `scripts/prepare_assets.sh`**

```bash
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
cp "$ROOT/timdimm_closeup.jpeg"          "$FIG/timdimm_closeup.jpeg"
cp "$ROOT/timdimm_night.jpeg"            "$FIG/timdimm_night.jpeg"
cp "$ROOT/timdimm_evening_oldmount.jpg"  "$FIG/timdimm_oldmount.jpg"
cp "$ROOT/ants_nuc.jpeg"                 "$FIG/ants_nuc.jpeg"
cp "$ROOT/ants_motherboard.jpeg"         "$FIG/ants_motherboard.jpeg"

echo "assets staged."
```

- [ ] **Step 2: Run it and verify all files exist**

Run:
```bash
chmod +x scripts/prepare_assets.sh
make assets
ls -la assets/logos assets/figures
```
Expected: the five logos and five photos all present, non-zero size.

- [ ] **Step 3: Spot-check the two extracted logos**

Open `assets/logos/nrf_saao.png` and `assets/logos/salt.png` and confirm they are the NRF/SAAO combined logo and the SALT hexagon (not some other deck image). If the deck's media indices ever differ, re-identify by viewing `…/media/image*.jpeg`.

- [ ] **Step 4: Commit** (logos/photos are binary assets we want tracked)

```bash
git add -A
git commit -m "Stage NRF/SAAO, SALT, MMT, UA, SPIE logos and timDIMM/ant photos"
```

---

### Task 3: SAAO/SALT blue palette

Replace the placeholder palette with a curated blue ramp anchored on the SALT hexagon blue, retaining the NRF/SALT red as a sparing accent. Anchor the primary blue on the actual SALT logo color, then build the ramp around it.

**Files:**
- Modify: `palette.css`

- [ ] **Step 1: Sample the SALT logo's dominant blue (anchor value)**

Run:
```bash
/Users/tim/conda/envs/timdimm/bin/python - <<'PY'
import numpy as np
from PIL import Image
a = np.asarray(Image.open("assets/logos/salt.png").convert("RGB")).reshape(-1,3).astype(int)
mx,mn = a.max(1),a.min(1)
blue = a[(a[:,2]>90)&((mx-mn)>40)&(a[:,2]>=a[:,0])&(a[:,2]>=a[:,1])]
med = np.median(blue,axis=0).astype(int)
print("SALT dominant blue ~ #%02X%02X%02X" % tuple(med))
PY
```
Expected: a cornflower blue near `#2E6DAE` (±, depending on JPEG). Use it as a sanity check for `--spec-green` below; keep the curated values unless it is wildly different.

- [ ] **Step 2: Write the final `palette.css`**

```css
:root{
  --spec-violet:#122F57;   /* deep navy — gradient start */
  --spec-blue:  #1E5A9C;   /* primary blue — section rules, step markers */
  --spec-green: #2E6DAE;   /* SALT hexagon cornflower — card/accent */
  --spec-yellow:#4A8FCB;   /* mid blue */
  --spec-orange:#79AED8;   /* light blue */
  --spec-red:   #C8362E;   /* NRF/SALT red — sparing highlight */
  --ink:#16202B;
  --bg:#FFFFFF;
  --bg-alt:#F4F7FA;
  --muted:#54606E;
  --hairline:#DEE5EC;
}
```

- [ ] **Step 3: Re-render the preview and confirm the blue theme**

Run:
```bash
make preview
```
Open `preview.png`: the gradient rule under the header should read navy→blue→cornflower→light-blue→red (mostly blue with a warm tail), and section underlines should be the primary blue.

- [ ] **Step 4: Commit**

```bash
git add palette.css
git commit -m "Add SAAO/SALT blue palette anchored on the SALT hexagon blue"
```

---

### Task 4: `make_plots.py` — timDIMM seeing figures

Create the figure generator with the two timDIMM-only figures. The "test" for plotting work is a data-sanity run: the script prints cleaning summary stats and must produce non-empty PNGs with a plausible median.

**Files:**
- Create: `scripts/make_plots.py`
- Produces: `assets/figures/seeing_histogram.png`, `assets/figures/seeing_violins_monthly.png`, and printed stats (`MEDIAN=…`, `N_CLEAN=…`).

**Interfaces:**
- Consumes: `../seeing.csv` (columns `time,target,seeing,airmass,azimuth,exptime`).
- Produces: module-level helpers `POSTER_STYLE`, `load_seeing()`, `SEEING_MIN`, `SEEING_MAX` reused by Task 5.

- [ ] **Step 1: Write `scripts/make_plots.py`**

```python
#!/usr/bin/env python
"""Generate timDIMM result figures for the SPIE 2026 poster.

Run with the timdimm conda env:
    /Users/tim/conda/envs/timdimm/bin/python scripts/make_plots.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))          # poster repo root
DATA = os.path.normpath(os.path.join(ROOT, ".."))          # …/timdimm
FIG  = os.path.join(ROOT, "assets", "figures")
os.makedirs(FIG, exist_ok=True)

# palette (mirrors palette.css)
NAVY="#122F57"; BLUE="#1E5A9C"; CORN="#2E6DAE"; LIGHT="#79AED8"; RED="#C8362E"
MUTED="#54606E"; HAIR="#DEE5EC"

# physical seeing window (arcsec) — rejects non-physical spikes/zeros
SEEING_MIN, SEEING_MAX = 0.3, 8.0

POSTER_STYLE = {
    "font.size": 20, "axes.titlesize": 24, "axes.labelsize": 22,
    "xtick.labelsize": 18, "ytick.labelsize": 18, "legend.fontsize": 19,
    "axes.edgecolor": MUTED, "axes.linewidth": 1.2,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "font.family": "DejaVu Sans",
}
plt.rcParams.update(POSTER_STYLE)


def load_seeing():
    """Return cleaned timDIMM seeing as a DataFrame [time(datetime), seeing]."""
    df = pd.read_csv(os.path.join(DATA, "seeing.csv"),
                     usecols=["time", "seeing"])
    df["time"] = pd.to_datetime(df["time"], utc=True)
    n_raw = len(df)
    df = df[(df["seeing"] > SEEING_MIN) & (df["seeing"] < SEEING_MAX)].copy()
    print(f"seeing.csv: {n_raw} raw -> {len(df)} clean "
          f"(kept {df['seeing'].size/n_raw*100:.1f}%)")
    return df


def fig_histogram(df):
    s = df["seeing"]
    med, q1, q3 = s.median(), s.quantile(0.25), s.quantile(0.75)
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.hist(s, bins=np.arange(SEEING_MIN, SEEING_MAX + 0.1, 0.1),
            color=BLUE, edgecolor="white", linewidth=0.3)
    for x, ls, lab in [(med, "-", f"median = {med:.2f}″"),
                       (q1, "--", f"Q1 = {q1:.2f}″"),
                       (q3, "--", f"Q3 = {q3:.2f}″")]:
        ax.axvline(x, color=RED if ls == "-" else NAVY, ls=ls, lw=2.2, label=lab)
    ax.set_xlabel("DIMM seeing (arcsec)")
    ax.set_ylabel("number of measurements")
    ax.set_title("timDIMM seeing distribution (2024–2026)")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=HAIR)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_histogram.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out, f"| MEDIAN={med:.2f} N_CLEAN={len(s)}")
    return med


def fig_violins_monthly(df):
    df = df.copy()
    df["month"] = df["time"].dt.tz_convert(None).dt.to_period("M")
    months = sorted(df["month"].unique())
    data = [df.loc[df["month"] == m, "seeing"].values for m in months]
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    parts = ax.violinplot(data, showmedians=True, widths=0.85)
    for b in parts["bodies"]:
        b.set_facecolor(CORN); b.set_edgecolor(BLUE); b.set_alpha(0.75)
    for key in ("cbars", "cmins", "cmaxes", "cmedians"):
        parts[key].set_color(NAVY); parts[key].set_linewidth(1.6)
    ax.set_xticks(range(1, len(months) + 1))
    ax.set_xticklabels([str(m) for m in months], rotation=60, ha="right")
    ax.set_ylabel("DIMM seeing (arcsec)")
    ax.set_title("Monthly seeing distributions")
    ax.set_ylim(0, SEEING_MAX)
    ax.grid(axis="y", color=HAIR)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_violins_monthly.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out)


def main():
    df = load_seeing()
    fig_histogram(df)
    fig_violins_monthly(df)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it and verify outputs + sanity stats**

Run:
```bash
make plots
```
Expected: prints a "kept ~XX%" cleaning line, `MEDIAN=` between ~1.0 and ~1.6 (raw median was 1.32″), and `wrote …seeing_histogram.png` / `…seeing_violins_monthly.png`. Confirm both files exist:
```bash
ls -la assets/figures/seeing_histogram.png assets/figures/seeing_violins_monthly.png
```

- [ ] **Step 3: Eyeball the two figures**

Open both PNGs. Histogram: single-peaked near ~1.3″ with median/quartile lines labelled. Violins: ~24 monthly violins, readable x labels, no clipping. If labels collide, that's fixed by the existing `rotation=60`.

- [ ] **Step 4: Commit**

```bash
git add scripts/make_plots.py assets/figures/seeing_histogram.png assets/figures/seeing_violins_monthly.png
git commit -m "Add make_plots.py with timDIMM seeing histogram and monthly violins"
```

---

### Task 5: `make_plots.py` — SALT-guider comparison figures

Extend the generator with the two comparison figures. LabVIEW timestamps (seconds since 1904-01-01 UTC) are converted and asserted to land in the expected window (verified: SALT data spans 2026-01-01 → 2026-04-17).

**Files:**
- Modify: `scripts/make_plots.py`
- Produces: `assets/figures/seeing_compare_hist.png`, `assets/figures/seeing_compare_nights.png`

**Interfaces:**
- Consumes: `load_seeing()`, `SEEING_MIN/MAX`, palette constants from Task 4; `../SALT_guider_data.csv` (`timestamp,ee50,fwhm`).
- Produces: figures referenced by `index.html` results section.

- [ ] **Step 1: Add the SALT loader + two plot functions to `make_plots.py`**

Insert these functions after `load_seeing()` (they reuse Task 4's module constants):

```python
LABVIEW_EPOCH = pd.Timestamp("1904-01-01", tz="UTC")


def load_salt():
    """Return cleaned SALT guider data [time(datetime, UTC), fwhm(arcsec)]."""
    df = pd.read_csv(os.path.join(DATA, "SALT_guider_data.csv"),
                     usecols=["timestamp", "fwhm"])
    n_raw = len(df)
    df["time"] = LABVIEW_EPOCH + pd.to_timedelta(df["timestamp"], unit="s")
    df = df[(df["fwhm"] > SEEING_MIN) & (df["fwhm"] < SEEING_MAX)].copy()
    lo, hi = df["time"].min(), df["time"].max()
    print(f"SALT: {n_raw} raw -> {len(df)} clean | span {lo} .. {hi}")
    assert pd.Timestamp("2024-01-01", tz="UTC") < lo < pd.Timestamp("2027-01-01", tz="UTC"), \
        "SALT timestamp conversion outside expected window — check LabVIEW epoch"
    return df


def fig_compare_hist(dimm, salt):
    bins = np.arange(SEEING_MIN, SEEING_MAX + 0.1, 0.1)
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.hist(dimm["seeing"], bins=bins, density=True, color=BLUE, alpha=0.55,
            label=f"timDIMM (n={len(dimm)})")
    ax.hist(salt["fwhm"], bins=bins, density=True, histtype="step", lw=2.6,
            color=RED, label=f"SALT guider (n={len(salt)})")
    ax.set_xlabel("seeing / image FWHM (arcsec)")
    ax.set_ylabel("normalized frequency")
    ax.set_title("timDIMM vs SALT guider (Jan–Apr 2026)")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=HAIR)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_compare_hist.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out)


def _nightly(df, col):
    """Add a 'night' column (local night = UTC date shifted back 12 h)."""
    df = df.copy()
    df["night"] = (df["time"] - pd.Timedelta(hours=12)).dt.date
    return df


def fig_compare_nights(dimm, salt):
    d = _nightly(dimm, "seeing"); s = _nightly(salt, "fwhm")
    # nights where BOTH instruments are well sampled
    cd = d.groupby("night").size(); cs = s.groupby("night").size()
    common = sorted(set(cd[cd > 80].index) & set(cs[cs > 80].index),
                    key=lambda n: min(cd[n], cs[n]), reverse=True)
    nights = sorted(common[:4])
    assert len(nights) == 4, f"need 4 well-sampled common nights, found {len(common)}"
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.0), sharey=True)
    for ax, night in zip(axes.ravel(), nights):
        dn = d[d["night"] == night]; sn = s[s["night"] == night]
        ax.plot(dn["time"].dt.tz_convert(None), dn["seeing"], ".", ms=5,
                color=BLUE, label="timDIMM")
        ax.plot(sn["time"].dt.tz_convert(None), sn["fwhm"], ".", ms=4,
                color=RED, alpha=0.6, label="SALT guider")
        ax.set_title(str(night)); ax.set_ylim(0, SEEING_MAX)
        ax.grid(color=HAIR)
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[0, 0].legend(frameon=False, markerscale=2)
    for ax in axes[:, 0]:
        ax.set_ylabel("arcsec")
    fig.suptitle("Four representative nights: timDIMM seeing vs SALT guider FWHM",
                 fontsize=24)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_compare_nights.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out, "| nights:", nights)
```

- [ ] **Step 2: Update `main()` to also build the comparison figures**

Replace the `main()` body with:

```python
def main():
    dimm = load_seeing()
    fig_histogram(dimm)
    fig_violins_monthly(dimm)
    salt = load_salt()
    fig_compare_hist(dimm, salt)
    fig_compare_nights(dimm, salt)
```

- [ ] **Step 3: Run and verify the epoch assertion + outputs**

Run:
```bash
make plots
```
Expected: a `SALT: … span 2026-01-01 …+00:00 .. 2026-04-17 …+00:00` line (the assertion passes), then `wrote …seeing_compare_hist.png` and `wrote …seeing_compare_nights.png | nights: [4 dates in 2026]`. Confirm files exist:
```bash
ls -la assets/figures/seeing_compare_hist.png assets/figures/seeing_compare_nights.png
```

- [ ] **Step 4: Eyeball both comparison figures**

Overlay histogram: two distributions on a shared axis, both peaking ~1–1.5″, legend with counts. Four-nights grid: 2×2, each panel both series vs time with `HH:MM` x-axis. If a night is sparse for one series, the `>80` sample threshold should already have excluded it; if panels still look thin, raise the threshold in `fig_compare_nights`.

- [ ] **Step 5: Commit**

```bash
git add scripts/make_plots.py assets/figures/seeing_compare_hist.png assets/figures/seeing_compare_nights.png
git commit -m "Add SALT-guider comparison figures (LabVIEW timestamps, overlaid hist + 4-night grid)"
```

---

### Task 6: Header and footer

Build the real header (centered title flanked by logos) and footer (SPIE logo + paper number). Done before the column content so the page frame is locked.

**Files:**
- Modify: `index.html` (header + footer)

- [ ] **Step 1: Replace the `<header>` block in `index.html`**

```html
    <header id="header">
      <div class="head-row">
        <div class="logos logos-left">
          <img src="assets/logos/nrf_saao.png" alt="NRF / SAAO">
          <img src="assets/logos/salt.png" alt="Southern African Large Telescope">
        </div>
        <div class="titleblock">
          <h1>Upgraded seeing monitor for the South African Astronomical Observatory</h1>
          <p class="tagline">A 2024 hardware &amp; software refresh of the SAAO automated DIMM
            <!-- TODO: confirm/adjust tagline --></p>
          <p class="authors">
            T.&nbsp;E.&nbsp;Pickering<sup>1,2</sup>, L.&nbsp;A.&nbsp;Crause<sup>3</sup>,
            E.&nbsp;Romero&nbsp;Colmenero<sup>3</sup>, R.&nbsp;Kuhn<sup>3</sup>,
            N.&nbsp;van&nbsp;der&nbsp;Merwe<sup>4</sup>
            <span class="affil"><sup>1</sup>Univ.&nbsp;of&nbsp;Arizona&nbsp;
            <sup>2</sup>MMTO&nbsp; <sup>3</sup>SAAO&nbsp;/&nbsp;SALT&nbsp;
            <sup>4</sup>SALT</span>
          </p>
        </div>
        <div class="logos logos-right">
          <img src="assets/logos/mmt.png" alt="MMT Observatory">
          <img src="assets/logos/ua.png" alt="University of Arizona">
        </div>
      </div>
    </header>
```

- [ ] **Step 2: Replace the `<footer>` block in `index.html`**

```html
    <footer id="footer">
      <div class="foot-grid">
        <div>
          <b>Acknowledgments:</b> South African Astronomical Observatory (SAAO) &amp;
          Southern African Large Telescope (SALT). timDIMM upgrade by the authors.
        </div>
        <img class="spie-logo" src="assets/logos/spie.jpg" alt="SPIE">
        <div>
          <b>SPIE&nbsp;Paper&nbsp;14151-100</b><br>
          Astronomical Telescopes&nbsp;+&nbsp;Instrumentation 2026
        </div>
      </div>
    </footer>
```

- [ ] **Step 3: Render preview and verify header/footer**

Run:
```bash
make preview
```
Open `preview.png`: title centered between NRF/SAAO+SALT (left) and MMT+UA (right); logos vertically centered and not overflowing; footer shows SPIE logo centered with paper number at right. Title should fit on ≤3 lines — if it crowds the logos, drop `.titleblock h1` font-size a couple pt in `styles.css`.

- [ ] **Step 4: Commit**

```bash
git add index.html styles.css
git commit -m "Build poster header (centered title, flanking logos) and footer (14151-100)"
```

---

### Task 7: Column content — the five sections

Fill the three columns with the five sections. Abstract is verbatim; Hardware/Software are drafted from the abstract with `[TODO:]` gaps; Ant Infestation is a placeholder; Results embeds the four generated figures.

**Files:**
- Modify: `index.html` (`<main id="columns">`)

- [ ] **Step 1: Replace `<main id="columns">…</main>` with the full three-column content**

```html
    <main id="columns">
      <section class="col" id="col1">
        <section class="section">
          <h2>Abstract</h2>
          <!-- verbatim from abstract.txt; note "the was developed" typo retained -->
          <p>Automated measurement of atmospheric seeing began at the South African
          Astronomical Observatory (SAAO) in March 2010. The original equipment
          consisted of a MASS-DIMM mated to a 25&nbsp;cm Meade LX200 with the DIMM
          channel feeding a high-speed (200+&nbsp;fps) IEEE1394 camera. That hardware
          eventually succumbed to the ravages of time. The interfaces to the MASS and
          DIMM camera became obsolete and difficult to support. The key failure,
          though, was that the mount could no longer point or track well enough to be
          useful anymore.</p>
          <p>In 2024 the system was upgraded significantly and returned to routine
          operation. The DIMM camera and mount were replaced with newer, more
          performant options and the MASS-DIMM was replaced with a simple DIMM mask.
          We present results from the first two years of renewed operation, compared
          to seeing measurements from other sources at the SAAO site, and describe the
          updated software developed for this system.</p>
        </section>
        <section class="section">
          <h2>New Hardware</h2>
          <p>The original 2010 system paired a <b>MASS-DIMM</b> with a 25&nbsp;cm Meade
          LX200; the DIMM channel fed a 200+&nbsp;fps IEEE1394 camera. Two failures
          ended its life: the MASS and DIMM camera interfaces became obsolete and
          unsupportable and — decisively — the mount could no longer point or track
          reliably.</p>
          <p>The 2024 rebuild keeps the DIMM technique but modernizes the system:</p>
          <ul>
            <li><b>Mount</b> — <span class="todo">[TODO: new mount make/model]</span>
            replacing the failed LX200.</li>
            <li><b>DIMM camera</b> — <span class="todo">[TODO: model, frame rate,
            interface]</span> replacing the IEEE1394 camera.</li>
            <li><b>DIMM mask</b> — the MASS-DIMM was retired for a <b>simple
            two-aperture DIMM mask</b>, simplifying the optics and upkeep.</li>
            <li><span class="todo">[TODO: OTA reused or replaced? aperture?]</span></li>
          </ul>
          <figure>
            <img src="assets/figures/timdimm_closeup.jpeg" alt="Rebuilt timDIMM instrument">
            <figcaption>The rebuilt timDIMM.
            <span class="todo">[TODO: name the mount &amp; camera]</span></figcaption>
          </figure>
          <div class="photo-pair">
            <figure>
              <img src="assets/figures/timdimm_night.jpeg" alt="timDIMM at night">
              <figcaption>In routine night operation.</figcaption>
            </figure>
            <figure>
              <img src="assets/figures/timdimm_oldmount.jpg" alt="Previous LX200 setup">
              <figcaption>The previous LX200-based setup.</figcaption>
            </figure>
          </div>
        </section>
      </section>

      <section class="col" id="col2">
        <section class="section">
          <h2>New Software</h2>
          <p>The upgrade included a substantial rewrite of the acquisition and
          analysis software <span class="todo">[TODO: confirm stack — Python]</span>.
          Key elements:</p>
          <ul>
            <li><b>Acquisition</b> — camera control and frame capture
            <span class="todo">[TODO: driver/library]</span>.</li>
            <li><b>DIMM reduction</b> — differential image motion &rarr; seeing
            <span class="todo">[TODO: cadence / real-time?]</span>.</li>
            <li><b>Telescope control</b> — pointing, tracking, target selection on
            the new mount <span class="todo">[TODO: details]</span>.</li>
            <li><b>Logging &amp; dissemination</b> — seeing values stored and
            <span class="todo">[TODO: how published to operations]</span>.</li>
          </ul>
          <!-- TODO: optional software-repo QR:
          <figure class="repo-qr">
            <img src="assets/figures/qr_repo.png" alt="Software repository">
            <figcaption><b>Code:</b> [TODO: repo URL]</figcaption>
          </figure> -->
        </section>
        <section class="section">
          <h2>Ant Infestation</h2>
          <!-- TODO: author to write the ant-infestation narrative -->
          <p class="todo">[TODO: Ant infestation story — to be written by the author.]</p>
          <div class="photo-pair">
            <figure>
              <img src="assets/figures/ants_nuc.jpeg" alt="Ants inside the control computer">
              <figcaption class="todo">[TODO: caption — ants in the NUC]</figcaption>
            </figure>
            <figure>
              <img src="assets/figures/ants_motherboard.jpeg" alt="Ants on the motherboard">
              <figcaption class="todo">[TODO: caption — ants on the motherboard]</figcaption>
            </figure>
          </div>
        </section>
      </section>

      <section class="col" id="col3">
        <section class="section">
          <h2>Results &amp; Comparisons</h2>
          <p>Two years of renewed operation (Apr&nbsp;2024&nbsp;&ndash;&nbsp;Jun&nbsp;2026)
          give a median DIMM seeing of <b>~1.3&#8243;</b>
          <span class="todo">[verify against histogram callout]</span>.</p>
          <figure>
            <img src="assets/figures/seeing_histogram.png" alt="timDIMM seeing distribution">
            <figcaption>Global timDIMM seeing distribution; dashed lines mark the
            median and interquartile range.</figcaption>
          </figure>
          <figure>
            <img src="assets/figures/seeing_violins_monthly.png" alt="Monthly seeing violins">
            <figcaption>Monthly seeing distributions across the campaign, showing
            seasonal variation.</figcaption>
          </figure>
          <h3 class="subhead">Comparison with the SALT guider</h3>
          <figure>
            <img src="assets/figures/seeing_compare_hist.png" alt="timDIMM vs SALT histograms">
            <figcaption>Normalized distributions of timDIMM DIMM seeing and SALT
            guider image FWHM (both arcsec) over the Jan&ndash;Apr&nbsp;2026 overlap.</figcaption>
          </figure>
          <figure>
            <img src="assets/figures/seeing_compare_nights.png" alt="Four representative nights">
            <figcaption>Four representative nights: timDIMM seeing and SALT guider
            FWHM vs time. <span class="todo">[TODO: agreement/offset commentary]</span></figcaption>
          </figure>
        </section>
      </section>
    </main>
```

- [ ] **Step 2: Render preview and verify all five sections**

Run:
```bash
make preview
```
Open `preview.png` and confirm: col 1 = Abstract + New Hardware (with 3 photos); col 2 = New Software + Ant Infestation (2 ant photos, placeholder text in red italic); col 3 = Results with all four figures present (no broken-image boxes). Check nothing overflows the page bottom.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "Add five poster sections (abstract verbatim, drafted hardware/software, ant placeholder, results figures)"
```

---

### Task 8: Full render, balance pass, and final verification

**Files:**
- Modify (as needed for balance only): `index.html`, `styles.css`

- [ ] **Step 1: Full build (render + A0 check + preview)**

Run:
```bash
make clean && make
```
Expected: `OK: page box is A0` and a written `preview.png`.

- [ ] **Step 2: Balance pass against the full preview**

Open `preview.png` at full size and check, in order:
1. No section runs off the bottom of the page; columns are reasonably balanced in height.
2. Figures are legible at A0 (axis labels not tiny); the four result plots fill column 3 without crowding.
3. Header logos are vertically centered and similar visual weight; title not colliding with logos.
4. All `[TODO:]` markers render in red italic (so the author can find them) — confirm they're the only red text besides intended accents.

Make only spacing/sizing adjustments here: column `gap` (`styles.css` `.col`), figure `max-height`, or `.titleblock h1` font-size. If column 1 or 2 is much taller than 3, consider moving New Software above is not allowed (order is fixed) — instead tighten figure heights. Re-run `make preview` after each tweak.

- [ ] **Step 3: Confirm the A0 PDF one more time and open it**

Run:
```bash
make check && make open
```
Expected: `OK: page box is A0`; the PDF opens. Visually confirm fonts embedded and images crisp.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "Final balance pass; A0 poster renders cleanly with all sections and figures"
```

---

## Self-Review

**Spec coverage:**
- Port framework / pipeline / fonts → Task 1. ✓
- Directory structure → Task 1 + file map. ✓
- Centered-title header, host logos left / affiliation logos right → Task 6. ✓
- SAAO/SALT blue palette (anchored on SALT blue) → Task 3. ✓
- Abstract (verbatim) → Task 7. ✓
- New Hardware (drafted + TODO, hardware photos) → Task 7. ✓
- New Software (drafted + TODO, optional repo QR) → Task 7. ✓
- Ant Infestation (placeholder text, ants_nuc + ants_motherboard only) → Task 7. ✓
- Results & Comparisons: global histogram (median/quartiles), monthly violins → Task 4; overlaid comparison histograms, 2×2 four-night grid → Task 5; embedded in col 3 → Task 7. ✓
- Figures from CSVs, outlier rejection, FWHM in arcsec, LabVIEW (1904 UTC) timestamps → Tasks 4–5. ✓
- Footer with SPIE logo + paper number 14151-100 → Task 6. ✓
- Asset sourcing (NRF/SAAO + SALT from HRS deck; MMT/UA/SPIE from pypeit; named photos; mp4 ignored) → Task 2. ✓
- timdimm conda env for all Python → Global Constraints + Makefile PYTHON default. ✓
- A0 verification → Task 1 + Task 8. ✓

**Placeholder scan:** The only `[TODO:]` markers are author-content gaps the spec explicitly defers (hardware/software specifics, ant story, captions, tagline, repo URL). These are rendered as visible red text by design, not plan placeholders. No build step is left unspecified.

**Type consistency:** `load_seeing()`/`load_salt()` return DataFrames with `time`/`seeing` and `time`/`fwhm`; `SEEING_MIN/MAX` and palette constants defined in Task 4 are reused in Task 5; figure filenames (`seeing_histogram.png`, `seeing_violins_monthly.png`, `seeing_compare_hist.png`, `seeing_compare_nights.png`) match between Tasks 4/5 and the `index.html` `<img>` references in Task 7. Logo/photo filenames staged in Task 2 match the `<img>` references in Tasks 6–7.
