#!/usr/bin/env python3
"""
Emit the result-table bodies of Chapters 5 and 6 from planning/ledger_v2.json.

The tables were written by hand when the project had three models and two
phases. Rather than hand-editing them to five, this prints the rows so the
numbers come from the same place the figures do and can be regenerated when a
run changes.

    python3 scripts/make_tables.py            # all tables
    python3 scripts/make_tables.py s1-ps      # one table

Paste the printed block between \\midrule and \\bottomrule. Column headers are
printed too, since the model count changes the column specifier.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LEDGER = json.loads((HERE / "planning" / "ledger_v2.json").read_text())
ORDER = ["qwen2b", "qwen7b", "llama11b", "qwen72b", "llama90b"]
LABEL = {k: LEDGER["_models"][k]["label"] for k in ORDER}
CONDITIONS = [("Text only", "text_only"), ("Grey patch", "gray_patch"),
              ("Noise", "noise")]
STRUCTURES = ["direct", "descriptive", "attribution", "hypothetical", "inversion"]


def sgn(x, nd=3):
    """Signed fixed-point, so a column of numbers stays aligned."""
    return f"${x:+.{nd}f}$"


def header(first: str) -> str:
    cols = " & ".join(LABEL[k] for k in ORDER)
    return (f"% column spec: {{@{{}}l{'c' * len(ORDER)}@{{}}}}\n"
            f"{first} & {cols} \\\\")


def t_capm() -> str:
    out = [header("Condition")]
    out.append(r"\midrule")
    for name, key in CONDITIONS:
        cells = []
        for m in ORDER:
            a = LEDGER["phase1a"][m]
            cm = a["by_condition_captured"][key]
            lo = a["frac_capm_below_0.1_by_condition"][key]
            cells.append(f"{cm:.3f} ({lo*100:.0f}\\%)")
        out.append(f"{name} & " + " & ".join(cells) + r" \\")
    out.append(r"\midrule")
    out.append("All (Phase~1A) & " + " & ".join(
        f"{LEDGER['phase1a'][m]['mean_captured_mass']:.3f}" for m in ORDER) + r" \\")
    out.append("Phase~1B, real faces & " + " & ".join(
        f"{LEDGER['phase1b'][m]['mean_captured_mass']:.3f}" for m in ORDER) + r" \\")
    return "\n".join(out)


def t_aggregate() -> str:
    rows = [
        (r"$\ASIint$ (\cref{eq:asi})", lambda a: sgn(a["asi_intrinsic"])),
        (r"Mean $\pyes$", lambda a: f"{a['mean_p_yes']:.3f}"),
        (r"Response-style part $\tfrac{3}{11}\bar p$ (\cref{eq:decomp})",
         lambda a: f"{3/11*a['mean_p_yes']:.3f}"),
        (r"Residual $D$", lambda a: sgn(a["asi_intrinsic"] - 3/11*a["mean_p_yes"])),
    ]
    out = [header(""), r"\midrule"]
    for label, fn in rows:
        out.append(label + " & " + " & ".join(
            fn(LEDGER["phase1a"][m]) for m in ORDER) + r" \\")
    out.append(r"\midrule")
    for sub in ("HS", "BS"):
        out.append(f"{sub} subscale & " + " & ".join(
            sgn(LEDGER["phase1a"][m]["by_subscale_bias"][sub]) for m in ORDER) + r" \\")
    return "\n".join(out)


def t_structure() -> str:
    out = [header("Structure"), r"\midrule",
           r"\multicolumn{%d}{@{}l}{\emph{mean directional score} $\bar b$} \\" % (len(ORDER)+1)]
    for st in STRUCTURES:
        out.append(st.capitalize() + " & " + " & ".join(
            sgn(LEDGER["phase1a"][m]["by_structure_bias"][st]) for m in ORDER) + r" \\")
    out.append(r"\midrule")
    out.append(r"\multicolumn{%d}{@{}l}{\emph{mean} $\pyes$} \\" % (len(ORDER)+1))
    for st in STRUCTURES:
        out.append(st.capitalize() + " & " + " & ".join(
            f"{LEDGER['phase1a'][m]['by_structure_p_yes'][st]:.3f}" for m in ORDER) + r" \\")
    return "\n".join(out)


def t_s1_ps() -> str:
    a0 = LEDGER["phase1a"][ORDER[0]]
    rows = [
        (rf"$\overline{{\pyes}}$, positively keyed ($n={a0['n_positive_noninv']}$)",
         lambda a: f"{a['p_yes_positive_noninv']:.3f}"),
        (rf"$\overline{{\pyes}}$, reverse keyed ($n={a0['n_reverse_noninv']}$)",
         lambda a: f"{a['p_yes_reverse_noninv']:.3f}"),
        (r"$\PS$ (\cref{eq:ps}, non-inversion rows)",
         lambda a: sgn(a["polarity_separation"])),
        (r"$\PS$, all rows (sensitivity)",
         lambda a: sgn(a["polarity_separation_all_rows"])),
    ]
    out = [header(""), r"\midrule"]
    for label, fn in rows:
        out.append(label + " & " + " & ".join(
            fn(LEDGER["phase1a"][m]) for m in ORDER) + r" \\")
    return "\n".join(out)


def t_s1_perm() -> str:
    a0 = LEDGER["phase1a"][ORDER[0]]["within_subscale_separation"]
    out = [header(""), r"\midrule"]
    out.append(r"Item-level $\PS$ & " + " & ".join(
        sgn(LEDGER["phase1a"][m]["perm_T_obs"]) for m in ORDER) + r" \\")
    out.append(r"Exact two-sided $p$ (\cref{eq:perm}) & " + " & ".join(
        f"{LEDGER['phase1a'][m]['perm_p_exact']:.3f}" for m in ORDER) + r" \\")
    out.append(r"\midrule")
    for sub in ("HS", "BS"):
        n = a0[sub]
        out.append(f"Within {sub} ({n['n_positive_items']} vs "
                   f"{n['n_reverse_items']} items) & " + " & ".join(
            sgn(LEDGER["phase1a"][m]["within_subscale_separation"][sub]["separation"])
            for m in ORDER) + r" \\")
    return "\n".join(out)


def t_gap() -> str:
    out = [header(""), r"\midrule"]
    for key, name in (("gender_gap_overall", "Combined"),
                      ("gender_gap_BS", "Benevolent"),
                      ("gender_gap_HS", "Hostile")):
        out.append(f"{name} $G_m$ & " + " & ".join(
            sgn(LEDGER["phase1b"][m][key]["gap"], 4) for m in ORDER) + r" \\")
        out.append(r"\quad exact $p$ & " + " & ".join(
            f"{LEDGER['phase1b'][m][key]['p']:.3f}" for m in ORDER) + r" \\")
    out.append(r"\midrule")
    out.append(r"Cohen's $d$ (benevolent) & " + " & ".join(
        sgn(LEDGER["phase1b"][m]["gender_gap_BS"]["cohens_d"], 2) for m in ORDER) + r" \\")
    return "\n".join(out)


def t_s2_rr() -> str:
    out = [header(""), r"\midrule"]
    for key, name in (("rr_text_only", "No image"), ("rr_vision", "Image shown")):
        out.append(f"$\\RR$, {name.lower()} & " + " & ".join(
            f"{LEDGER['phase2'][m][key]:.3f}" for m in ORDER) + r" \\")
    out.append(r"$\dRR$ & " + " & ".join(
        sgn(LEDGER["phase2"][m]["delta_rr"]) for m in ORDER) + r" \\")
    out.append(r"\midrule")
    out.append(r"$\dm$ & " + " & ".join(
        sgn(LEDGER["phase2"][m]["delta_m"]) for m in ORDER) + r" \\")
    out.append(r"Mean $\capm_{\Dset}$ & " + " & ".join(
        f"{LEDGER['phase2'][m]['mean_captured_mass']:.3f}" for m in ORDER) + r" \\")
    return "\n".join(out)


def t_s2_rr_full() -> str:
    out = [r"% column spec: {@{}lccccc@{}}",
           r"& \multicolumn{3}{c}{$\RR_{\text{vision}}(\tau)$ / $\RR_{\text{text}}(\tau)$} & $\dRR(0.5)$ & 95\% CI \\",
           r"\cmidrule(lr){2-4}",
           r"Model & $\tau=0.25$ & $\tau=0.5$ & $\tau=1$ & & \\",
           r"\midrule"]
    for m in ORDER:
        p = LEDGER["phase2"][m]
        tol = " & ".join(
            f"{p['rr_vision_by_tol'][t]:.3f} / {p['rr_text_only_by_tol'][t]:.2f}"
            for t in ("0.25", "0.5", "1.0"))
        lo, hi = p["delta_rr_ci95"]
        out.append(f"{LABEL[m]} & {tol} & {sgn(p['delta_rr'])} & "
                   f"$[{lo:+.2f},{hi:+.2f}]$ \\\\")
    return "\n".join(out)


def t_s2_anchor() -> str:
    out = [r"% column spec: {@{}lcccc@{}}",
           r"& \multicolumn{2}{c}{Text only} & \multicolumn{2}{c}{Vision} \\",
           r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
           r"Model & original & reversed & original & reversed \\",
           r"\midrule"]
    for m in ORDER:
        r_ = LEDGER["phase2"][m]["mean_raw_rating"]
        out.append(f"{LABEL[m]} & " + " & ".join(
            f"{r_[c][o]:.2f}" for c in ("text_only", "vision")
            for o in ("original", "reversed")) + r" \\")
    return "\n".join(out)


def t_s2_deltam() -> str:
    rows = [(r"Original order only (\cref{eq:deltam})", "delta_m_original"),
            ("Reversed order only", "delta_m_reversed"),
            ("Order-averaged", "delta_m_order_averaged"),
            (r"Anchor-insensitivity null (\cref{prop:null})", "delta_m_null")]
    out = [header(r"$\dm$ variant"), r"\midrule"]
    for label, key in rows:
        out.append(label + " & " + " & ".join(
            sgn(LEDGER["phase2"][m][key]) for m in ORDER) + r" \\")
    return "\n".join(out)


def t_s2_person() -> str:
    out = [r"% column spec: {@{}lcccccc@{}}",
           r"& \multicolumn{3}{c}{Original order} & \multicolumn{3}{c}{Order-averaged} \\",
           r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
           r"Model & 9 person queries & control & gap & 9 person queries & control & gap \\",
           r"\midrule"]
    for m in ORDER:
        cells = []
        for tag in ("original", "order_averaged"):
            x = LEDGER["phase2"][m][f"person_vs_control_{tag}"]
            cells += [sgn(x["person_queries"]), sgn(x["control"]), f"{x['gap']:.3f}"]
        out.append(f"{LABEL[m]} & " + " & ".join(cells) + r" \\")
    return "\n".join(out)


def t_s1_capmfilter() -> str:
    out = [header("Rows kept"), r"\midrule"]
    rows = [("all 330", None)] + [(f"$\\capm\\ge{t}$", t) for t in ("0.1", "0.3", "0.5")]
    for label, thr in rows:
        cells = []
        for m in ORDER:
            a = LEDGER["phase1a"][m]
            if thr is None:
                n, v, ps = a["n"], a["asi_intrinsic"], a["polarity_separation"]
            else:
                f = a["capm_filtered"][thr]
                n, v, ps = f["n"], f["asi_intrinsic"], f["polarity_separation"]
            cells.append(f"{n} / {v:+.3f} / {ps:+.3f}")
        out.append(label + " & " + " & ".join(cells) + r" \\")
    return "\n".join(out)


TABLES = {"capm": t_capm, "s1-aggregate": t_aggregate, "s1-structure": t_structure,
          "s1-ps": t_s1_ps, "s1-perm": t_s1_perm, "s1b-gap": t_gap, "s2-rr": t_s2_rr,
          "s2-rr-full": t_s2_rr_full, "s2-anchor": t_s2_anchor,
          "s2-deltam": t_s2_deltam, "s2-person": t_s2_person,
          "s1-capmfilter": t_s1_capmfilter}


def main() -> None:
    names = sys.argv[1:] or list(TABLES)
    for n in names:
        if n not in TABLES:
            print(f"unknown table {n!r}; have {', '.join(TABLES)}", file=sys.stderr)
            continue
        print(f"\n{'='*72}\n{n}\n{'='*72}")
        print(TABLES[n]())


if __name__ == "__main__":
    main()
