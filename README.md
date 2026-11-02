# Thesis report — Auditing VLM Perception of Gender Bias using Human Sexism Scales in Image Search

REIT4841 final thesis, Gia Hung Huynh, supervised by Prof Gianluca Demartini
(The University of Queensland). LaTeX source, synced with Overleaf.

Experiment code and result files: [`hunghuynh1110/VLM_Audit`](https://github.com/hunghuynh1110/VLM_Audit).

## Status

**Outline stage.** Every section contains a blue *Plan* box that says what the
section must argue, which references to cite, which numbers to report and which
figure goes there. Equations, tables (with verified numbers) and figure
placeholders are already in place. Start with [`planning/OUTLINE.md`](planning/OUTLINE.md).

## Layout

```
main.tex                 working build: shared body + plan boxes VISIBLE
supervisor.tex           clean build: shared body + plan boxes HIDDEN (circulate this)
body.tex                 the document body, shared by both so they cannot drift apart
preamble.tex             packages, notation macros, plan-box switch (\showplantrue / \showplanfalse)
frontmatter/             title page, letter to Head of School, declaration, AI statement,
                         acknowledgements, abstract (write last), notation
chapters/                01–08, one file per chapter
appendices/              A instruments · B fault report · C run registry · D full tables · E reproducibility
references.bib           49 planned (core) + 13 reserve entries, all verified
figures/                 final figures go here (vector PDF preferred)
planning/                OUTLINE.md, references_audit.md, facts_ledger.md, ledger.json
```

## Overleaf

1. Overleaf → **New Project → Import from GitHub** → choose this repository
   (GitHub synchronisation needs an Overleaf plan that includes it; your UQ
   account may already have one).
2. Overleaf compiles `main.tex` with pdfLaTeX and runs biber automatically.
   To circulate a clean PDF, set Menu -> Main document -> `supervisor.tex`
   and recompile; switch back to `main.tex` to keep working.
3. Overleaf syncs with the **`main`** branch only. Before anyone pushes to GitHub
   from outside Overleaf, use *Menu → GitHub → Push Overleaf changes to GitHub*
   first; after a push from outside, use *Pull GitHub changes into Overleaf*.
   If both sides changed, Overleaf pushes its version to a new branch for you to
   merge.

## Local build

```
latexmk -pdf main.tex
```

## Writing workflow

Fill sections in this order: Ch 3 → 4 → 5 → 6 → 2 → 7 → 1 → 8 → abstract. For
each section, write under the plan box, keep the equations and tables, swap
each `\plannedfigure{...}` for the real `\includegraphics`, then delete the plan
box. They are **commented out** in the chapter files, so they are readable in
the editor beside the prose they describe and never reach the PDF:

    python3 scripts/plan_boxes.py status   # how many, and where
    python3 scripts/plan_boxes.py show     # put them back in the build
    python3 scripts/plan_boxes.py hide     # take them out again

`hide` refuses to write unless its own inverse restores the file exactly, so
the round trip is safe. While they are showing, `supervisor.tex` still gives a
clean PDF; `\showplanfalse` is the default in `preamble.tex` and governs the
scaffolding that is not a plan box.

A known data gap is written `\gap{not reported}`, which shows as a red to-do
in the working build and as an italic statement in the clean build, so a
circulated PDF never shows `[fill]`.
