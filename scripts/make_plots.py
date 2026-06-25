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
