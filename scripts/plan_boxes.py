#!/usr/bin/env python3
"""
Comment the plan boxes out of the build, or put them back.

The plan boxes are working notes: what each unwritten section must contain,
which decisions are open, which numbers still need checking. They belong in the
source, where they sit next to the prose they describe, and not in a PDF that
goes to a supervisor or an examiner.

Setting \\showplanfalse already keeps them out of the PDF, but it leaves them one
switch away from appearing. Commenting them out removes that risk, and the notes
stay fully readable in the editor.

    python3 scripts/plan_boxes.py hide      # comment them out
    python3 scripts/plan_boxes.py show      # put them back
    python3 scripts/plan_boxes.py status    # count, change nothing

Round trips exactly: 'hide' prefixes each line of a block with "% ", and 'show'
strips that prefix back off, so running one then the other leaves the files
byte-identical. Verified by the --check flag on 'hide'.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ["chapters/*.tex", "appendices/*.tex", "frontmatter/*.tex"]
PREFIX = "% "
BEGIN, END = "\\begin{plan}", "\\end{plan}"


def files() -> list[Path]:
    out: list[Path] = []
    for p in PATTERNS:
        out += [Path(f) for f in sorted(glob.glob(str(ROOT / p)))]
    return out


def hide(text: str) -> tuple[str, int]:
    """Prefix every line of every plan block with a comment marker."""
    out, n, inside = [], 0, False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if not inside and stripped.startswith(BEGIN):
            inside, n = True, n + 1
        if inside:
            out.append(PREFIX + line if line.strip() else PREFIX.rstrip())
            if stripped.startswith(END):
                inside = False
        else:
            out.append(line)
    if inside:
        raise SystemExit("unbalanced plan block: a begin without its end")
    return "\n".join(out), n


def show(text: str) -> tuple[str, int]:
    """Strip the comment marker back off a commented plan block."""
    out, n, inside = [], 0, False
    for line in text.split("\n"):
        bare = line[len(PREFIX):] if line.startswith(PREFIX) else (
            line[1:] if line.rstrip() == PREFIX.rstrip() else line)
        if not inside and line.startswith(PREFIX) and bare.lstrip().startswith(BEGIN):
            inside, n = True, n + 1
        if inside:
            out.append(bare)
            if bare.lstrip().startswith(END):
                inside = False
        else:
            out.append(line)
    if inside:
        raise SystemExit("unbalanced commented plan block")
    return "\n".join(out), n


def count(text: str) -> tuple[int, int]:
    live = sum(1 for l in text.split("\n") if l.lstrip().startswith(BEGIN))
    hidden = sum(1 for l in text.split("\n")
                 if l.startswith(PREFIX) and l[len(PREFIX):].lstrip().startswith(BEGIN))
    return live - hidden, hidden


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    if mode not in {"hide", "show", "status"}:
        print(__doc__)
        return 2

    total = 0
    for f in files():
        original = f.read_text()
        if mode == "status":
            live, hidden = count(original)
            if live or hidden:
                print(f"  {f.relative_to(ROOT)}: {live} visible, {hidden} commented")
            total += live + hidden
            continue

        new, n = (hide if mode == "hide" else show)(original)
        if mode == "hide":
            # The inverse must restore the file exactly, or nothing is written.
            back, _ = show(new)
            if back != original:
                raise SystemExit(f"{f}: hide is not reversible, refusing to write")
        if new != original:
            f.write_text(new)
        if n:
            print(f"  {f.relative_to(ROOT)}: {n} block{'s' if n != 1 else ''}")
        total += n

    verb = {"hide": "commented out", "show": "restored", "status": "found"}[mode]
    print(f"\n{total} plan blocks {verb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
