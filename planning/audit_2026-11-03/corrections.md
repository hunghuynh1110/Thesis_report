# Corrections after the audit

Implemented at the author’s request on 3 November 2026. This record describes the initial corrective pass; subsequent chapter rewrites, front matter completion and appendix revisions are recorded separately in Git history.

## Corrected

- A01: headline gender gap direction and corrected significance, consistently across abstract, results captions and summaries, and conclusion.
- A02: CALM consistency definition and related scope/aim descriptions.
- A03: anchor figure caption, including the negative Llama slope and five-model coverage.
- A04: safety bypass and unqualified novelty/representation claims.
- A05: bounded visual token budget, without claiming equal token counts.
- A06: validation statistic described as an absolute gender probability gap.
- A07: target probabilities stored in production, with top-ten records restricted to the diagnostic sweep.
- A08: high ASI comparison omitted from the analysis, without claiming the raw data were unavailable.
- A09: wording change in the modality comparison acknowledged.
- A10: delivered five-model scope and explicitly identified three-model subsets.
- A11: single-device versus multi-device execution, without assigning three GPUs to every large model.
- A12: half-point tolerance defined by absolute difference, not integer rounding.
- A13: Phase 1B t-test labels and p<0.001 bounds; table generator updated to reproduce them.
- A14: maximum Qwen coverage change corrected from 0.027 to 0.034, from the audited ledger.
- A15 to A17: narrower generalisation, slope diagnostics, and coverage versus refusal distinctions.
- A19: publication permission distinguished from redistribution restrictions.
- A20: Appendix D caption updated to reflect the main table’s three tolerances.

## Clarified without changing statistical decisions

A18: made the exchangeability assumption explicit and labelled Phase 1A polarity p values as unadjusted across models. No new correction family was imposed, and the existing Phase 1B significance threshold was retained.

## Unchanged

- The author’s reserved delta_m sign interpretation.
- Stored results, ledger values, figure files, bibliography and all equations.
- Every citation key, cross reference, label and commented planning block.
- The author’s own Section 4.1 paragraph.
- A21 and A22: missing job identifiers, final analysis commit, environment provenance, author declarations and existing layout defects still require separate completion.

## Numerical reporting changes

The stale model count n=2 is corrected to n=5; the incorrect coverage maximum is corrected from 0.027 to 0.034; and two displayed p=0.000 cells now use p<0.001. No underlying experimental result was changed. Model names were added to a caption to identify the direction and significance exceptions.

## Validation at the time of the corrective pass

Citation/reference/label occurrence checks pass. Equations and commented blocks are preserved. The Phase 1B table matches the updated generator exactly. The report builds to 103 pages with zero errors and zero undefined citations/references. The seven existing overfull boxes remain. No GPT mentions occur in the compiled PDF.
