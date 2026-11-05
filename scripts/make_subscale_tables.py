"""
Emits the bodies of the two subscale tables in section 6.4 and prints the
statistics quoted in its prose.

Human side: the SIGIR 2018 participants split at the median of the total ASI
score and, separately, at the median of each subscale score. The subscale
scores are stored in the released CSV as asi_benevolent_score and
asi_hostile_score, so they are read, not reconstructed.

Model side: Phase 1A intrinsic scores by subscale against the original-order
extrinsic deviations.

Run from the thesis root with the audit repository's interpreter:
    ~/Code/VLM_Audit/.venv/bin/python scripts/make_subscale_tables.py
"""

from itertools import permutations
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AUDIT = Path.home() / "Code" / "VLM_Audit"
CSV = AUDIT / "data" / "sigir2018" / "final_anonymised.csv"
PHASE2 = AUDIT / "outputs_bunya" / "phase2"

QUERIES = ["aggressive person", "anxious person", "bossy person", "calm person",
           "casual person", "hot air baloon", "interested person",
           "smart person", "warm person", "working person"]

MODELS = {
    "Qwen-2B":   "qwen_2b_historical_2018.parquet",
    "Qwen-7B":   "qwen_7b_historical_2018.parquet",
    "Llama-11B": "llama_dev_historical_2018.parquet",
    "Qwen-72B":  "qwen_historical_2018.parquet",
    "Llama-90B": "llama_historical_2018.parquet",
}

# Phase 1A by_subscale, from outputs_bunya/phase1/*_summary.json
SUBSCALE = {
    "Qwen-2B":   (0.0588, 0.0490),
    "Qwen-7B":   (-0.0158, 0.0489),
    "Llama-11B": (0.0083, 0.1588),
    "Qwen-72B":  (-0.0145, 0.0301),
    "Llama-90B": (0.1473, 0.1586),
}

SPLITS = [("Total ASI", "asi_score"),
          ("Benevolent", "asi_benevolent_score"),
          ("Hostile", "asi_hostile_score")]


def per_query_mean(sub: pd.DataFrame) -> dict[str, float]:
    """Mean specific_bias per query over a participant subset."""
    acc: dict[str, list[float]] = {q: [] for q in QUERIES}
    for i in range(10):
        chunk = sub[[f"{i}_query", f"specific_bias_{i}"]].dropna()
        for q, b in chunk.itertuples(index=False):
            if q in acc:
                acc[q].append(float(b))
    return {q: float(np.mean(v)) if v else float("nan") for q, v in acc.items()}


def ols(y, cols):
    """OLS with intercept and conventional two-sided Student t inference."""
    cols = [np.asarray(c, float) for c in cols]
    X = np.column_stack([np.ones(len(cols[0]))] + cols)
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = resid @ resid / (len(y) - X.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    p = 2 * stats.t.sf(np.abs(beta / se), df=len(y) - X.shape[1])
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, p, r2


def spearman(a, b) -> float:
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    return float(ra @ rb / np.sqrt((ra @ ra) * (rb @ rb)))


def exact_p(x, y) -> tuple[float, int]:
    """Two sided exact permutation p over all pairings of y against x."""
    obs = abs(spearman(x, y))
    hits = sum(1 for perm in permutations(range(len(y)))
               if abs(spearman(x, [y[i] for i in perm])) >= obs - 1e-12)
    return hits / factorial(len(y)), hits


def signed(v: float) -> str:
    return f"$-{abs(v):.3f}$" if v < 0 else f"$+{v:.3f}$"


def main() -> None:
    df = pd.read_csv(CSV)
    baselines, rows = {}, []

    for label, col in SPLITS:
        cut = df[col].median()
        lo, hi = df[df[col] <= cut], df[df[col] > cut]
        blo, bhi = per_query_mean(lo), per_query_mean(hi)
        baselines[label] = blo
        mlo = float(np.mean([blo[q] for q in QUERIES]))
        mhi = float(np.mean([bhi[q] for q in QUERIES]))
        rows.append(f"{label} & ${cut:.3f}$ & {len(lo)} & {len(hi)} & "
                    f"${mlo:.3f}$ & ${mhi:.3f}$ & {signed(mhi - mlo)} \\\\")

    print("% ---- table 1 body: human splits ----")
    print("\n".join(rows))

    # joint regression on each participant's mean objectivity rating
    df["mean_obj"] = df[[f"specific_bias_{i}" for i in range(10)]].mean(axis=1)
    d = df[["mean_obj", "asi_benevolent_score", "asi_hostile_score"]].dropna()
    z = lambda s: (s - s.mean()) / s.std(ddof=1)
    bs, hs = z(d.asi_benevolent_score), z(d.asi_hostile_score)

    print(f"\n% n = {len(d)} participants")
    for name, cols, labels in [("BS alone", [bs], ["BS"]),
                               ("HS alone", [hs], ["HS"]),
                               ("joint", [bs, hs], ["BS", "HS"])]:
        beta, se, p, r2 = ols(d.mean_obj, cols)
        terms = "  ".join(f"{l} b={b:+.3f} p={pi:.4f}"
                          for l, b, pi in zip(labels, beta[1:], p[1:]))
        print(f"%   {name:<9} {terms}   R2={r2:.4f}")
    print(f"%   r(BS,HS) = {d.asi_benevolent_score.corr(d.asi_hostile_score):.3f}")

    # model side
    dm = {}
    for m, fn in MODELS.items():
        t = pd.read_parquet(PHASE2 / fn)
        t = t[(t.condition == "vision") & (t.scale_order == "original")]
        mq = t.groupby("query").rating_normalised.mean().to_dict()
        dm[m] = float(np.mean([mq[q] - baselines["Total ASI"][q] for q in QUERIES]))

    print("\n% ---- table 2 body: model subscale scores ----")
    for m in MODELS:
        b, h = SUBSCALE[m]
        print(f"{m} & {signed(b)} & {signed(h)} & {signed(dm[m])} \\\\")

    y = [dm[m] for m in MODELS]
    print()
    for lab, idx in [("aggregate", None), ("benevolent", 0), ("hostile", 1)]:
        x = ([SUBSCALE[m][idx] for m in MODELS] if idx is not None
             else [sum(SUBSCALE[m]) / 2 for m in MODELS])
        p, hits = exact_p(x, y)
        print(f"%   rho({lab:<10}) = {spearman(x, y):+.2f}   p={p:.3f}  ({hits}/120)")

    # baseline substitution shift
    shifts = [float(np.mean([baselines["Benevolent"][q] - baselines["Total ASI"][q]
                             for q in QUERIES]))]
    print(f"\n%   low-BS minus low-ASI baseline, mean over queries: {shifts[0]:+.6f}")


if __name__ == "__main__":
    main()
