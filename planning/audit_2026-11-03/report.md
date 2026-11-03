# Full thesis audit, 3 November 2026

## Scope and limits

Audited revision: `9644217`, after the GPT-removal commit. This pass inspected all eight chapters, the abstract, front matter and five appendices; checked all bibliography entries and citation/label resolution; recomputed the numerical ledger from the correct audit repository at `/Users/hunghuynh/Code/VLM_Audit`; and checked generated tables and figures. The audit repository was treated as read only. No manuscript text, numbers, references, captions or source code were corrected during this pass. This folder is an audit deliverable, not a manuscript revision.

Reference identity verification is distinct from claim verification. All 63 works were matched to real records, but that does not establish that every sentence citing them is justified. High-risk methodological claims were checked against the original papers and implementation, and the limits of individual checks are identified below. Model inference was not rerun; the audit establishes reproducibility from stored outputs, not independent proof of their collection provenance. Cluster logs and the author's historical intentions cannot be reconstructed from the available files.

## Writing work completed in this chat

| Material | State |
|---|---|
| Section 1.1 | Drafted in chat only |
| Sections 1.4 and 1.5 | Rewritten in source and committed separately (`21e6db9`, `2deb9e4`) |
| Section 2.1 | Drafted in chat only |
| Chapter 4 | Full prose rewrite committed (`725cd88`); the compressed alternative was rejected and was not applied |
| Chapter 5 | Drafted in chat only; source still contains the older prose |
| Chapter 7 | Rewritten before this chat; used as a style reference |
| GPT mentions and unsupported exclusion rationale | Removed across Chapters 1, 2, 4, 7 and 8 and committed (`9644217`) |

## Results of mechanical and numerical checks

- **63 bibliography entries; 54 actually cited and printed.** Nine reserve/unused entries are not in the compiled reference list.
- **41 DOI-bearing entries:** all DOI registry records resolved and identified the intended works. Initial rate-limit responses were retried; they were not treated as missing papers.
- **19 additional published works or books:** verified against official proceedings/publisher records. The remaining three entries are real arXiv technical reports.
- **No missing citation keys, missing internal reference labels, or duplicate labels** were found in active manuscript text.
- **Complete ledger regeneration:** all five models and all three phases reproduced `planning/ledger_v2.json` exactly, with no differences.
- **12 result tables:** numeric cells match the corresponding ledger-based generators. The main robustness table uses the full-layout generator, not the older similarly named generator.
- **13 generated PDF figures:** regenerated into a temporary directory and rendered identically to the checked-in figures at a 1200-pixel comparison resolution. The two inline TikZ diagrams were inspected as source, not regenerated model experiments.
- **Build:** 102 pages, zero LaTeX errors, zero undefined citations/references, seven existing overfull boxes. GPT does not occur in the compiled report.

These checks support the stored numbers and graphics. They do not validate interpretations contradicted by those numbers, or declarations about unrecorded historical decisions.

## Publication status and the arXiv concern

| Category | Cited/printed | Entire `.bib` file |
|---|---:|---:|
| Published journal/conference papers | 50 | 59 |
| Standard statistics book | 1 | 1 |
| arXiv technical reports with no peer-reviewed version identified in this check | 3 | 3 |
| Total | 54 | 63 |

The three technical reports are:

1. [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783), `grattafiori2024llama3`.
2. [Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution](https://arxiv.org/abs/2409.12191), `wang2024qwen2vl`.
3. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073), `bai2022constitutional`.

That is **3/54 = 5.6% of the printed references**, not a bibliography dominated by preprints. Technical reports are not peer-reviewed evidence, but the original model reports are legitimate primary documentation for the systems evaluated. Do not replace them with unrelated conference papers merely to change the venue label. If the desired policy is stricter, reconsider the Constitutional AI discussion first; the two model reports document the actual audited systems. The Llama 3 report is broader than the specific Llama-3.2 checkpoints, so exact checkpoint claims should additionally point to the relevant versioned model/configuration documentation.

Several works with arXiv versions are already correctly cited as published papers: CALM at ICLR 2025, Gao and Kreiss at EMNLP 2025, Yang et al. at EACL 2026, and Li et al. at DASFAA 2026. A preprint copy of a published paper does not make the work arXiv-only. Li et al.'s [Springer record](https://link.springer.com/chapter/10.1007/978-981-92-0372-7_2) confirms publication on 10 May 2026, pages 19–34.

## Findings needing attention

The findings below separate confirmed contradictions from interpretations that require more cautious wording or a documented statistical decision. No change to the user's reserved delta_m sign convention has been made or prescribed.

### A01: The headline gender gap is not positive in all five models

**Classification:** Confirmed error.

**Locations:** [frontmatter/abstract.tex:47](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/frontmatter/abstract.tex:47>), [chapters/05_study1_intrinsic.tex:604](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/05_study1_intrinsic.tex:604>), [chapters/05_study1_intrinsic.tex:691](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/05_study1_intrinsic.tex:691>), [chapters/08_conclusion.tex:53](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/08_conclusion.tex:53>)

**Evidence:** The regenerated ledger gives Qwen-2B a benevolent gap of -0.0071 (p=0.00403). Four model gaps are positive; one is negative. Llama-11B p=0.03894 does not meet the stated Bonferroni threshold p<0.01. The figure caption incorrectly says every gap is positive and significant.

**Recommended correction:** Correct the abstract, Chapter 5 caption and summary, and conclusion together. Retain every measured value. Distinguish direction from significance.

### A02: CALM consistency rate is misdefined and the omission rationale is unsupported

**Classification:** Confirmed error.

**Locations:** [chapters/03_measurement_framework.tex:587](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:587>), [chapters/01_introduction.tex:238](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/01_introduction.tex:238>), [chapters/04_experimental_design.tex:586](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:586>)

**Evidence:** The CALM paper defines CR from two judgements under identical, unperturbed conditions. It does not require a third option order. See its Metrics section, PDF page 6, https://proceedings.iclr.cc/paper_files/paper/2025/file/fdca08d371e4b6c031397909e20043bd-Paper-Conference.pdf . If the proposal used a different definition, it must be labelled as a proposal-specific metric rather than attributed to CALM. Deterministic repeated passes would make conventional CR an execution reproducibility check, not an unavailable third-order statistic.

**Recommended correction:** Separate the original CALM definition from any proposal adaptation and state the actual reason it is not separately reported. Update the scope table and linked explanations.

### A03: The anchor figure caption gives the wrong slope sign

**Classification:** Confirmed error.

**Locations:** [chapters/06_study2_extrinsic.tex:196](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/06_study2_extrinsic.tex:196>)

**Evidence:** Independent regression of the original stored ratings gives Llama-90B slopes -0.96790 without an image and -0.87079 with an image. The plotted figure regenerates identically and the chapter body reports -0.97 and -0.87. Its caption instead says the slope becomes positive. The same caption still describes three models although the figure has five.

**Recommended correction:** Rewrite the caption to match the negative slope and the five plotted models. Explain pairwise agreement loss without claiming complete anchor ignoring.

### A04: Reading logits does not establish a bypass of safety alignment

**Classification:** Unsupported interpretation.

**Locations:** [chapters/01_introduction.tex:138](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/01_introduction.tex:138>), [chapters/01_introduction.tex:212](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/01_introduction.tex:212>), [frontmatter/abstract.tex:91](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/frontmatter/abstract.tex:91>)

**Evidence:** The forward pass is performed on instruction-tuned weights. Reading before sampling avoids sampling and text parsing; it does not remove the effects of alignment from the distribution. Arditi et al. show refusal is represented within model activations: https://proceedings.neurips.cc/paper_files/paper/2024/hash/f545448535dfde4f9786555403ab7c49-Abstract-Conference.html . This audit performs no corresponding intervention. The cited alignment papers do not establish that alignment changes only expression and never representations.

**Recommended correction:** Describe the method as observing probabilities before decoding. Remove or qualify the safety-bypass and latent-attitude claims without changing the measurement protocol.

### A05: Visual token bounds are described as a fixed token count

**Classification:** Confirmed error.

**Locations:** [chapters/04_experimental_design.tex:420](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:420>), [chapters/04_experimental_design.tex:258](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:258>)

**Evidence:** The code sets min_pixels=256*28^2 and max_pixels=1280*28^2. These are a range, not equality constraints. The official documentation explains that such settings encode images to a number of tokens within the interval: https://huggingface.co/docs/transformers/v4.57.1/en/model_doc/qwen2_vl#image-resolution-trade-off . Actual equality across different images is not demonstrated by these settings alone.

**Recommended correction:** State that the pixel/token range is bounded. Claim equal sequence lengths only if image_grid_thw or equivalent run evidence establishes them. Review related Chapter 2 and Appendix A claims.

### A06: The stimulus validation statistic is described as the wrong quantity

**Classification:** Confirmed error.

**Locations:** [chapters/04_experimental_design.tex:181](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:181>)

**Evidence:** The stimulus validation summary and figure-generation code define 0.853 and 0.062 as |P(male)-P(female)|. The prose describes 0.853 as probability assigned to one side of the pooled pair. A gap and a one-sided conditional probability are different quantities.

**Recommended correction:** Call the statistic the absolute gender probability gap and retain 0.853, 0.062 and threshold 0.20.

### A07: Production measurements do not retain the raw top ten vocabulary tokens

**Classification:** Confirmed error.

**Locations:** [chapters/04_experimental_design.tex:354](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:354>)

**Evidence:** The production runner calls extract_probs for specified target strings. HFVisionExtractor.extract_probs returns a dictionary for those targets, and the stored rows contain target token probabilities, not a full-vocabulary top-ten dump. Chapter 5 explicitly says production runs stored target tokens alone. Top-ten diagnostics exist in the diagnostic sweep.

**Recommended correction:** Limit the claim to the diagnostic sweep and state accurately what production rows retain.

### A08: The stated unavailability of high-ASI raw data conflicts with the analysis inputs

**Classification:** Confirmed error.

**Locations:** [chapters/03_measurement_framework.tex:534](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:534>), [chapters/06_study2_extrinsic.tex:279](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/06_study2_extrinsic.tex:279>)

**Evidence:** The current loader successfully reads final_anonymised.csv with 281 rows and 172 columns. It uses asi_score and per-query ratings to compute the low-ASI baseline. The same file supports identifying participants above the median; a different raw file is not intrinsically needed for the high group. The median is 2.8181818 and the low group has 148 participants. No high-group baseline was inserted into the manuscript during this audit.

**Recommended correction:** Describe the comparison as not computed within the delivered analysis, unless there is documented evidence of a more specific historical access problem. Do not retain the generic missing-raw-file explanation.

### A09: Claims that the prompt is unchanged contradict the administered prompts

**Classification:** Confirmed error.

**Locations:** [chapters/07_discussion.tex:89](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/07_discussion.tex:89>), [appendices/A_instruments.tex:101](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/appendices/A_instruments.tex:101>)

**Evidence:** Phase 2 changes both image presence and the referent: "this image result" versus "a typical result". Appendix A quotes both and Chapter 4 acknowledges the difference. The comparison therefore does not hold all wording fixed.

**Recommended correction:** Acknowledge the wording change and its potential contribution to the modality contrast; retain the actual prompts.

### A10: Older model counts conflict with the delivered five-model scope

**Classification:** Confirmed error.

**Locations:** [chapters/01_introduction.tex:230](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/01_introduction.tex:230>), [chapters/03_measurement_framework.tex:235](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:235>), [chapters/05_study1_intrinsic.tex:324](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/05_study1_intrinsic.tex:324>)

**Evidence:** The abstract, data and Chapter 4 cover five models. Parts of the introduction still discuss correlation at n=2, while Chapters 6 and 7 report rho=-0.70 for five models. Some three-model descriptions are legitimate subsets, but they are not identified as such; a five-column table caption says all three models.

**Recommended correction:** Update scope descriptions or explicitly label subsets. The independently recalculated five-model Spearman statistic is -0.70, p=0.1881204.

### A11: The discussion incorrectly assigns three GPUs to every large model

**Classification:** Confirmed error.

**Locations:** [chapters/07_discussion.tex:147](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/07_discussion.tex:147>)

**Evidence:** Chapter 4 model specifications give Qwen-72B two H100 GPUs and Llama-90B three H100 GPUs. The discussion says every large model ran on three. Its associated perfectly-confounded argument must distinguish single-device from multi-device execution, rather than an exact shared GPU count.

**Recommended correction:** Correct the hardware description while preserving the demonstrated transfer fault and its controls.

### A12: A half-point tolerance is not equivalent to rounding to the same integer

**Classification:** Confirmed error.

**Locations:** [chapters/03_measurement_framework.tex:582](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:582>)

**Evidence:** The implementation tests abs(r_original-r_reversed_normalised)<=0.5. For example, 3.49 and 3.51 pass that test but round to different integers. Conversely, two values can round to the same integer while differing by more than 0.5. These examples are mathematical checks, not new experimental observations.

**Recommended correction:** Define the tolerance as an absolute difference of at most 0.5. Retain all computed robustness rates.

### A13: The Phase 1B table mislabels t-test p values as exact and rounds some to zero

**Classification:** Confirmed error.

**Locations:** [chapters/05_study1_intrinsic.tex:583](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/05_study1_intrinsic.tex:583>)

**Evidence:** scripts/build_ledger.py calls scipy.stats.ttest_ind on face means. These are t-test p values, not the exact keying permutation test from Phase 1A. Displayed 0.000 values reflect rounding, not zero probability.

**Recommended correction:** Label the test accurately and use a bound such as p<0.001 when a nonzero value rounds below display precision. This changes reporting notation, not the stored results.

### A14: The maximum Qwen coverage change is understated

**Classification:** Confirmed error.

**Locations:** [chapters/05_study1_intrinsic.tex:110](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/05_study1_intrinsic.tex:110>)

**Evidence:** For Qwen-2B, the ledger gives text-only captured mass 0.9102 and noise captured mass 0.8758, a difference of 0.0344. The text says all three Qwen variants change by at most 0.027. The table itself matches the ledger.

**Recommended correction:** Correct the prose maximum while retaining the table. This is one numerical claim that cannot be repaired merely through stylistic wording.

### A15: Results are generalised beyond the evaluated architectures

**Classification:** Unsupported interpretation.

**Locations:** [chapters/06_study2_extrinsic.tex:91](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/06_study2_extrinsic.tex:91>), [chapters/07_discussion.tex:222](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/07_discussion.tex:222>)

**Evidence:** Chapter 6 treats a shared pattern in two models as a property of current visual grounding generally. Chapter 7 correctly limits external validity to five models in two families. Similar passages equate conditional responses with psychological attitudes or declare an entire family unaffected.

**Recommended correction:** State that the pattern occurs in both evaluated large models. Describe architecture mechanisms as interpretations unless tested through an intervention.

### A16: The slope alone cannot diagnose exact scale following or anchor ignoring

**Classification:** Unsupported interpretation.

**Locations:** [chapters/06_study2_extrinsic.tex:210](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/06_study2_extrinsic.tex:210>), [chapters/03_measurement_framework.tex:606](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:606>)

**Evidence:** Ideal following requires both slope -1 and intercept 8; identical raw responses require slope +1 and intercept 0. Llama-11B without images has slope -1.11850 but intercept 5.96071 and robustness 0.000. This explains why direction and pairwise agreement differ; it contradicts an unqualified claim that all smaller models never respond to the scale definition.

**Recommended correction:** Describe slopes with their intercepts or use them as descriptive diagnostics. Retain the robustness result and avoid inferring an internal reading process from slope alone.

### A17: Low captured mass is not a validated refusal detector across all models

**Classification:** Unsupported interpretation.

**Locations:** [chapters/03_measurement_framework.tex:113](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:113>), [chapters/07_discussion.tex:71](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/07_discussion.tex:71>)

**Evidence:** Mass outside a chosen response set can start a refusal, explanation, different formatting, or another continuation. The recorded diagnostic gives evidence for one Llama prompt, while Chapter 5 correctly distinguishes that observation from inference about production models.

**Recommended correction:** Use low response coverage as the direct observation and treat refusal as a supported but limited interpretation. Do not turn the diagnostic into a universal equivalence.

### A18: Permutation inference and multiple-testing assumptions need precise scope

**Classification:** Statistical interpretation requiring a decision.

**Locations:** [chapters/03_measurement_framework.tex:345](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/03_measurement_framework.tex:345>), [chapters/07_discussion.tex:210](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/07_discussion.tex:210>)

**Evidence:** Enumerating every keying assignment eliminates Monte Carlo error but still requires an exchangeability/null argument. Averaging items does not itself establish exchangeability. The Bonferroni threshold is explicitly applied across five Phase 1B models, while combined, hostile and benevolent outcomes and five Phase 1A polarity tests are also discussed. Qwen-72B polarity p=0.01037 exceeds 0.01 before rounding; no correction across these five polarity tests is stated.

**Recommended correction:** State the assumptions and the intended testing families. Distinguish unadjusted Phase 1A results from the corrected Phase 1B results. Do not silently change which results count as significant.

### A19: CFD publication restrictions are stated too absolutely

**Classification:** Confirmed error.

**Locations:** [chapters/04_experimental_design.tex:267](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/chapters/04_experimental_design.tex:267>)

**Evidence:** The official terms require written consent for publication and prohibit redistribution; the FAQ expressly allows publication of a limited sample and describes requesting permission. Thus "forbids republishing images" omits the permission condition. Source: https://www.chicagofaces.org/ . The decision not to reproduce faces remains consistent with a conservative presentation choice.

**Recommended correction:** Describe the actual permission restriction or state simply that the thesis does not reproduce the images. No face images need to be added.

### A20: Appendix D caption describes a superseded table layout

**Classification:** Confirmed error.

**Locations:** [appendices/D_full_tables.tex:51](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/appendices/D_full_tables.tex:51>)

**Evidence:** The caption says the main robustness table reports only tau=0.5, but the current Chapter 6 table contains all three tolerances. Both tables reproduce the same numerical cells.

**Recommended correction:** Correct the cross-description of the two tables without changing their values.

### A21: Reproducibility statements overstate the committed and recorded state

**Classification:** Incomplete provenance.

**Locations:** [appendices/E_reproducibility.tex:31](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/appendices/E_reproducibility.tex:31>), [appendices/E_reproducibility.tex:80](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/appendices/E_reproducibility.tex:80>)

**Evidence:** The final audit state is not identified by a commit, and the external audit repository contains uncommitted code and untracked Phase 1B and small-model outputs. No cluster lockfile is available, despite precise software versions being stated in Chapter 4. scripts/make_tables.py prints fragments and includes an older t_s2_rr layout; the source was checked against the corresponding full-layout generator. Appendix B is currently a validation table without its planned diagnosis prose or minimal reproduction. Three registry rows lack job identifiers, including the grouped Phase 1B jobs.

**Recommended correction:** Complete the provenance record and qualify exact environment claims. Keep missing identifiers explicit. Do not claim that every prose number is automatically generated merely because table/figure generators exist.

### A22: Submission placeholders and layout defects remain

**Classification:** Submission completeness.

**Locations:** [frontmatter/declaration.tex:12](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/frontmatter/declaration.tex:12>), [frontmatter/ai_statement.tex:27](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/frontmatter/ai_statement.tex:27>), [frontmatter/acknowledgements.tex:15](</Users/hunghuynh/Library/UQ /UQ Semester 4/REIT4841/Thesis_report/frontmatter/acknowledgements.tex:15>)

**Evidence:** The compiled report still contains these three placeholders. The build has seven overfull boxes, including a Chapter 5 table overrun of 179.54002 pt. It also reports the known duplicate front-matter page destination warning. The body otherwise builds without errors or undefined references.

**Recommended correction:** The author should complete the declarations. Repair table layout and front-matter numbering separately from prose editing.

## Bibliographic metadata issues and apparent mismatches

No wholly invented paper or DOI was identified among the 63 entries. The following distinctions prevent introducing new errors while trying to fix the bibliography:

- **Gao and Kreiss page range:** Crossref currently reports 6745–6761, while the [ACL Anthology record](https://aclanthology.org/2025.emnlp-main.342/) and the downloaded publisher PDF give 6734–6750. The current BibTeX range agrees with the publisher PDF. Keep it; record the registry discrepancy rather than automatically replacing it.
- **Efron and Tibshirani:** the book is real. The current publisher catalogue describes the 1994 issue/reprint, while the bibliography cites the conventional 1993 original. Confirm which edition is being cited before changing the year. This is an edition clarification, not a fabricated source.
- **Tjuatja et al.:** a Crossref surname field says “Talwalkwar”. The bibliography's “Talwalkar” should not be overwritten from this metadata without checking the publisher PDF.
- **Missing completeness fields:** several published proceedings entries omit URLs, DOIs or page ranges even where official records supply them. Examples include Flamingo, the alignment paper, RMSNorm and VisoGender. This is incomplete metadata, not evidence that the papers are nonexistent.
- **Old audit notes are not authoritative:** `planning/references_audit.md` contains historical sections that still call Li et al. unpublished/accepted-only, retain old wrong page ranges and describe an earlier 62-entry bibliography. Later corrections are appended, but the summary is stale. Use the current per-entry evidence matrix rather than treating every historical statement as current.

## Recommended correction order

1. Correct headline factual contradictions: A01, A03, A06 and A14.
2. Correct methodological attributions and implementation claims: A02, A04, A05, A07 and A09.
3. Resolve the missing-data rationale and stale scope statements: A08, A10 and A11.
4. Clarify statistical reporting and interpretation: A12, A13, A15 to A18. Preserve the reserved delta_m interpretation pending the supervisor's decision.
5. Finish provenance, declarations, captions and layout: A19 to A22.
6. Complete bibliography metadata from the verified published records without replacing the small number of relevant technical reports indiscriminately.

## Evidence files

- `reference_checks.json`: all 63 entries, whether cited, publication classification, primary record and retrieved DOI metadata.
- `numerical_checks.json`: zero ledger differences and independently recomputed anchor slopes.
- `table_checks.json`: per-table comparison with numerical generators.
- `figure_checks.json`: per-figure rendered comparison.
- `findings.json`: structured findings, locations, evidence and recommended actions.

No correction or commit is included in this audit. The report is numerically reproducible from its stored data, but it is not yet ready to be described as free of unsupported claims or internal contradictions.
