#!/usr/bin/env python3
"""Emit the body of Table A.1: per-item mean bias score for all five models.

The earlier version of this table carried three model columns, left over from
when the audit covered three models. The heatmap beside it already showed five,
so table and figure disagreed on the same page. Both now read the same
parquets, and the trait phrases come from the audit repository's item table
rather than being retyped here.

    python3 scripts/make_items_table.py > /tmp/items_body.tex
"""
import sys
from pathlib import Path
import pandas as pd

AUDIT = Path.home() / "Code" / "VLM_Audit"
OUT = AUDIT / "outputs_bunya"
MODELS = {
    "qwen2b":   "phase1/qwen_2b.parquet",
    "qwen7b":   "phase1/qwen_7b.parquet",
    "llama11b": "phase1/llama_dev.parquet",
    "qwen72b":  "phase1/qwen.parquet",
    "llama90b": "phase1/llama.parquet",
}

def fmt(v: float) -> str:
    return f"$-{abs(v):.3f}$" if v < 0 else f"$\\phantom{{-}}{v:.3f}$"

def main() -> None:
    sys.path.insert(0, str(AUDIT))
    from src.data.asi_items import ASI_ITEMS

    frames = {k: pd.read_parquet(OUT / p) for k, p in MODELS.items()}
    M = pd.DataFrame({k: df.groupby("item_id").bias_score.mean()
                      for k, df in frames.items()})
    cells = {k: df.groupby("item_id").size().unique().tolist()
             for k, df in frames.items()}

    for n, item in enumerate(ASI_ITEMS, start=1):
        idx = M.index[n - 1]
        pol = "$+1$" if item.polarity == 1 else "$-1$"
        vals = " & ".join(fmt(v) for v in M.loc[idx])
        print(f"{n:<3}& {item.subscale} & {pol} & {item.trait} & {vals} \\\\")
    print(f"% cells per item per model: {cells}", file=sys.stderr)
    print(f"% items: {len(ASI_ITEMS)}, index match: "
          f"{len(ASI_ITEMS) == len(M)}", file=sys.stderr)

if __name__ == "__main__":
    main()
