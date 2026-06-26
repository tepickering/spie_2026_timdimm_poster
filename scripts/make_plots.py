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
    med_d = dimm["seeing"].median()
    med_s = salt["fwhm"].median()
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.hist(dimm["seeing"], bins=bins, density=True, color=BLUE, alpha=0.55,
            label=f"DIMM (n={len(dimm)}, median {med_d:.2f}″)")
    ax.hist(salt["fwhm"], bins=bins, density=True, histtype="step", lw=2.6,
            color=RED, label=f"SALT guider (n={len(salt)}, median {med_s:.2f}″)")
    ax.axvline(med_d, color=NAVY, ls="--", lw=2.2)
    ax.axvline(med_s, color=RED, ls="--", lw=2.2)
    ax.set_xlabel("seeing / image FWHM (arcsec)")
    ax.set_ylabel("normalized frequency")
    ax.set_title("DIMM vs SALT guider (Jan–Apr 2026)")
    ax.set_xlim(0, 5)
    ax.legend(frameon=False)
    ax.grid(axis="y", color=HAIR)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_compare_hist.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out, f"| DIMM median={med_d:.2f} SALT median={med_s:.2f}")


def _nightly(df):
    """Add a 'night' column (local night = UTC date shifted back 12 h)."""
    df = df.copy()
    df["night"] = (df["time"] - pd.Timedelta(hours=12)).dt.date
    return df


def fig_compare_nights(dimm, salt):
    import matplotlib.dates as mdates
    d = _nightly(dimm); s = _nightly(salt)
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
                color=BLUE, label="DIMM")
        ax.plot(sn["time"].dt.tz_convert(None), sn["fwhm"], ".", ms=4,
                color=RED, alpha=0.6, label="SALT guider")
        ax.set_title(str(night)); ax.set_ylim(0, 5)
        # fixed evening-to-morning window, 18:00–04:30 UT
        ax.set_xlim(pd.Timestamp(night) + pd.Timedelta(hours=18),
                    pd.Timestamp(night) + pd.Timedelta(days=1, hours=4.5))
        ax.grid(color=HAIR)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[0, 0].legend(frameon=False, markerscale=2)
    for ax in axes[:, 0]:
        ax.set_ylabel("arcsec")
    for ax in axes[1, :]:
        ax.set_xlabel("time (UT)")
    fig.suptitle("Four representative nights: DIMM seeing vs SALT guider FWHM",
                 fontsize=24)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_compare_nights.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out, "| nights:", nights)


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
    ax.set_title("DIMM seeing distribution (2024–2026)")
    ax.set_xlim(0, 5)
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
    parts = ax.violinplot(data, showmedians=True, showextrema=False, widths=0.85)
    for b in parts["bodies"]:
        b.set_facecolor(CORN); b.set_edgecolor(BLUE); b.set_alpha(0.75)
    parts["cmedians"].set_color(NAVY); parts["cmedians"].set_linewidth(1.6)
    ax.set_xticks(range(1, len(months) + 1))
    ax.set_xticklabels([str(m) for m in months], rotation=60, ha="right")
    ax.set_ylabel("DIMM seeing (arcsec)")
    ax.set_title("Monthly seeing distributions")
    ax.set_ylim(0, 5)
    ax.grid(axis="y", color=HAIR)
    fig.tight_layout()
    out = os.path.join(FIG, "seeing_violins_monthly.png")
    fig.savefig(out, dpi=200); plt.close(fig)
    print("wrote", out)


def main():
    dimm = load_seeing()
    fig_histogram(dimm)
    fig_violins_monthly(dimm)
    salt = load_salt()
    fig_compare_hist(dimm, salt)
    fig_compare_nights(dimm, salt)


if __name__ == "__main__":
    main()
