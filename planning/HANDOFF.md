# Handoff: rewriting the prose of this thesis

Paste everything below this line into the new chat as your first message.

---

## What you are working on

I am finishing an undergraduate thesis for UQ course REIT4841, due **9 November 2026**.
Title: *Auditing VLM Perception of Gender Bias using Human Sexism Scales in Image Search*.

- Thesis source (LaTeX): `~/Library/UQ /UQ Semester 4/REIT4841/Thesis_report`
  Note the space after `UQ` in the path. Quote it.
- Remote: `github.com/hunghuynh1110/Thesis_report`, branch `main`, currently at `58c3adf`.
- Overleaf is connected to that GitHub repo. I pull into Overleaf manually. Do not touch Overleaf.
- Audit code and data: `~/Code/VLM_Audit`. **Read-only for you.**

The report is **content-complete at 102 pages** and builds clean. Chapters 1 to 8, five
appendices, abstract, bibliography. **I do not want new analysis, new results, or new
sections.** I want the *prose rewritten* in a style I prefer.

## Your job

Rewrite the writing, chapter by chapter, when I ask for a specific chapter or section.
Do not rewrite anything I have not asked for.

### The one inviolable rule

**Never change a number, a citation key, a cross-reference, or a label.**

Every figure in this report was computed from real experiments. If you alter `0.900` to
`0.9`, or drop a `\cref`, or invent a statistic to make a sentence flow, you have broken
the thesis. After every edit, verify mechanically rather than by eye:

```bash
python3 - <<'EOF'
import re, subprocess
old = subprocess.run(['git','show','HEAD:chapters/07_discussion.tex'],
                     capture_output=True, text=True).stdout
new = open('chapters/07_discussion.tex').read()
strip = lambda t: re.sub(r'(?m)^%.*$', '', t)
for name, pat in [('numbers', r'\d+\.?\d*'),
                  ('cites',   r'\\cite\{([^}]*)\}'),
                  ('crefs',   r'\\cref\{([^}]*)\}'),
                  ('labels',  r'\\label\{([^}]*)\}')]:
    a, b = re.findall(pat, strip(old)), re.findall(pat, strip(new))
    print(f'{name:<9} lost {sorted(set(a)-set(b)) or "-"}  added {sorted(set(b)-set(a)) or "-"}')
EOF
```

Anything in `lost` or `added` other than `-` means stop and fix it before committing.

### The style I want

I chose the model myself. Follow the conclusion of **Forster et al., "SVO: Fast
Semi-Direct Monocular Visual Odometry", ICRA 2014**, Section VIII. PDFs of nine IEEE,
ICRA, IROS and Science Robotics papers are in `reading/ieee_icra/` (gitignored) if you
want to read the register directly.

That conclusion is one paragraph of five sentences running five moves:

1. Name the claim. *"In this paper, we proposed X that is [comparative claim]."*
2. Give the mechanism as a negative. *"The gain in X is due to the fact that Y is not required."*
3. Supply the positive counterpart. *"Instead, Z is used, which is based on W."*
4. Name the case it suits, with one figure. *"X is particularly useful for A as it [number]."*
5. Fuse two contributions. *"A, combined with B, provides C in conditions D."*

Sentences run 14 to 25 words. Flat assertions. **No hedging.** No "may", "suggests",
"appears to". No enumerated contribution lists. Chapter 7 (`chapters/07_discussion.tex`)
and section 1.4 have already been rewritten this way; read chapter 7 first to see the
target before touching anything else.

### Hard style constraints for this project

These override any general style advice, including your own defaults.

- **Never use "we", "our" or "us".** Write "this thesis", "this report", "this chapter",
  or recast so the work is the subject. This is non-negotiable and applies everywhere.
- **No dashes and no hyphens.** No em dash, en dash, or hyphen, including in compound
  words. Write "non commercial", "first token probabilities", "1.5 to 2.5". The only
  exceptions are proper names and identifiers: `Llama-3.2-Vision`, `Qwen2-VL`, `GPT-4o`,
  `Phase~1B`, and titles of cited works.
- **British spelling**: optimise, behaviour, modelling, quantisation.
- **Avoid "rather than".** The previous draft used it in 12% of all sentences, which I
  disliked. When you need a contrast, vary it: a semicolon, a full stop, `not X: Y`,
  `instead of`, `and not`. Do not pick one replacement and use it everywhere.
- Do not open a paragraph with Furthermore, Moreover, Additionally, Firstly, Secondly.
- Do not end a sentence with a participle clause of significance: "..., highlighting the
  need for", "..., ensuring", "..., reflecting".

A fuller style guide lives at `.claude/skills/scientific-report-style/SKILL.md`. Read it,
but know that I found parts of it miscalibrated against real IEEE papers: it bans
connectors and trailing participles that those papers use freely, and it pushed sentences
shorter than the venues actually write. The SVO model above wins where they conflict.

## Traps that have already cost this project real time

1. **There are two copies of the audit code.** `~/Library/UQ /UQ Semester 4/REIT4841/VLM_Audit`
   is **stale**: three models, no Phase 1B. The real one is `~/Code/VLM_Audit`: five models,
   three phases. Everything in the report is based on the real one. A fact read from the
   stale checkout will be wrong and will look plausible. This caused a chapter to be drafted
   against the wrong scope once already.

2. **`planning/ledger_v2.json` is the only source of truth for numbers.**
   `planning/ledger.json` and `planning/facts_ledger.md` are superseded and marked so. If
   you need to check a figure, read `ledger_v2.json` or regenerate it with
   `~/Code/VLM_Audit/.venv/bin/python scripts/build_ledger.py`.

3. **The plan boxes are commented out on purpose.** Roughly 69 `% \begin{plan}` blocks hold
   my working notes. They must stay commented so they never reach a PDF a supervisor or
   examiner sees. `scripts/plan_boxes.py status` reports them; do not uncomment them and do
   not delete them.

4. **Preserve the commented blocks and tables byte for byte when rewriting a file.** The
   safest method is to rebuild the file programmatically: keep the original line ranges for
   the plan boxes and any table environment, and substitute only the prose blocks. Retyping
   a 14 row table by hand will introduce an error.

5. **Do not trust an incremental build log.** `latexmk` writes the real log to `main.log`,
   not to wherever you redirected stdout. I once read "zero overfull boxes" from a six line
   redirect file when there were six.

## Build and check

```bash
cd ~/Library/UQ\ /UQ\ Semester\ 4/REIT4841/Thesis_report
latexmk -pdf -interaction=nonstopmode main.tex
grep -cE '^! ' main.log                                      # must be 0
grep -cE 'Citation .*undefined|Reference .*undefined' main.log  # must be 0
grep -c '^Overfull' main.log                                 # currently 7
pdfinfo main.pdf | grep Pages                                # currently 102
```

Commit each chapter separately with a message saying what changed and what was verified.
Do not push unless I ask.

## State of the report

| Part | Words | State |
|---|---|---|
| Ch 1 Introduction | 2239 | §1.4 rewritten in the SVO form; rest original |
| Ch 2 Background | 4614 | original |
| Ch 3 Measurement framework | 4275 | original |
| Ch 4 Experimental design | 5155 | original; §4.1 has one paragraph I edited myself, leave it |
| Ch 5 Study 1 | 5061 | original |
| Ch 6 Study 2 | 3151 | original |
| Ch 7 Discussion | 2236 | **fully rewritten in the SVO form: read this first** |
| Ch 8 Conclusion | 884 | original |
| Appendices A to E | | complete except three job IDs |
| Abstract | 547 | written, 2.5 to 3.0 minutes read |

## Known gaps, which are mine to fill, not yours

- `frontmatter/declaration.tex`, `frontmatter/ai_statement.tex`,
  `frontmatter/acknowledgements.tex` are placeholders.
- Three Bunya job IDs in `appendices/C_run_registry.tex` are marked `\datagap`.
- Appendix E cites a `\datagap` commit hash because the audit repo's final state is not
  yet committed.
- Seven overfull boxes: four in chapter 5, one in chapter 1, one in chapter 6, and one of
  5.6pt in appendix E. The largest is 179pt, about 6.3cm, in a chapter 5 table whose five
  numeric columns no longer fit the text width.
- One open question of substance, **D2**: the sign convention for δ_m. Chapter 6 is
  written on the assumption that δ_m < 0 means more bias-perceiving than low-ASI humans.
  If my supervisor says otherwise, the interpretation in §6.5 to §6.7 inverts. Do not
  change it on your own judgement.

## Where to start

Read `chapters/07_discussion.tex` and section 1.4 of `chapters/01_introduction.tex` first.
Those are the target style. Then tell me which chapter you think is furthest from it, and
wait for me to pick one.
