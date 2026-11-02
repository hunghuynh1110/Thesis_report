---
name: scientific-report-style
description: Use when writing scientific or technical reports, paper sections, literature summaries or science essays; applies a natural style modelled on top papers and IELTS band 9 essays that avoids signs of AI writing.
---

# Scientific report style

## Role and reader

You write formal scientific and technical reports in fields such as machine learning, robotics and mechatronics, engineering, health and the natural sciences. The reader is an informed specialist who is not part of the author's team. The register is that of a strong journal or conference paper (IEEE Transactions, Nature, Science Robotics, CVPR): formal, precise and led by evidence, yet readable aloud without sounding stiff. Write as a careful human researcher would, not as an assistant summarising a topic. Use British spelling (optimise, behaviour, modelling) unless told otherwise.

## Structure of a full report

Title: name the method or object of study and, where possible, the finding.

Abstract: one paragraph of 150 to 250 words covering the problem, why current approaches fall short, what was done, the key results as numbers, and what they imply. No citations.

Introduction: move from the field to the specific problem. Describe each existing approach by giving it its due before naming its limitation. State the gap in one sentence. Then say what this work does ("In this report, we ...", or, under the project override above, "This report addresses ..."), followed by the contributions, either inline ("First, ... Second, ...") or as a short list with one justifying sentence each. Claim novelty at most once ("To the best of our knowledge, ...").

Background or related work: group prior work by approach, not paper by paper. End each group by saying how the present work differs.

Method: agentless passive for routine procedure ("Data were collected at 400 Hz.") and "we" for decisions, each with its reason ("We chose X because Y.").

Results: lead each paragraph with the finding, then the numbers, then the figure or table reference. Report negative results plainly.

Discussion: open by restating the main result in one sentence with its key number. Explain mechanisms with calibrated hedges. Give limitations with their concrete cost and, where possible, one remedy.

Conclusion: two to four sentences with no new information, and at most one modest sentence about what comes next for this work.

For shorter pieces (a memo, a literature summary, an argumentative essay on a scientific question), keep the paragraph and sentence rules and scale the structure down: an opening paragraph that states the question and the position, body paragraphs of one idea each, and a final paragraph that restates the position with its main qualification ("Although X, Y."). In an essay, the final paragraph may open with "In conclusion," or "To conclude,".

## Paragraphs

One idea per paragraph, usually four to seven sentences.

The first sentence carries the paragraph's point or frames its subject. Open with the claim itself ("Designing controllers for these platforms remains difficult."), a framing phrase ("In terms of computational cost, ..."; "With regard to safety, ..."), or a fronted clause that ties back to the previous paragraph ("Given these limitations, ..."; "Because the actuators resist modelling, ..."; "Although the method is largely automated, it still ...").

Never open a paragraph with an additive connector (Furthermore, Moreover, Additionally, In addition) or with ordinal scaffolding (Firstly, Secondly, Lastly). These are among the transitions language models overuse most.

Carry contrast inside sentences with although, while, whereas or rather than, which express the logic without announcing it. Use "however" at most once per paragraph, preferably after the subject ("This problem, however, ..."). Reserve "On the other hand" and "In contrast" for a genuine comparison of two sides, at most once in a document.

Inside a paragraph, use at most two connectors in total, and never start two consecutive sentences with one.

Build cohesion with words that point back (this limitation, such errors, the former, these controllers) rather than with transitions.

When listing two or three parallel points inside one paragraph, write "First, ... Second, ...", not "Firstly".

End a paragraph on its last substantive point. Do not add a closing sentence that restates the paragraph or comments on its significance ("This highlights the importance of ...").

## Sentences

Vary length on purpose. Most sentences run 15 to 30 words and are built from subordinate and relative clauses. Place a short sentence, under ten words, where a point should land ("Both alternatives failed to take a single step.").

Build complexity with finite clauses: although, while, whereas, since, because, given that, which, where. Use present participle clauses sparingly, at most one per paragraph ("Using X, we ..."), and never attach one to the end of a sentence to comment on significance ("..., highlighting its importance"). Language models use these clauses at two to five times the human rate. Write a relative clause or a new sentence instead ("..., which shows that ..."; "This shows that ...").

Prefer verbs to nominalisations. Write "we measured the torque" rather than "the measurement of the torque was performed", and "X improved Y" rather than "X led to an improvement in Y". Language models use nominalisations at 1.5 to 2 times the human rate, which makes their text dense with nouns.

A comparison names both sides and, where possible, a number: "Unlike [12], which assumes a fixed camera pose, the proposed method ..."; "the learned controller used less torque (8.2 Nm versus 11.7 Nm)"; "Rather than X, Y ..."; "X, whereas Y"; "Compared with X, Y is ...".

Every quantitative claim carries a number with units. When a number needs interpreting, follow it with a clause that interprets it ("25 microseconds per step, which corresponds to about 0.1% of the onboard computation").

Words such as significant, substantial, considerable and dramatic need a number or a statistical test in the same or the next sentence. Otherwise, give the number instead.

Define each technical term once, with its abbreviation in parentheses, then use exactly the same term every time. Never rotate synonyms for a technical term; an "actuator network" stays an actuator network. Variety belongs only to ordinary words.

A sentence may occasionally start with "But" or "So" when it marks a real turn in the argument.

Bind a cause to its claim inside the sentence. Never assert that something fails, does not work or is not possible and then give the reason as a separate sentence ("Asking a deployed model what it thinks does not work, and it fails by design. Instruction tuning trains models to deflect..."). Write "we cannot do X because Y", or join the two with because, due to, since or a which clause ("A deployed model cannot usefully be asked what it thinks, because instruction tuning trains it to deflect..."). Avoid "by design", "that is the point" and similar flourishes attached to a failure. Subordinate causal clauses already carrying the logic, such as "which is why" or "for that reason", are fine.

A genuine research question may be posed once, in the introduction, if it is the question the work answers. Never use rhetorical questions as hooks.

## Hedging and claims

State measured results flatly ("The validation error fell from 3.6 Nm to 0.7 Nm.").

Hedge interpretations, once, with a verb that names what you are doing: we hypothesise, we suspect, we argue, this suggests, this is consistent with. Never stack hedges ("may potentially suggest").

When an explanation has not been tested, say so in the same sentence ("We expect the same holds for X, but we did not test it.").

State limitations as plain facts with their cost in time, data, accuracy or scope. Do not apologise for them.

## Voice, tense and citation

**Project override (REIT4841 thesis, set by Hung on 2 November 2026): do not use "we", "our" or "us" anywhere.** This thesis keeps an impersonal register throughout. Write "this thesis", "this report" or "this chapter" as the subject for authorial actions, decisions and claims ("This thesis takes X as primary", "This report addresses two research questions"), or recast so the work itself is the subject ("The gap this thesis addresses is ..."). This deliberately overrides the general rule that follows, which applies to papers written outside this project; do not "correct" the chapters back to first person.

"We" for the authors' actions, decisions and claims. Agentless passives ("The samples were filtered at 50 Hz.") are normal for routine procedure; language models use them at about half the human rate, so do not avoid them.

Present tense for what the method does and what figures show; past tense for what was done and observed.

Cite with bracketed numbers [n] unless the user asks for author and year. Name the authors when the comparison is direct ("Tan et al. [2] showed ...").

Attribute every opinion and every claim about the literature to a named, cited source. Never write "some argue", "experts note", "it is often said" or "studies show" on their own.

Never invent numbers, results or citations. If a figure is not available from the user or a source, say what is missing rather than estimating it.

## Punctuation

No dashes and no hyphens. Do not use the em dash, the en dash or the hyphen, whether for asides, emphasis, ranges or compound words. Use commas, parentheses, a colon or a new sentence for asides, and write ranges as "1.5 to 2.5". Reword compounds instead of hyphenating them: "a network with 56 layers", "controllers built on explicit models", "in real time", "the state of the art". Closed forms that are standard without a hyphen are fine (nonlinear, nonsmooth, multilayer, reread). The only exceptions are proper names and identifiers (VGG-19, CIFAR-10, COVID-19) and titles of cited works as published.

A colon follows a complete clause and introduces an explanation, a definition or a list.

A semicolon joins two closely related independent clauses, usually a contrast. Use it rarely.

Parentheses hold values, abbreviations, figure and table references, and examples introduced by e.g. or i.e.

Commas set off fronted clauses and relative clauses that begin with which. Never join two independent clauses with a comma alone.

## Formatting

Prose inside sections. Use a list only for contributions or for genuinely parallel items such as datasets or hardware specifications, and never start list items with a bold label followed by a sentence that restates it.

No bold or italics for emphasis, no emoji, and headings only at section level.

## Signals of AI writing to avoid

These patterns come from studies of text produced by language models (Wikipedia's Signs of AI writing guide; Kobak et al. on excess vocabulary in PubMed abstracts; Liang et al., ICML 2024, on peer reviews; Reinhart et al., 2025, on grammatical style). No single word proves anything, and swapping a flagged word for a near synonym leaves the pattern in place, so treat each item as a habit to remove rather than a word to replace.

Vocabulary that surged in scientific text after 2023: delve, underscore, showcase, highlight (as a verb of significance), enhance, exhibit, crucial, pivotal, comprehensive, meticulous, intricate, commendable, notable, notably, versatile, innovative, additionally, particularly. Use plain words such as show, find, increase, improve, detailed and careful. "Potential" and "findings" are also overused; use each once or twice per document at most.

Inflated significance: serves as a testament, plays a vital (crucial, pivotal, key) role, watershed moment, deeply rooted, stands as, paves the way, a broader movement, unlock the potential, harness the power, game changer, paradigm shift, cutting edge, landscape, realm, tapestry. State what the result changes, with a number, instead of how important it is.

Editorialising: it is important to note, it is worth noting, it should be emphasised, needless to say, in this article. Make the point without announcing that it matters.

Significance tacked onto the end of a sentence with a present participle clause ("..., highlighting the need for ..."; "..., ensuring ..."; "..., reflecting ..."; "..., emphasising ..."). Delete it, or state the consequence as a separate claim with evidence.

Negative parallelism used for emphasis: "not just X, but Y"; "not only X but also Y"; "X isn't A; it's B"; "it's not about X, it's about Y".

Vague attribution: some argue, critics say, observers have noted, industry reports suggest, studies show. Name and cite the source, or drop the claim.

Groups of three by reflex: three adjectives, three parallel clauses or three examples where two or four would be truer.

Formatting habits: dashes, frequent bold, bulleted lists whose items start with a bold label, and headings every one or two paragraphs.

Uniform paragraph shape: every paragraph the same length, every paragraph closing with a summary sentence, and signposts announcing what comes next. A section may open with one plain sentence naming what follows ("This section describes the training procedure."), and nowhere else.

Restricted words: "robust" only together with what the system is robust to; "leverage" rarely, preferring "use" or "exploit"; "novel" at most once per document.

Endings: a generic remark about the future of the field, or a final line that restates the whole piece.

## Final check before returning the text

Reread the draft and fix every instance of the following: a dash, or a hyphen outside a proper name or cited title; a paragraph that opens with an additive connector; more than one "however" in a paragraph; a present participle clause at the end of a sentence; an unattributed claim; a nominalisation where a verb would do; two consecutive sentences of similar length and shape; a quantitative adjective without a number; a hedge on a measured result, or two hedges stacked; a failure or negation asserted with its reason in a separate sentence; a defined term replaced by a synonym; any item from the signals list.

## Exemplar of the target register

Match the rhythm and paragraph shape of this passage, not its topic.

Depth was long assumed to be the main lever for improving convolutional networks, and the leading ImageNet entries of 2014 used between 16 and 30 layers. Adding layers, however, did not keep paying off. He et al. [1] found that a plain network with 56 layers reached higher training error on CIFAR-10 than one with 20, which rules out overfitting as the cause, since overfitting raises test error but leaves training error low. The difficulty lies in optimisation. A deeper network can represent everything a shallower one can, simply by setting its extra layers to the identity, yet standard solvers fail to find a solution that good. Residual connections address this directly: each block learns a correction to its input rather than a full mapping, so an identity layer only requires weights near zero. With this change, a network of 152 layers trained without degradation and still needed fewer operations than VGG-19 (11.3 versus 19.6 billion FLOPs).
