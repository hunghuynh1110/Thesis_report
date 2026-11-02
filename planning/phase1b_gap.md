# The thesis draft is scoped to the wrong experiment

Recorded 2 November 2026, after the model table in chapter 4 was questioned.

## What happened

Chapters 1 to 4 were drafted from `planning/ledger.json` and the `VLM_Audit`
checkout, both of which describe a **three model, two phase** project. The
project as actually run is **five models and three phases**. The difference was
found by reading `VLM_Audit_Handout.pdf` (19 Oct 2026) and
`GiaHung_Huynh_49384848_Thesis_Poster.pdf`, which are primary records of the
October progress seminar.

The earlier claim that "no smaller Qwen exists in the project" was wrong. It
was drawn from the code and outputs in the local checkout, which is a statement
about the checkout, not about the project.

## The design as actually run

| Phase | Stimulus | Measurements per model |
|---|---|---|
| 1A | no person shown: text only, grey patch, Gaussian noise | 330 |
| **1B** | **40 real faces, Chicago Face Database** | **4,400** |
| 2 | SIGIR 2018 image search results | 360 |

Five models: **Qwen-2B, Qwen-7B, Llama-11B, Llama-90B, Qwen-72B.**

Phase 1B faces: 5 faces in each of 8 cells (4 races x 2 genders), selected so
rated Attractiveness is closest to the overall median, cells matched to within
0.08 on a 1.5 to 5.5 scale. Cite Ma, Correll & Wittenbrink (2015).

## The headline result, which the current draft does not contain

Gender gap = female mean minus male mean, positive means attributed more
readily to women. Two-sample t-test on 20 per-face means per side. Bold in the
handout = survives Bonferroni for five models (p < 0.01).

| model | overall ASI | benevolent | hostile |
|---|---|---|---|
| Qwen-2B | −0.0010 (p=0.631) | −0.0071 (p=0.004) | +0.0051 (p=0.166) |
| Qwen-7B | +0.0050 (p=0.197) | +0.0185 (p=0.002) | −0.0084 (p=0.050) |
| Llama-11B | +0.0067 (p=0.231) | +0.0180 (p=0.039) | −0.0046 (p=0.638) |
| Llama-90B | +0.0053 (p=0.622) | +0.0340 (p=0.003) | −0.0234 (p=0.116) |
| Qwen-72B | +0.0221 (p<0.001) | +0.0540 (p<0.001) | −0.0099 (p=0.041) |

Three claims the handout draws from it:
1. The benevolent gap is significant in every model and grows with size in both
   families.
2. No hostile gap reaches significance, so its direction is visible but not
   defensible.
3. The combined score is 2.5 to 6.4 times smaller than the benevolent half in
   all five models, which is why four of them look unbiased on a single number.

Power, by face rather than by measurement (each face is a mean of 55):

| model | gap | SD between faces | Cohen's d | power |
|---|---|---|---|---|
| Qwen-2B | −0.0071 | 0.0073 | −0.97 | 85% |
| Qwen-7B | +0.0185 | 0.0174 | 1.06 | 91% |
| Llama-11B | +0.0180 | 0.0266 | 0.68 | 55% |
| Llama-90B | +0.0340 | 0.0341 | 1.00 | 87% |
| Qwen-72B | +0.0540 | 0.0144 | 3.74 | >99% |

Llama-11B is the only underpowered case, which is why its gap does not survive
correction.

Raw form, benevolent items in the sexist direction, inversion excluded:

| model | P(yes) women's faces | P(yes) men's faces | difference |
|---|---|---|---|
| Llama-90B | 0.627 | 0.573 | +0.055 |
| Qwen-72B | 0.265 | 0.185 | +0.080 |

The hostile result is not claimed: for Qwen-72B the negative score comes almost
entirely from the reverse coded items, and stated plainly its hostile gap is
+0.006.

## Captured mass, all five models

Phase 1A:

| model | no image | grey patch | Gaussian noise |
|---|---|---|---|
| Qwen-2B | 0.91 | 0.89 | 0.88 |
| Qwen-7B | 0.99 | 1.00 | 1.00 |
| Llama-11B | 0.98 | 0.24 | 0.20 |
| Llama-90B | 0.95 | 0.47 | 0.33 |
| Qwen-72B | 0.95 | 0.96 | 0.95 |

Phase 1B averages over all 4,400: Qwen-72B 0.97, Llama-90B 0.48, Llama-11B 0.14.
The collapse is a property of the Llama family at every size, not of scale,
which is a stronger claim than the current chapter 1 contribution 4 makes.

## Robustness under scale reversal, all five models

| model | no image | image shown |
|---|---|---|
| Qwen-2B | 0.20 | 0.19 |
| Qwen-7B | 0.20 | 0.16 |
| Qwen-72B | 0.90 | 0.16 |
| Llama-11B | 0.00 | 0.02 |
| Llama-90B | 0.90 | 0.04 |

The two small Qwens are near 0.20 in both conditions, so the collapse from 0.90
is specific to the large models. The current chapter 1 states this as a
two model result and would be stronger and more accurate stated over five.

## The 2018 relationship, tested

Across the 281 SIGIR participants a rater's sexism score correlates with judged
objectivity at Spearman rho = +0.188, p = 0.0016: real but weak, significant
because n is large. A median split gives 5.28 against 5.45 and does not reach
significance (p = 0.179). The five models show the same relationship at
rho = +0.70, but with five points p = 0.188, so it is a pattern that matches
rather than one that can be tested. **This supersedes the n = 2 argument in
chapter 1 aim 3 and in \cref{sec:s2-deviation}.**

## Limitations the handout already states

- 40 faces from one database, so this generalises to these faces, not to faces
  in general.
- Five faces per race cell is too thin for claims about race.
- One non-person control query, and no model between 11B and 72B.
- CFD licensing forbids printing the faces, so they may be shown on screen
  only. **This constrains what \cref{fig:stimuli} may contain.**
- Phase 2 confounds the image with the referent, since the no image prompt asks
  about "a typical result" and the image prompt about "this image result", so
  the fall from 0.90 to 0.16 mixes the two. Text only also rests on 10 distinct
  prompts, not 90.

## What is missing from this machine

Not present in the `VLM_Audit` checkout (HEAD `ff88e1d`, 21 Oct 2026) or in
`Thesis_report`:

- the Qwen-2B and Qwen-7B runs, for every phase;
- all Phase 1B data, for every model;
- the Chicago Face Database stimuli and the selection script;
- the code that runs Phase 1B and computes the gender gap, the t-tests and the
  power analysis;
- `src/models/qwen_extractor.py` still defines `_MODEL_IDS = {"qwen": 72B}`,
  so the committed code cannot load the small models.

`outputs_bunya/` holds three models and Phases 1A and 2 only. The handout
predates HEAD by two days, so the Phase 1B work exists but was never committed
here. Most likely it is still on Bunya under `/QRISdata/Q9468/`.

## Consequence for the draft

| Written | Needs |
|---|---|
| ch1 contribution 3: two models | five models |
| ch1 contribution 4: "Llama models" vs Qwen | family effect at every size, Phase 1B captured mass |
| ch1 aim 3: n = 2, not meaningful | n = 5, rho = +0.70, p = 0.188 |
| ch3 | a Phase 1B section: the gender gap statistic, the per-face unit of analysis, the t-test and the power argument |
| ch4 tab:models | five rows |
| ch4 §4.3 | a Phase 1B stimulus section and the CFD licence constraint |
| ch4 tab:scope | Phase 1B is an addition to the proposal, not a reduction |
| ch5 | Phase 1B is the headline result and currently has no section |
| figures | the gender gap by model and subscale, which is the thesis's main figure and does not exist |

The abstract brief in `frontmatter/abstract.tex` also needs rewriting, since it
was written around a finding that is no longer the main one.
