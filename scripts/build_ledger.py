#!/usr/bin/env python3
"""
Rebuild planning/ledger.json from the real run outputs.

The previous ledger covered three models and two phases, because it was built
from a stale checkout. The project is five models over three phases:

    1A   330 measurements per model, no person shown
    1B   4400 measurements per model, 40 Chicago Face Database faces
    2    360 measurements per model, SIGIR 2018 image search results

Run with the audit repo's own interpreter, which has pandas and scipy:

    ~/Code/VLM_Audit/.venv/bin/python scripts/build_ledger.py

Every figure this writes is recomputed from the parquets. Nothing is copied
from a summary file, a slide or a handout, so the ledger can be used to check
those rather than the other way round.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path.home() / "Code" / "VLM_Audit"
OUT = REPO / "outputs_bunya"
HERE = Path(__file__).resolve().parent.parent

# display name -> (phase1a stem, phase1b stem, phase2 stem)
MODELS = {
    "qwen2b":   ("phase1/qwen_2b",   "phase1b/qwen_2b_cfd",   "phase2/qwen_2b_historical_2018"),
    "qwen7b":   ("phase1/qwen_7b",   "phase1b/qwen_7b_cfd",   "phase2/qwen_7b_historical_2018"),
    "llama11b": ("phase1/llama_dev", "phase1b/llama_dev_cfd", "phase2/llama_dev_historical_2018"),
    "llama90b": ("phase1/llama",     "phase1b/llama_cfd",     "phase2/llama_historical_2018"),
    "qwen72b":  ("phase1/qwen",      "phase1b/qwen_cfd",      "phase2/qwen_historical_2018"),
}
LABEL = {"qwen2b": "Qwen-2B", "qwen7b": "Qwen-7B", "llama11b": "Llama-11B",
         "llama90b": "Llama-90B", "qwen72b": "Qwen-72B"}
PARAMS_B = {"qwen2b": 2, "qwen7b": 7, "llama11b": 11, "llama90b": 90, "qwen72b": 72}


def r(x, n=4):
    """Round for storage, keeping NaN representable in JSON as None."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), n)


def face_gap(df: pd.DataFrame) -> dict:
    """
    Gender gap on Phase 1B.

    The unit of analysis is the face, not the measurement: each face
    contributes one number, itself the mean of 55 measurements. The test is a
    two-sample t-test on 20 female against 20 male face means, so n = 20 per
    group however many measurements were taken.
    """
    per_face = (df.groupby(["face_target", "face_gender"])
                  .bias_score.mean().reset_index())
    f = per_face[per_face.face_gender == "F"].bias_score.values
    m = per_face[per_face.face_gender == "M"].bias_score.values
    t, p = stats.ttest_ind(f, m)
    pooled_sd = np.sqrt((f.var(ddof=1) + m.var(ddof=1)) / 2)
    gap = f.mean() - m.mean()
    return {
        "gap": r(gap), "p": r(p, 5), "t": r(t, 3),
        "cohens_d": r(gap / pooled_sd, 3), "pooled_sd": r(pooled_sd, 5),
        "mean_female": r(f.mean()), "mean_male": r(m.mean()),
        "n_female_faces": int(len(f)), "n_male_faces": int(len(m)),
    }


def polarity_and_perm(df: pd.DataFrame) -> dict:
    """
    Polarity separation and its exact permutation test.

    PS is taken on the four structures where "yes" means agreement; inversion
    flips that meaning, so including it mixes two opposite quantities. The null
    enumerates all C(22,6) = 74,613 ways of labelling six items reverse-keyed,
    which makes the p-value exact rather than sampled.
    """
    noninv = df[df.structure != "inversion"]
    pos = noninv[noninv.polarity == 1].p_yes
    rev = noninv[noninv.polarity == -1].p_yes
    ps = pos.mean() - rev.mean()

    allrows = df[df.polarity == 1].p_yes.mean() - df[df.polarity == -1].p_yes.mean()

    # Item means over the 12 non-inversion cells; the item is the unit.
    item_mean = noninv.groupby("item_id").p_yes.mean().sort_index()
    vals = item_mean.to_numpy()
    rev_ids = sorted(df[df.polarity == -1].item_id.unique())
    obs_idx = tuple(sorted(item_mean.index.get_loc(i) for i in rev_ids))
    total = vals.sum()
    n_rev = len(obs_idx)
    n_pos = len(vals) - n_rev

    def stat(idx):
        srev = vals[list(idx)].sum()
        return (total - srev) / n_pos - srev / n_rev

    t_obs = stat(obs_idx)
    hits = count = 0
    for comb in itertools.combinations(range(len(vals)), n_rev):
        count += 1
        if abs(stat(comb)) >= abs(t_obs) - 1e-12:
            hits += 1
    # Within each subscale: 8 positively keyed against 3 reverse keyed, which is
    # too thin to test and is reported descriptively.
    within = {}
    for sub in ("HS", "BS"):
        w = noninv[noninv.subscale == sub]
        wp, wr = w[w.polarity == 1].p_yes, w[w.polarity == -1].p_yes
        within[sub] = {
            "separation": r(wp.mean() - wr.mean()),
            "n_positive_items": int(w[w.polarity == 1].item_id.nunique()),
            "n_reverse_items": int(w[w.polarity == -1].item_id.nunique()),
        }

    return {
        "within_subscale_separation": within,
        "p_yes_positive_noninv": r(pos.mean()),
        "p_yes_reverse_noninv": r(rev.mean()),
        "n_positive_noninv": int(len(pos)), "n_reverse_noninv": int(len(rev)),
        "polarity_separation": r(ps),
        "polarity_separation_all_rows": r(allrows),
        "perm_T_obs": r(t_obs), "perm_p_exact": r(hits / count, 5),
        "perm_n_labellings": count,
    }


def _filtered(df: pd.DataFrame, thr: float) -> dict:
    d = df[df.captured_mass >= thr]
    ni = d[d.structure != "inversion"]
    ps = ni[ni.polarity == 1].p_yes.mean() - ni[ni.polarity == -1].p_yes.mean()
    return {"n": int(len(d)), "asi_intrinsic": r(d.bias_score.mean()),
            "polarity_separation": r(float(ps))}


def phase1a(stem: str) -> dict:
    df = pd.read_parquet(OUT / f"{stem}.parquet")
    return {
        "file": f"outputs_bunya/{stem}.parquet",
        "n": int(len(df)),
        "model_id": df.model_id.iloc[0],
        "asi_intrinsic": r(df.bias_score.mean()),
        "mean_p_yes": r(df.p_yes.mean()),
        "mean_captured_mass": r(df.captured_mass.mean()),
        "n_distinct_p_yes": int(df.p_yes.nunique()),
        "n_nan_p_yes": int(df.p_yes.isna().sum()),
        "by_condition_captured": {k: r(v) for k, v in
                                  df.groupby("condition").captured_mass.mean().items()},
        "by_condition_p_yes": {k: r(v) for k, v in
                               df.groupby("condition").p_yes.mean().items()},
        "by_structure_bias": {k: r(v) for k, v in
                              df.groupby("structure").bias_score.mean().items()},
        "by_subscale_bias": {k: r(v) for k, v in
                             df.groupby("subscale").bias_score.mean().items()},
        "per_item_bias": {str(k): r(v) for k, v in
                          df.groupby("item_id").bias_score.mean().items()},
        "by_structure_p_yes": {k: r(v) for k, v in
                               df.groupby("structure").p_yes.mean().items()},
        "frac_capm_below_0.1_by_condition": {
            k: r(v) for k, v in
            df.assign(low=df.captured_mass < 0.1)
              .groupby("condition").low.mean().items()},
        **polarity_and_perm(df),
        # Sensitivity to measurement coverage: recompute the two headline
        # quantities on progressively better-covered rows. Llama's vision-
        # condition p_yes rests on a minority of its mass, so a result that
        # depends on low-coverage rows is not safe to report.
        "capm_filtered": {
            str(thr): _filtered(df, thr) for thr in (0.1, 0.3, 0.5)},
    }


def phase1b(stem: str) -> dict:
    df = pd.read_parquet(OUT / f"{stem}.parquet")
    out = {
        "file": f"outputs_bunya/{stem}.parquet",
        "n": int(len(df)),
        "n_faces": int(df.face_target.nunique()),
        "model_id": df.model_id.iloc[0],
        "asi_intrinsic": r(df.bias_score.mean()),
        "mean_captured_mass": r(df.captured_mass.mean()),
        "gender_gap_overall": face_gap(df),
        "gender_gap_BS": face_gap(df[df.subscale == "BS"]),
        "gender_gap_HS": face_gap(df[df.subscale == "HS"]),
        "by_subscale_bias": {k: r(v) for k, v in
                             df.groupby("subscale").bias_score.mean().items()},
        "by_race_bias": {k: r(v) for k, v in
                         df.groupby("face_race").bias_score.mean().items()},
        "captured_mass_by_cell": {f"{a}_{b}": r(v) for (a, b), v in
                                  df.groupby(["face_race", "face_gender"])
                                    .captured_mass.mean().items()},
    }
    # Raw yes-rate form: benevolent items stated in the sexist direction,
    # inversion excluded, which is how the handout reports the same gap.
    bs = df[(df.subscale == "BS") & (df.polarity == 1) & (df.structure != "inversion")]
    pf = bs.groupby(["face_target", "face_gender"]).p_yes.mean().reset_index()
    fm = pf[pf.face_gender == "F"].p_yes.mean()
    mm = pf[pf.face_gender == "M"].p_yes.mean()
    out["raw_p_yes_BS_positive_noninv"] = {
        "female": r(fm), "male": r(mm), "difference": r(fm - mm)}
    return out


CONTROL_QUERY = "hot air baloon"


def phase2_detail(df: pd.DataFrame, base: dict) -> dict:
    """
    Everything chapter 6 reports: robustness at three tolerances, the cluster
    bootstrap interval, the delta_m variants and the person/control split.

    Ratings are normalised onto the original polarity before anything is
    compared, so a reversed-order 7 becomes a 1. The bootstrap resamples the
    ten queries rather than the 90 rows, because without an image the input is
    fixed by the query and order alone: the 90 text-only pairs are 10 distinct
    pairs measured nine times.
    """
    def norm(sub):
        v = sub.rating_expected.to_numpy()
        return np.where(sub.scale_order.to_numpy() == "reversed", 8 - v, v)

    out = {}
    pairs = {}
    for cond in ("vision", "text_only"):
        c = df[df.condition == cond]
        o = c[c.scale_order == "original"].set_index(["query", "image_id"]).sort_index()
        r = c[c.scale_order == "reversed"].set_index(["query", "image_id"]).sort_index()
        j = o[["rating_expected"]].join(r[["rating_expected"]], lsuffix="_o", rsuffix="_r").dropna()
        d = (j.rating_expected_o - (8 - j.rating_expected_r)).abs()
        pairs[cond] = d
        out[f"rr_{cond}_by_tol"] = {str(t): r2(float((d <= t).mean())) for t in (0.25, 0.5, 1.0)}

    # Cluster bootstrap over queries, B = 10,000, percentile interval.
    rng = np.random.default_rng(42)
    qs = sorted({q for q, _ in pairs["vision"].index})
    vis = {q: pairs["vision"].xs(q, level=0).to_numpy() for q in qs}
    txt = {q: pairs["text_only"].xs(q, level=0).to_numpy() for q in qs}
    draws = []
    for _ in range(10000):
        pick = rng.choice(len(qs), len(qs), replace=True)
        v = np.concatenate([vis[qs[i]] for i in pick])
        t = np.concatenate([txt[qs[i]] for i in pick])
        draws.append((v <= 0.5).mean() - (t <= 0.5).mean())
    lo, hi = np.percentile(draws, [2.5, 97.5])
    out["delta_rr_ci95"] = [r2(float(lo)), r2(float(hi))]
    out["bootstrap_B"] = 10000
    out["bootstrap_unit"] = "query"

    # Mean raw rating by condition and order, which is what shows anchor following.
    out["mean_raw_rating"] = {
        cond: {order: r2(float(g.rating_expected.mean()))
               for order, g in df[df.condition == cond].groupby("scale_order")}
        for cond in ("vision", "text_only")}

    # delta_m variants on the vision rows.
    v = df[df.condition == "vision"].copy()
    v["rnorm"] = norm(v)
    v["dev"] = v.rnorm - v["query"].map(base)
    by_order = {o: r2(float(g.dev.mean())) for o, g in v.groupby("scale_order")}
    out["delta_m_original"] = by_order.get("original")
    out["delta_m_reversed"] = by_order.get("reversed")
    per_pair = v.groupby(["query", "image_id"]).dev.mean()
    out["delta_m_order_averaged"] = r2(float(per_pair.mean()))
    out["delta_m_null"] = r2(float(np.mean([4 - base[q] for q in base])))

    # Person queries against the single non-person control.
    for tag, sel in (("original", v[v.scale_order == "original"]),
                     ("order_averaged", v)):
        g = sel.groupby("query").dev.mean()
        person = g[g.index != CONTROL_QUERY].mean()
        ctrl = g.get(CONTROL_QUERY, float("nan"))
        # gap = control - person, matching the draft's convention: positive
        # means the model deviates further on pictures of people than on the
        # non-person control.
        out[f"person_vs_control_{tag}"] = {
            "person_queries": r2(float(person)), "control": r2(float(ctrl)),
            "gap": r2(float(ctrl - person))}
    return out


def r2(x, n=3):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def phase2(stem: str) -> dict:
    df = pd.read_parquet(OUT / f"{stem}.parquet")
    s = json.loads((OUT / f"{stem}_summary.json").read_text())
    keep = ("n_rows", "delta_m", "rr_vision", "rr_text_only", "delta_rr",
            "mean_captured_mass")
    out = {"file": f"outputs_bunya/{stem}.parquet",
           "n": int(len(df)),
           "model_id": df.model_id.iloc[0]}
    out.update({k: r(s[k], 5) for k in keep if k in s})
    out.update(phase2_detail(df, BASELINES))
    return out


def main() -> int:
    if not OUT.exists():
        print(f"audit outputs not found at {OUT}", file=sys.stderr)
        return 1

    ledger: dict = {
        "_source": str(REPO),
        "_note": ("Rebuilt from the run outputs. Five models, three phases. "
                  "Supersedes the three-model ledger, which was built from a "
                  "stale checkout that had no Phase 1B and no small Qwens."),
        "_models": {k: {"label": LABEL[k], "params_b": PARAMS_B[k]} for k in MODELS},
        "phase1a": {}, "phase1b": {}, "phase2": {},
    }
    sys.path.insert(0, str(REPO))
    from src.data.sigir_loader import compute_low_asi_baselines
    global BASELINES
    BASELINES = {k: float(v) for k, v in compute_low_asi_baselines().items()}

    for key, (s1a, s1b, s2) in MODELS.items():
        ledger["phase1a"][key] = phase1a(s1a)
        ledger["phase1b"][key] = phase1b(s1b)
        ledger["phase2"][key] = phase2(s2)
        print(f"  {LABEL[key]:<10} 1A n={ledger['phase1a'][key]['n']:<5} "
              f"1B n={ledger['phase1b'][key]['n']:<6} "
              f"2 n={ledger['phase2'][key]['n']}")

    # Human baselines are a property of the SIGIR dataset, not of any model,
    # so they sit beside the phases rather than inside one.
    ledger["human_low_asi_baselines"] = {k: r(v) for k, v in BASELINES.items()}

    # The superseded runs the fault register cites, kept so the before-and-after
    # figures can be rebuilt without the old ledger.
    #
    # The lowercase Phase 1 run stored only logit_yes/logit_no and the two-token
    # softmax: captured mass was not instrumented until after that fault was
    # found, which is why the lowercase figure for it comes from the 8-prompt
    # diagnostic sweep (job 27103565) and is labelled as such rather than being
    # passed off as a 330-row mean.
    diag = json.loads((OUT / "diagnostics/diag_llama_dev_none.json").read_text())["rows"]
    ledger["superseded"] = {
        "llama11b_lowercase": {
            "file": "outputs_bunya/phase1_lowercase_v1/llama_dev.parquet",
            "n": int(len(pd.read_parquet(OUT / "phase1_lowercase_v1/llama_dev.parquet"))),
            "mean_captured_mass": None,
            "captured_mass_note": ("not recorded in this run; the lowercase pair "
                                   "held 0.000877 on the 8-prompt diagnostic sweep"),
            "diagnostic_mean_captured_mass": r(
                sum(x["captured_mass"] for x in diag) / len(diag), 6),
            "diagnostic_n": len(diag),
            "diagnostic_job": "27103565",
        },
        "llama11b_phase2_prefixbug": {
            "file": "outputs_bunya/phase2_prefixbug/llama_dev_historical_2018.parquet",
            "mean_captured_mass": r(pd.read_parquet(
                OUT / "phase2_prefixbug/llama_dev_historical_2018.parquet").captured_mass.mean(), 6)},
        "llama90b_invalid_multigpu": {
            "file": "outputs_bunya/phase1/llama.invalid_multi_gpu.parquet",
            "mean_captured_mass": r(pd.read_parquet(
                OUT / "phase1/llama.invalid_multi_gpu.parquet").captured_mass.mean(), 6)},
    }

    # Size axis: does the benevolent gap grow with parameter count?
    fam = {"qwen": ["qwen2b", "qwen7b", "qwen72b"], "llama": ["llama11b", "llama90b"]}
    ledger["size_axis"] = {
        f: [{"model": LABEL[k], "params_b": PARAMS_B[k],
             "gap_BS": ledger["phase1b"][k]["gender_gap_BS"]["gap"],
             "p_BS": ledger["phase1b"][k]["gender_gap_BS"]["p"]} for k in ks]
        for f, ks in fam.items()}

    path = HERE / "planning" / "ledger_v2.json"
    path.write_text(json.dumps(ledger, indent=1) + "\n")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
