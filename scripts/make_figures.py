#!/usr/bin/env python3
"""
Generate every data figure in the thesis from the stored run outputs.

Reads the parquet files of the audit repository at ~/Code/VLM_Audit
(outputs_bunya/) plus planning/ledger_v2.json, and writes vector PDFs into
figures/, named after the LaTeX label without the "fig:" prefix.

Nothing here estimates or rounds a published number: every value is recomputed
from the stored runs. The permutation null (s1-perm) is a full enumeration of
all C(22,6) = 74,613 keying assignments, so it is exact rather than sampled.

Usage:
    python scripts/make_figures.py [--audit-repo PATH] [--only NAME ...]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy import stats

# --------------------------------------------------------------------------
# Style. Validated categorical palette, first three slots, which are the only
# three that clear the all-pairs colour-vision-deficiency floor in both modes.
# --------------------------------------------------------------------------
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
GRID = "#dddcd8"
NEUTRAL = "#f0efec"

# Five models at five parameter counts. Colour carries the family, which is
# the comparison the design is built on, and the three validated categorical
# slots are enough because there are only two families plus a neutral.
MODELS = {
    "qwen2b": ("Qwen-2B", AQUA),
    "qwen7b": ("Qwen-7B", AQUA),
    "llama11b": ("Llama-11B", BLUE),
    "qwen72b": ("Qwen-72B", AQUA),
    "llama90b": ("Llama-90B", BLUE),
}
# Ordered by parameter count, which is the x axis of every size figure.
SIZE_ORDER = ["qwen2b", "qwen7b", "llama11b", "qwen72b", "llama90b"]
PARAMS_B = {"qwen2b": 2, "qwen7b": 7, "llama11b": 11, "qwen72b": 72, "llama90b": 90}
FAMILY = {"qwen2b": "qwen", "qwen7b": "qwen", "qwen72b": "qwen",
          "llama11b": "llama", "llama90b": "llama"}
FAMILY_LABEL = {"qwen": "Qwen2-VL", "llama": "Llama-3.2-Vision"}
FAMILY_COLOUR = {"qwen": AQUA, "llama": BLUE}
# Subscale series for the gender gap: two real series plus the combined score.
SUBSCALE = {"BS": ("benevolent", BLUE), "HS": ("hostile", ORANGE),
            "all": ("combined", MUTED)}
PRODUCTION = ["llama90b", "qwen72b"]

CONDITION_LABEL = {
    "text_only": "no image",
    "gray_patch": "grey patch",
    "noise": "noise",
}
# Short forms for axes where the full labels collide; the caption spells them out.
CONDITION_SHORT = {"text_only": "none", "gray_patch": "grey", "noise": "noise"}
CONDITION_ORDER = ["text_only", "gray_patch", "noise"]

# Diverging ramp: two hues with a neutral grey midpoint, never a hue at zero.
DIVERGING = LinearSegmentedColormap.from_list(
    "blue_grey_red", ["#0d366b", BLUE, "#cde2fb", NEUTRAL, "#f6c9c9", "#e34948", "#8c2020"]
)

TEXTWIDTH_IN = 6.30  # a4paper with 25 mm margins


def set_style() -> None:
    serif = [f for f in ("Latin Modern Roman", "CMU Serif", "DejaVu Serif")
             if any(f == x.name for x in mpl.font_manager.fontManager.ttflist)]
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
        "font.family": "serif",
        "font.serif": serif or ["DejaVu Serif"],
        "font.size": 9,
        "axes.titlesize": 9.5,
        "axes.labelsize": 9,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.6,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "legend.frameon": False,
        "lines.linewidth": 1.4,
    })


def finish(fig, name: str, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.pdf"
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
class Data:
    def __init__(self, audit: Path, ledger: Path):
        self.audit = audit
        o = audit / "outputs_bunya"
        self.p1 = {
            "qwen2b": pd.read_parquet(o / "phase1/qwen_2b.parquet"),
            "qwen7b": pd.read_parquet(o / "phase1/qwen_7b.parquet"),
            "llama11b": pd.read_parquet(o / "phase1/llama_dev.parquet"),
            "qwen72b": pd.read_parquet(o / "phase1/qwen.parquet"),
            "llama90b": pd.read_parquet(o / "phase1/llama.parquet"),
        }
        # Phase 1B: the same inventory against 40 real faces.
        self.p1b = {
            "qwen2b": pd.read_parquet(o / "phase1b/qwen_2b_cfd.parquet"),
            "qwen7b": pd.read_parquet(o / "phase1b/qwen_7b_cfd.parquet"),
            "llama11b": pd.read_parquet(o / "phase1b/llama_dev_cfd.parquet"),
            "qwen72b": pd.read_parquet(o / "phase1b/qwen_cfd.parquet"),
            "llama90b": pd.read_parquet(o / "phase1b/llama_cfd.parquet"),
        }
        self.p1_rerun = pd.read_parquet(o / "phase1_rerun_h100/llama.parquet")
        self.p1_4bit = pd.read_parquet(o / "phase1_90b_1gpu_4bit/llama.parquet")
        self.p1_lowercase = pd.read_parquet(o / "phase1_lowercase_v1/llama_dev.parquet")
        self.p1_invalid90 = pd.read_parquet(o / "phase1/llama.invalid_multi_gpu.parquet")
        self.p2 = {
            "qwen2b": pd.read_parquet(o / "phase2/qwen_2b_historical_2018.parquet"),
            "qwen7b": pd.read_parquet(o / "phase2/qwen_7b_historical_2018.parquet"),
            "llama11b": pd.read_parquet(o / "phase2/llama_dev_historical_2018.parquet"),
            "qwen72b": pd.read_parquet(o / "phase2/qwen_historical_2018.parquet"),
            "llama90b": pd.read_parquet(o / "phase2/llama_historical_2018.parquet"),
        }
        self.p2_prefixbug = pd.read_parquet(o / "phase2_prefixbug/llama_dev_historical_2018.parquet")
        self.ledger = json.loads(ledger.read_text())
        vr = json.loads((audit / "findings/stimulus_validation/silhouette_result.json").read_text())
        gp = json.loads((audit / "findings/stimulus_validation/gray_patch_result.json").read_text())
        self.gate = {"silhouette": vr, "gray_patch": gp}


def item_means_noninv(df: pd.DataFrame) -> pd.DataFrame:
    """Mean p_yes per item over the 12 cells outside the inversion structure."""
    sub = df[df.structure != "inversion"]
    g = sub.groupby("item_id").agg(p=("p_yes", "mean"),
                                   polarity=("polarity", "first"),
                                   subscale=("subscale", "first"))
    return g.reset_index()


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
def fig_gate1(d: Data, out: Path) -> None:
    """Stimulus validation: gender gap and max race probability, two stimuli."""
    sil, gp = d.gate["silhouette"], d.gate["gray_patch"]
    fig, axes = plt.subplots(1, 2, figsize=(TEXTWIDTH_IN, 2.0))
    panels = [
        ("Gender gap  $|P(\\mathrm{male})-P(\\mathrm{female})|$",
         [sil["gender"]["metric"], gp["gender"]["metric"]], sil["gender"]["threshold"]),
        ("Maximum race-token probability",
         [sil["race"]["metric"], gp["race"]["metric"]], sil["race"]["threshold"]),
    ]
    names = ["humanoid\nsilhouette", "grey patch"]
    for ax, (title, vals, thr) in zip(axes, panels):
        y = np.arange(2)[::-1]
        colours = [ORANGE if v > thr else BLUE for v in vals]
        ax.barh(y, vals, height=0.46, color=colours, zorder=3)
        ax.axvline(thr, color=INK2, ls=(0, (3, 2)), lw=0.9, zorder=4)
        ax.text(thr, 1.62, f" threshold {thr:.2f}", color=INK2, fontsize=7.5, va="top")
        for yi, v in zip(y, vals):
            ax.text(v + 0.02, yi, f"{v:.3f}", va="center", fontsize=8.5, color=INK)
        ax.set_yticks(y, names)
        ax.set_xlim(0, 1.22)
        ax.set_ylim(-0.6, 1.75)
        ax.set_xticks(np.arange(0, 1.01, 0.25))
        ax.set_title(title, loc="left", pad=6)
        ax.xaxis.grid(True, zorder=0)
        ax.set_axisbelow(True)
    fig.legend(handles=[Patch(facecolor=BLUE, label="within threshold"),
                        Patch(facecolor=ORANGE, label="flagged")],
               loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.09))
    finish(fig, "gate1", out)


def fig_capm_fixes(d: Data, out: Path) -> None:
    """Captured mass before and after each measurement fix, log axis.

    Drawn as before/after arrows rather than bars: a bar encodes magnitude by
    length from zero, and a log axis has no zero to start from.
    """
    L = d.ledger
    rows = [
        ("Phase 1, Llama-11B\nlowercase probe",
         L["phase1"]["llama11b_lowercase_FLAWED"].get("mean_captured_mass") or 0.000877,
         L["phase1"]["llama11b"]["mean_captured_mass"]),
        ("Phase 2, Llama-11B\ncue in the user turn",
         float(d.p2_prefixbug.captured_mass.mean()),
         float(d.p2["llama11b"].captured_mass.mean())),
        ("Phase 1, Llama-90B\nzeroed cross-GPU copies",
         float(d.p1_invalid90.captured_mass.mean()),
         L["phase1"]["llama90b"]["mean_captured_mass"]),
    ]
    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, 2.3))
    for i, (label, before, after) in enumerate(rows):
        y = len(rows) - 1 - i
        before = max(before, 1e-6)
        ax.annotate("", xy=(after, y), xytext=(before, y),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2,
                                    shrinkA=3.5, shrinkB=3.5))
        ax.plot([before], [y], "o", ms=6, color=ORANGE, zorder=3)
        ax.plot([after], [y], "o", ms=6, color=BLUE, zorder=3)
        ax.text(before, y + 0.20, f"{before:.4g}", ha="center", fontsize=7.5, color=INK2)
        ax.text(after, y + 0.20, f"{after:.3f}", ha="center", fontsize=7.5, color=INK2)
    ax.set_xscale("log")
    ax.set_xlim(1e-6, 4)
    ax.set_ylim(-0.6, len(rows) - 0.25)
    ax.set_yticks(range(len(rows))[::-1], [r[0] for r in rows])
    ax.set_xlabel("mean captured mass $\\kappa$ (log scale)")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=ORANGE, label="before the fix"),
                       Line2D([], [], marker="o", ls="", color=BLUE, label="after the fix")],
              loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2)
    finish(fig, "capm-fixes", out)


def fig_stimuli(d: Data, out: Path) -> None:
    """The three Phase 1 conditions plus the rejected silhouette."""
    from PIL import Image, ImageDraw

    w = h = 512  # the run used 1024 px; geometry is scale invariant
    rng = np.random.default_rng(42)
    noise = Image.fromarray(
        np.clip(rng.normal(128, 50, (h, w, 3)), 0, 255).astype(np.uint8), "RGB")
    grey = Image.new("RGB", (w, h), (150, 150, 150))

    sil = Image.new("RGB", (w, h), (210, 210, 210))
    dr = ImageDraw.Draw(sil)
    BODY = (90, 90, 90)
    cx, head_r, head_cy = w // 2, int(w * 0.08), int(h * 0.18)
    dr.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=BODY)
    sh, wa = int(w * 0.18), int(w * 0.12)
    tt = head_cy + head_r + int(h * 0.01)
    tb = tt + int(h * 0.28)
    dr.polygon([(cx - sh, tt), (cx + sh, tt), (cx + wa, tb), (cx - wa, tb)], fill=BODY)
    aw, at = int(w * 0.055), tt + int(h * 0.01)
    ab, ag = at + int(h * 0.26), int(w * 0.005)
    for s in (-1, 1):
        inner = cx + s * (sh + ag)
        x0, x1 = sorted([inner, inner + s * aw])
        dr.rectangle([x0, at, x1, ab], fill=BODY)
    lw_, lg = int(w * 0.075), int(w * 0.01)
    for s in (-1, 1):
        x0 = cx + s * lg
        x1 = x0 + s * lw_
        dr.rectangle([min(x0, x1), tb, max(x0, x1), tb + int(h * 0.30)], fill=BODY)

    panels = [(None, "no image\n(text only)"), (noise, "Gaussian noise"),
              (grey, "uniform grey patch"), (sil, "humanoid silhouette\n(rejected)")]
    fig, axes = plt.subplots(1, 4, figsize=(TEXTWIDTH_IN, 1.95))
    for ax, (img, label) in zip(axes, panels):
        if img is None:
            ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white",
                                       edgecolor=GRID, ls=(0, (3, 2)), lw=0.9))
            ax.text(0.5, 0.5, "—", ha="center", va="center",
                    fontsize=18, color=MUTED)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            ax.imshow(img)
            for sp in ax.spines.values():
                sp.set_visible(True)
                sp.set_color(GRID)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(label, fontsize=8.5, pad=5)
    axes[3].set_title(axes[3].get_title(), fontsize=8.5, color=ORANGE, pad=5)
    finish(fig, "stimuli", out)


def fig_capm_dist(d: Data, out: Path) -> None:
    """Headline figure of Study 1: captured mass by image condition."""
    fig, axes = plt.subplots(1, 3, figsize=(TEXTWIDTH_IN, 2.6), sharey=True)
    rng = np.random.default_rng(7)
    for ax, (key, (name, colour)) in zip(axes, MODELS.items()):
        df = d.p1[key]
        groups = [df[df.condition == c].captured_mass.to_numpy() for c in CONDITION_ORDER]
        bp = ax.boxplot(groups, widths=0.5, showfliers=False, patch_artist=True,
                        medianprops=dict(color=INK, lw=1.2),
                        boxprops=dict(facecolor="white", edgecolor=MUTED, lw=0.8),
                        whiskerprops=dict(color=MUTED, lw=0.8),
                        capprops=dict(color=MUTED, lw=0.8), zorder=2)
        for i, g in enumerate(groups, start=1):
            x = i + rng.uniform(-0.16, 0.16, len(g))
            ax.plot(x, g, "o", ms=2.0, alpha=0.35, color=colour,
                    mew=0, zorder=3, rasterized=False)
            ax.text(i, 1.045, f"{g.mean():.3f}", ha="center", fontsize=7.5, color=INK2)
        ax.set_xticks(range(1, 4), [CONDITION_SHORT[c] for c in CONDITION_ORDER])
        ax.set_xlabel("image condition")
        ax.set_title(name, loc="left", color=INK, pad=14)
        ax.set_ylim(-0.03, 1.12)
        ax.set_yticks(np.arange(0, 1.01, 0.25))
        ax.yaxis.grid(True)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("captured mass $\\kappa$")
    finish(fig, "capm-dist", out)


def fig_s1_structure(d: Data, out: Path) -> None:
    """Bias score by structure against the value its yes-rate alone predicts."""
    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, 2.6))
    structures = ["direct", "descriptive", "attribution", "hypothetical", "inversion"]
    width = 0.26
    xs = np.arange(len(structures))
    for j, (key, (name, colour)) in enumerate(MODELS.items()):
        df = d.p1[key]
        obs, pred = [], []
        for s in structures:
            sub = df[df.structure == s]
            obs.append(sub.bias_score.mean())
            sign = -1.0 if s == "inversion" else 1.0
            pred.append(sign * (10.0 / 22.0) * sub.p_yes.mean())
        off = (j - 1) * width
        ax.bar(xs + off, obs, width * 0.88, color=colour, label=name, zorder=3)
        ax.plot(xs + off, pred, "_", ms=9, mew=1.6, color=INK, zorder=5,
                label="predicted from yes-rate" if j == 0 else None)
    ax.axhline(0, color=MUTED, lw=0.8, zorder=2)
    ax.set_xticks(xs, structures)
    ax.set_ylabel("mean bias score $b_{i,t,c}$")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.17))
    finish(fig, "s1-structure", out)


def fig_s1_items(d: Data, out: Path) -> None:
    """Per-item agreement, split by keying, for the two production models."""
    base = item_means_noninv(d.p1["llama90b"])
    pos = base[base.polarity == 1].sort_values("p")
    neg = base[base.polarity == -1].sort_values("p")
    order = list(neg.item_id) + list(pos.item_id)
    ypos = {it: i for i, it in enumerate(order)}

    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, 4.1))
    ax.axhspan(-0.6, len(neg) - 0.4, color=NEUTRAL, zorder=0)
    for key in PRODUCTION:
        name, colour = MODELS[key]
        m = item_means_noninv(d.p1[key]).set_index("item_id")
        ax.plot([m.loc[i, "p"] for i in order], [ypos[i] for i in order],
                "o", ms=5, color=colour, label=name, zorder=4, mew=0)
        for grp, items in (("reverse", neg.item_id), ("positive", pos.item_id)):
            mu = m.loc[list(items), "p"].mean()
            y0 = (-0.4, len(neg) - 0.6) if grp == "reverse" else (len(neg) - 0.4, len(order) - 0.6)
            ax.plot([mu, mu], y0, color=colour, lw=1.3, ls=(0, (4, 2)), zorder=3)
    ax.set_yticks(range(len(order)), [f"item {i}" for i in order])
    ax.set_ylim(-0.8, len(order) - 0.2)
    ax.set_xlim(0, 1)
    ax.set_xlabel("mean $p_{\\mathrm{yes}}$ over the 12 cells outside inversion")
    ax.text(0.985, len(neg) / 2 - 0.5, "keyed in reverse", rotation=90,
            va="center", ha="right", fontsize=8, color=INK2)
    ax.text(0.985, (len(neg) + len(order)) / 2 - 0.5, "keyed towards sexism", rotation=90,
            va="center", ha="right", fontsize=8, color=INK2)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    handles = [Line2D([], [], marker="o", ls="", color=MODELS[k][1], label=MODELS[k][0])
               for k in PRODUCTION]
    handles.append(Line2D([], [], ls=(0, (4, 2)), color=MUTED, label="group mean"))
    ax.legend(handles=handles, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.07))
    finish(fig, "s1-items", out)


def perm_null(df: pd.DataFrame) -> tuple[np.ndarray, float]:
    """Full enumeration of all C(22,6) keying assignments. Exact, not sampled."""
    m = item_means_noninv(df)
    p = m.sort_values("item_id").p.to_numpy()
    obs_rev = m.sort_values("item_id").polarity.to_numpy() == -1
    total = p.sum()
    idx = np.array(list(itertools.combinations(range(22), 6)))
    rev_sums = p[idx].sum(axis=1)
    stat = (total - rev_sums) / 16.0 - rev_sums / 6.0
    observed = p[obs_rev].sum()
    t_obs = (total - observed) / 16.0 - observed / 6.0
    return stat, float(t_obs)


def fig_s1_perm(d: Data, out: Path) -> None:
    """Exact null distribution of polarity separation under random keying."""
    fig, axes = plt.subplots(1, 3, figsize=(TEXTWIDTH_IN, 2.3), sharey=True)
    for ax, (key, (name, colour)) in zip(axes, MODELS.items()):
        null, t_obs = perm_null(d.p1[key])
        pval = float(np.mean(np.abs(null) >= abs(t_obs)))
        ax.hist(null, bins=70, color=GRID, edgecolor="none", zorder=2)
        ax.axvline(t_obs, color=colour, lw=1.6, zorder=4)
        ax.set_title(name, loc="left", pad=4)
        ax.text(0.03, 0.93, f"observed {t_obs:+.3f}\nexact $p$ = {pval:.3f}",
                transform=ax.transAxes, ha="left", va="top", fontsize=7.6,
                color=INK2, linespacing=1.45)
        ax.set_xlabel("$T(\\ell)$")
        ax.set_yticks([])
        for sp in ("left",):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel(f"count of the\n{math.comb(22, 6):,} labellings")
    finish(fig, "s1-perm", out)


def fig_s1_replication(d: Data, out: Path) -> None:
    """Llama-90B reference run against the rerun and the 4-bit single-GPU run."""
    ref = d.p1["llama90b"].sort_values(["item_id", "structure", "condition"])
    keys = ["item_id", "structure", "condition"]
    fig, axes = plt.subplots(1, 2, figsize=(TEXTWIDTH_IN, 3.0), sharey=True, sharex=True)
    for ax, (other, label) in zip(axes, [(d.p1_rerun, "independent rerun, H100"),
                                         (d.p1_4bit, "4-bit, single GPU")]):
        o = other.sort_values(keys)
        merged = ref.merge(o, on=keys, suffixes=("_a", "_b"))
        x, y = merged.p_yes_a.to_numpy(), merged.p_yes_b.to_numpy()
        ok = np.isfinite(x) & np.isfinite(y)
        x, y = x[ok], y[ok]
        r = float(np.corrcoef(x, y)[0, 1])
        ax.plot([0, 1], [0, 1], color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=2)
        ax.plot(x, y, "o", ms=3.2, alpha=0.5, color=ORANGE, mew=0, zorder=3)
        ax.set_title(label, loc="left", pad=4)
        ax.text(0.04, 0.96, f"$n$ = {len(x)}\n$r$ = {r:.4f}\n"
                            f"mean $|\\Delta|$ = {np.abs(x - y).mean():.4f}",
                transform=ax.transAxes, ha="left", va="top", fontsize=7.6,
                color=INK2, linespacing=1.45)
        ax.set_xlabel("$p_{\\mathrm{yes}}$, reference run")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        ax.grid(True)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("$p_{\\mathrm{yes}}$, comparison run")
    finish(fig, "s1-replication", out)


def rr_pairs(df: pd.DataFrame, condition: str, tau: float = 0.5):
    """Per-pair robustness indicators, with the query each pair belongs to."""
    sub = df[df.condition == condition]
    o = sub[sub.scale_order == "original"].set_index(["query", "image_id"])
    r = sub[sub.scale_order == "reversed"].set_index(["query", "image_id"])
    j = o[["rating_normalised"]].join(r[["rating_normalised"]], lsuffix="_o", rsuffix="_r")
    j = j.dropna()
    ind = (j.rating_normalised_o - j.rating_normalised_r).abs() <= tau
    return ind.to_numpy().astype(float), j.index.get_level_values(0).to_numpy()


def cluster_bootstrap_drr(df: pd.DataFrame, tau: float = 0.5, B: int = 10000,
                          seed: int = 0) -> tuple[float, float, float]:
    """Percentile interval for Delta RR, resampling queries rather than rows."""
    iv, qv = rr_pairs(df, "vision", tau)
    it, qt = rr_pairs(df, "text_only", tau)
    queries = sorted(set(qv) | set(qt))
    rng = np.random.default_rng(seed)
    draws = np.empty(B)
    for b in range(B):
        pick = rng.choice(queries, size=len(queries), replace=True)
        mv = np.concatenate([iv[qv == q] for q in pick])
        mt = np.concatenate([it[qt == q] for q in pick])
        draws[b] = mv.mean() - mt.mean()
    return float(iv.mean() - it.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def fig_s2_rr(d: Data, out: Path) -> None:
    """Headline figure of Study 2: robustness with and without the image."""
    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, 2.5))
    xs = np.arange(len(MODELS))
    width = 0.34
    for off, cond, hatch, label in [(-width / 2, "text_only", "", "no image"),
                                    (width / 2, "vision", "///", "with image")]:
        vals = []
        for key in MODELS:
            ind, _ = rr_pairs(d.p2[key], cond)
            vals.append(ind.mean())
        colours = [MODELS[k][1] for k in MODELS]
        ax.bar(xs + off, vals, width * 0.9, color=colours, zorder=3,
               hatch=hatch, edgecolor="white", lw=0.8)
        for x, v in zip(xs + off, vals):
            ax.text(x, v + 0.025, f"{v:.3f}", ha="center", fontsize=8, color=INK)
    for i, key in enumerate(MODELS):
        drr, lo, hi = cluster_bootstrap_drr(d.p2[key])
        ax.annotate(f"$\\Delta\\mathrm{{RR}}$ {drr:+.3f}\n[{lo:+.2f}, {hi:+.2f}]",
                    xy=(i, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -26), textcoords="offset points",
                    ha="center", va="top", fontsize=7.6, color=INK2,
                    annotation_clip=False, linespacing=1.4)
    ax.set_xticks(xs, [MODELS[k][0] for k in MODELS])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("robustness rate $\\mathrm{RR}(\\tau=0.5)$")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(handles=[Patch(facecolor=MUTED, label="no image"),
                       Patch(facecolor=MUTED, hatch="///", edgecolor="white", label="with image")],
              ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.15))
    finish(fig, "s2-rr", out)


def fig_s2_anchor(d: Data, out: Path) -> None:
    """Raw rating under the reversed scale against the original scale."""
    fig, axes = plt.subplots(1, 3, figsize=(TEXTWIDTH_IN, 2.7), sharex=True, sharey=True)
    for ax, (key, (name, _)) in zip(axes, MODELS.items()):
        df = d.p2[key]
        ax.plot([1, 7], [7, 1], color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=2)
        ax.plot([1, 7], [1, 7], color=MUTED, lw=0.9, ls=(0, (1, 2)), zorder=2)
        slopes = {}
        for cond, colour in [("text_only", BLUE), ("vision", ORANGE)]:
            sub = df[df.condition == cond]
            o = sub[sub.scale_order == "original"].set_index(["query", "image_id"])
            r = sub[sub.scale_order == "reversed"].set_index(["query", "image_id"])
            j = o[["rating_expected"]].join(r[["rating_expected"]],
                                            lsuffix="_o", rsuffix="_r").dropna()
            x, y = j.rating_expected_o.to_numpy(), j.rating_expected_r.to_numpy()
            ax.plot(x, y, "o", ms=3.4, alpha=0.55, color=colour, mew=0, zorder=4)
            if len(x) > 2 and np.ptp(x) > 1e-9:
                slopes[cond] = float(np.polyfit(x, y, 1)[0])
        ax.set_title(name, loc="left", pad=4)
        txt = "\n".join(f"$\\beta_1$ {CONDITION_LABEL.get(c, c)} = {v:+.2f}"
                        for c, v in slopes.items())
        ax.text(0.04, 0.96, txt, transform=ax.transAxes, ha="left", va="top",
                fontsize=7.4, color=INK2, linespacing=1.5)
        ax.set_xlim(0.7, 7.3)
        ax.set_ylim(0.7, 7.3)
        ax.set_xticks(range(1, 8))
        ax.set_yticks(range(1, 8))
        ax.set_xlabel("$\\hat r$, original order")
        ax.grid(True)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("$\\hat r$, reversed order")
    axes[0].legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="no image"),
                            Line2D([], [], marker="o", ls="", color=ORANGE, label="with image"),
                            Line2D([], [], ls=(0, (3, 2)), color=MUTED, label="$y=8-x$ (anchors followed)"),
                            Line2D([], [], ls=(0, (1, 2)), color=MUTED, label="$y=x$ (anchors ignored)")],
                   loc="upper center", bbox_to_anchor=(1.75, -0.28), ncol=4)
    finish(fig, "s2-anchor", out)


def fig_s2_queries(d: Data, out: Path) -> None:
    """Per-query model rating against the low-ASI human baseline."""
    base = d.ledger["phase2"]["llama90b"]["human_low_asi_baselines"]
    queries = sorted(base, key=lambda q: base[q])
    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, 3.4))
    ax.axvline(4.0, color=MUTED, lw=1.0, ls=(0, (3, 2)), zorder=2)
    ax.text(3.92, -0.85, "anchor-insensitivity null, 4.0", fontsize=7.6,
            color=INK2, va="center", ha="right")
    for i, q in enumerate(queries):
        ax.plot([base[q]], [i], "D", ms=5.5, color=INK, zorder=5)
        for key in MODELS:
            df = d.p2[key]
            sub = df[(df.condition == "vision") & (df["query"] == q)]
            orig = sub[sub.scale_order == "original"].rating_normalised.mean()
            both = sub.rating_normalised.mean()
            ax.plot([orig], [i], "o", ms=5, color=MODELS[key][1], zorder=4, mew=0)
            ax.plot([both], [i], "o", ms=5, color=MODELS[key][1], zorder=3,
                    mew=0.8, mfc="white", mec=MODELS[key][1])
    control = queries.index("hot air baloon")
    ax.axhspan(control - 0.45, control + 0.45, color=NEUTRAL, zorder=0)
    ax.set_yticks(range(len(queries)), queries)
    ax.set_xlim(1, 7)
    ax.set_xlabel("normalised rating $\\tilde r$ (7 = extremely objective)")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    handles = [Line2D([], [], marker="D", ls="", color=INK, label="low-ASI human baseline")]
    handles += [Line2D([], [], marker="o", ls="", color=MODELS[k][1], label=MODELS[k][0])
                for k in MODELS]
    handles.append(Line2D([], [], marker="o", ls="", color=MUTED, mfc="white",
                          label="averaged over both orders"))
    ax.legend(handles=handles, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.16))
    finish(fig, "s2-queries", out)


def fig_app_heatmap(d: Data, out: Path) -> None:
    """Per-item bias score, items against models."""
    cols = []
    for key in MODELS:
        df = d.p1[key]
        cols.append(df.groupby("item_id").bias_score.mean())
    M = pd.concat(cols, axis=1)
    M.columns = [MODELS[k][0] for k in MODELS]
    meta = d.p1["llama90b"].drop_duplicates("item_id").set_index("item_id")
    labels = [f"{i:>2}  {meta.loc[i,'subscale']}{'  (rev)' if meta.loc[i,'polarity']==-1 else ''}"
              for i in M.index]
    vmax = float(np.abs(M.to_numpy()).max())
    fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN * 0.72, 5.2))
    im = ax.imshow(M.to_numpy(), cmap=DIVERGING, vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(M.shape[1]), M.columns, rotation=20, ha="right")
    ax.set_yticks(range(len(labels)), labels, fontsize=7.5)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.iat[i, j]
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=6.4,
                    color="white" if abs(v) > 0.55 * vmax else INK)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks(np.arange(-.5, M.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-.5, M.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.4)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, shrink=0.42, pad=0.03)
    cb.set_label("mean bias score $b_{i,t,c}$", fontsize=8)
    cb.outline.set_visible(False)
    finish(fig, "app-heatmap", out)


# --------------------------------------------------------------------------
# Phase 1B: the gender gap
# --------------------------------------------------------------------------
def face_gap(df: pd.DataFrame, subscale: str | None = None) -> dict:
    """
    Gender gap with a 95% interval, computed on face means.

    The unit of analysis is the face: each of the 40 faces is collapsed to one
    number before anything is compared, so the test is 20 against 20 however
    many prompts were run. Treating the 4,400 rows as independent would divide
    the standard error by about sqrt(110).
    """
    d = df if subscale is None else df[df.subscale == subscale]
    per_face = d.groupby(["face_target", "face_gender"]).bias_score.mean().reset_index()
    f = per_face[per_face.face_gender == "F"].bias_score.values
    m = per_face[per_face.face_gender == "M"].bias_score.values
    t, p = stats.ttest_ind(f, m)
    nf, nm = len(f), len(m)
    sp2 = ((nf - 1) * f.var(ddof=1) + (nm - 1) * m.var(ddof=1)) / (nf + nm - 2)
    se = np.sqrt(sp2 * (1 / nf + 1 / nm))
    half = stats.t.ppf(0.975, nf + nm - 2) * se
    gap = f.mean() - m.mean()
    return {"gap": gap, "p": p, "lo": gap - half, "hi": gap + half,
            "d": gap / np.sqrt(sp2)}


def fig_gap(d: Data, out: Path) -> None:
    """The thesis's headline result: the benevolent gap, and its size trend."""
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(TEXTWIDTH_IN, 3.5),
        gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.34})

    # ---- left: gap by model and subscale, with 95% intervals --------------
    series = ["all", "BS", "HS"]
    offs = {"all": -0.26, "BS": 0.0, "HS": 0.26}
    xs = np.arange(len(SIZE_ORDER))
    axL.axhline(0, color=INK, lw=0.8, zorder=1)
    for sub in series:
        lab, col = SUBSCALE[sub]
        g = [face_gap(d.p1b[m], None if sub == "all" else sub) for m in SIZE_ORDER]
        x = xs + offs[sub]
        axL.vlines(x, [v["lo"] for v in g], [v["hi"] for v in g],
                   color=col, lw=1.4, zorder=2)
        # A filled marker clears the Bonferroni line for five models; hollow does not.
        for xi, v in zip(x, g):
            filled = v["p"] < 0.01
            axL.plot(xi, v["gap"], "o", ms=5.5, mec=col, mew=1.4, zorder=3,
                     mfc=col if filled else "white")
        axL.plot([], [], "o", color=col, ms=5.5, label=lab)
    axL.set_xticks(xs)
    axL.set_xticklabels([MODELS[m][0] for m in SIZE_ORDER], rotation=20, ha="right")
    axL.set_ylabel("gender gap  (women $-$ men)")
    axL.set_title("by subscale", fontsize=9, loc="left", color=INK2)
    axL.legend(frameon=False, fontsize=7.5, loc="upper left", handletextpad=0.4)
    axL.spines[["top", "right"]].set_visible(False)
    axL.grid(axis="y", color=GRID, lw=0.6)
    axL.set_axisbelow(True)

    # ---- right: the benevolent gap against parameter count ---------------
    # The one gap in the ladder, named rather than interpolated over silently.
    axR.axvspan(11, 72, color=NEUTRAL, zorder=0)
    axR.axhline(0, color=INK, lw=0.8, zorder=1)
    # Direct labels rather than x ticks: 7B and 11B, and 72B and 90B, sit too
    # close in log space for tick labels to clear each other.
    place = {"qwen2b": (0, 9), "qwen7b": (0, 9), "llama11b": (2, -14),
             "qwen72b": (-2, 8), "llama90b": (0, -14)}
    for fam in ("qwen", "llama"):
        ms = [m for m in SIZE_ORDER if FAMILY[m] == fam]
        xx = [PARAMS_B[m] for m in ms]
        yy = [face_gap(d.p1b[m], "BS")["gap"] for m in ms]
        axR.plot(xx, yy, "-o", color=FAMILY_COLOUR[fam], ms=5, lw=1.6,
                 label=FAMILY_LABEL[fam], zorder=3)
        for m, x, y in zip(ms, xx, yy):
            axR.annotate(f"{PARAMS_B[m]}B", xy=(x, y), xytext=place[m],
                         textcoords="offset points", ha="center",
                         fontsize=7, color=FAMILY_COLOUR[fam], zorder=4)
    axR.set_xscale("log")
    axR.set_xticks([2, 10, 100])
    axR.set_xticklabels(["2B", "10B", "100B"])
    axR.minorticks_off()
    axR.set_xlim(1.5, 150)
    axR.set_xlabel("parameters")
    axR.set_ylabel("benevolent gap")
    axR.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
    axR.set_title("and how it scales", fontsize=9, loc="left", color=INK2)
    axR.legend(frameon=False, fontsize=7.5, loc="lower right",
               borderaxespad=0.2, handletextpad=0.4)
    axR.spines[["top", "right"]].set_visible(False)
    axR.grid(axis="y", color=GRID, lw=0.6)
    axR.set_axisbelow(True)
    axR.annotate("no model between", xy=(28, 1.0), xycoords=("data", "axes fraction"),
                 xytext=(0, -9), textcoords="offset points",
                 ha="center", va="top", fontsize=7, color=MUTED, zorder=4)

    finish(fig, "gap", out)


FIGURES = {
    "gap": fig_gap,
    "gate1": fig_gate1,
    "capm-fixes": fig_capm_fixes,
    "stimuli": fig_stimuli,
    "capm-dist": fig_capm_dist,
    "s1-structure": fig_s1_structure,
    "s1-items": fig_s1_items,
    "s1-perm": fig_s1_perm,
    "s1-replication": fig_s1_replication,
    "s2-rr": fig_s2_rr,
    "s2-anchor": fig_s2_anchor,
    "s2-queries": fig_s2_queries,
    "app-heatmap": fig_app_heatmap,
}


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-repo", type=Path,
                    default=Path.home() / "Code" / "VLM_Audit")
    ap.add_argument("--out", type=Path, default=here / "figures")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()

    set_style()
    d = Data(a.audit_repo, here / "planning" / "ledger_v2.json")
    names = a.only or list(FIGURES)
    for n in names:
        print(f"[{n}]")
        FIGURES[n](d, a.out)
    print(f"\n{len(names)} figures written to {a.out}")


if __name__ == "__main__":
    main()
