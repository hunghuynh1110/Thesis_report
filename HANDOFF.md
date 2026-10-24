# Handoff — thesis report (read this first)

This file hands the work over from a cloud Claude Code session
(`session_01Uu68fiHZwNyn2VrvVuSXoj`, 20–24 Oct 2026) to a fresh local session.
Read this file, then `planning/OUTLINE.md`. Everything below is already
committed and pushed.

## 1. The project

- **Thesis:** *Auditing VLM Perception of Gender Bias using Human Sexism Scales
  in Image Search*. REIT4841, UQ, author Gia Hung Huynh, supervisor
  Prof Gianluca Demartini (a co-author of the SIGIR 2018 paper used as the human
  baseline). Final report due **9 Nov 2026**.
- **Method in one line:** read next-token probabilities from one forward pass
  (never generated text) for the 22 ASI items (Phase 1) and for 1–7 objectivity
  ratings of SIGIR 2018 image-search results with CALM scale reversal (Phase 2).
- **Models:** Llama-3.2-90B-Vision and Qwen2-VL-72B (production),
  Llama-3.2-11B (development). GPT-4o not audited.

## 2. Repositories

| Repo | What | Branch |
|---|---|---|
| `hunghuynh1110/Thesis_report` (private, this repo) | LaTeX report, synced with Overleaf | `main` — **Overleaf only syncs `main`** |
| `hunghuynh1110/VLM_Audit` (public) | code, result files (`outputs_bunya/`), progress notes | `claude/bold-archimedes-ro2f9u` = latest work (`fix/multi-gpu-zero-copy`) + report scripts |

On `VLM_Audit`, **`main` is stale** (stops on 9 Aug, before the 90B fix and
the Qwen runs). Always use the branch above.

## 3. What exists in this repo

- `main.tex`, `preamble.tex`: report class, 12 pt A4, IEEE citations via
  biblatex/biber, notation macros. `\showplantrue/false` in `preamble.tex`
  shows or hides all plan boxes.
- `frontmatter/`, `chapters/01–08`, `appendices/A–E`: an **outline**, not
  prose. Each section has a blue *Plan* box (what to argue, what to cite, which
  numbers, which figure). Equations, propositions and tables (with verified
  numbers) are in place. 14 figures are `\plannedfigure` placeholders, and one
  TikZ diagram is drafted.
- `references.bib`: 62 entries checked twice (21 and 23 Oct), 49 `core` +
  13 `reserve`, with only 3 arXiv-only entries. Evidence is in
  `planning/references_audit.md`.
- `planning/OUTLINE.md`: chapter map, page budget, figure, table and maths
  lists, new analyses A1–A12, decisions D1–D7, and corrections to the August
  thesis-plan draft.
- `planning/facts_ledger.md`, `ledger.json`, `preliminary_diagnostics.json`:
  where every number comes from.
- Builds cleanly: `latexmk -pdf main.tex` gives 59 pages, no errors.

## 4. The user's requirements (keep to these)

1. **Plan before doing.** For anything non-trivial, give a short plan of what
   you will and won't do, and wait for approval.
2. **The user may write sections by hand.** The outline must say exactly which
   formulas, references, figures and numbers go where. **The abstract is
   written last.**
3. **References:** at least ~40 *meaningful* ones, mostly peer-reviewed, few
   arXiv-only, nothing unpublished or low-quality. Verify every new reference
   against the publisher or proceedings record before adding it, and record the
   evidence in `planning/references_audit.md`.
4. **Use the latest data:** the poster and handouts were built on the result
   files of the `VLM_Audit` branch above. Never cite FLAWED or INVALID runs
   except as evidence of a fault.
5. **New analyses are allowed (CPU only, on stored result files), but explain
   why each is needed.**
6. Use a formal, widely used template (currently the standard `report` class
   with the EECS front-matter order).

## 5. Results that change the story (see Ch 3, 5, 6 plan boxes)

- $\mathrm{ASI}_\mathrm{int} = \tfrac{3}{11}\bar p_\mathrm{yes} + D$ for the full
  22×5×3 design. Llama-90B's +0.153 is below what its yes-rate alone predicts
  (0.160).
- Polarity separation (non-inversion rows): Llama-11B −0.110, 90B −0.097,
  Qwen −0.188. The exact permutation test (74,613 labellings) gives
  p = 0.341 / 0.196 / **0.010**, so only Qwen is distinguishable from chance.
- The inversion structure carries little attitude signal: corr(direct,
  1 − inversion) = 0.10 / 0.04 / 0.47.
- Captured mass κ text / grey / noise: Llama-90B 0.951 / 0.467 / 0.329,
  Qwen ≈ 0.95 throughout. Defensiveness is Llama-specific.
- ΔRR: −0.856 (90B, 95% CI −0.98 to −0.66) and −0.744 (Qwen, −0.97 to −0.49).
  The mechanism is that with an image the model stops following the stated
  scale direction (raw ratings 4.79 / 4.64 vs text-only 2.75 / 5.13).
- δ_m depends on scale order. Original order (the proposal's Eq. 3.4):
  90B −0.491, Qwen **+0.217**. Order-averaged: −1.203 / −0.625. The null for
  ignoring the scale is −1.280. The person-vs-balloon gap survives
  (0.92 / 0.32).

Numbers marked *prelim* in the LaTeX come from
`VLM_Audit/scripts/report/preliminary_diagnostics.py` and must be regenerated
by a final analysis script.

## 6. Open decisions (user + supervisor)

- **D1** primary δ_m definition. Recommended: original order.
- **D2** δ_m sign. In SIGIR 2018, more sexist raters rate biased grids *more*
  objective, so δ_m < 0 means *more* bias-aware, not more biased (the opposite
  of the proposal's reading).
- **D3** polarity-separation definition. Recommended: non-inversion rows.
- D4–D7 are in `planning/OUTLINE.md` §6.

## 7. Known gaps / to-dos

- Job IDs for the Qwen production run and the 90B rerun are not in the repo.
  The user must copy them from Bunya logs (placeholders in Appendix C).
- Reference details still worth one check on the publisher page: Metaxa et al.
  author list; pages for Flamingo, RMSNorm and InstructGPT (deliberately
  omitted); Bai et al. 2025 issue number.
- Analyses still to do: A8 (κ-filtered sensitivity, 90B and Qwen) and A10
  (high-ASI baselines; needs the raw SIGIR CSV, released publicly by the SIGIR
  authors). A11 needs a GPU, so it is out of scope (state it as a limitation).
- **Suggested next step (not yet approved):** one script in `VLM_Audit`
  (`scripts/report/`) that finalises all *prelim* numbers and renders the 14
  figures as vector PDFs into `Thesis_report/figures/`. After that, write
  chapters in the order 3 → 4 → 5 → 6 → 2 → 7 → 1 → 8 → abstract.

## 8. Working conventions

- Overleaf ↔ GitHub: before pushing from outside Overleaf, the user should
  click *Push Overleaf changes to GitHub*; after a push, *Pull GitHub changes
  into Overleaf*. Always `git pull` before editing.
- Keep the notation macros in `preamble.tex` (`\pyes`, `\capm`, `\ASIint`,
  `\PS`, `\dRR`, `\dm`, …). In plan boxes use `\citeplan{}` (not `\cites`,
  which biblatex reserves).
- Citations inside plan boxes vanish when plan boxes are hidden, so the final
  prose must carry its own `\cite`.
- Commit messages: imperative subject line, explanatory body.
