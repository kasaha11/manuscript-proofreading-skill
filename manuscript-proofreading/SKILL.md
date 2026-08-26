---
name: manuscript-proofreading
description: Final-stage proofreading of an ACCEPTED medical manuscript (not peer review) — checks numerical consistency, statistical consistency, table/figure structure, terminology direction, Methods–Results agreement, and Annals of Coloproctology (ACP) house style (decimal places, P-value/percentage notation, italics, references, ethics statements), then outputs PDF-ready annotation comments with MUST-FIX/OPTIONAL priority. Use whenever the user (a journal editor) asks to proofread, proof-check, do a final check on, or find errors/inconsistencies in an accepted manuscript, galley proof, or camera-ready PDF before publication — including requests like "이 논문 프루프 봐줘", "출판 전 최종 점검", "숫자 일치하는지 확인", or "PDF 코멘트 만들어줘" for a manuscript. Do NOT use this for a full peer review of a submitted (not-yet-accepted) manuscript — that is a different task with different scope.
license: MIT
compatibility: Requires Python 3.8+ for scripts/verify_table.py and the ability to view PDF pages as images (for figure/table inspection). Works in Claude Code, Claude.ai, OpenAI Codex, and any Agent Skills-compatible agent; see README.md for ChatGPT Custom GPT setup.
metadata:
  version: "2.0.0"
  authors: "Soo Young Lee (Chonnam National University, Colorectal Surgery; original); Sanghee Kang (Korea University; revision)"
  repository: https://github.com/kasaha11/manuscript-proofreading-skill
  domain: medical-publishing
  house-style-default: Annals of Coloproctology
---

# Manuscript Proofreading (Final Proof Stage)

You are assisting a journal editor with **final proofreading of an accepted medical
manuscript**. This is explicitly **not** a new peer review — do not challenge study
design, request new analyses, or evaluate novelty/importance. The job is to catch
errors, inconsistencies, ambiguities, and presentation problems that should be fixed
before publication, and to produce comments ready to paste into the PDF.

## Bundled resources

- `scripts/verify_table.py` — deterministic checker for percentages, subgroup sums,
  CI shape, CI-vs-P consistency, P-value range, cross-location rounding consistency,
  and ACP-style P-value/percentage notation. Use it instead of mental arithmetic
  (see Working Rule 1).
- `tests/sample_checks.json` + `tests/run_tests.py` — worked fixture covering every
  check type (with expected MATCH/FLAG). Use the fixture as a copy-paste template
  for `checks.json`; run `python3 tests/run_tests.py` after editing the script.
- `references/verify_table_schema.md` — full input schema and worked examples for
  the script above. Read this before building your first `checks.json` in a session.
- `references/acp_house_style.md` — Annals of Coloproctology (ACP) house style rules
  (decimal places, P-value/percentage notation, italics, abbreviations, references,
  tables/figures, required statements, article-type limits). This is the **default**
  house style (see below); read it once per session before applying Section 2's
  house-style checks.

## Before starting: confirm settings

Infer these from context whenever possible and state your assumptions in the output;
only stop to ask if the manuscript file itself is missing or unreadable:

- **Manuscript file(s):** main PDF proof, plus any supplementary files. If a
  supplementary file is referenced in the text but not provided, say so explicitly —
  do not guess its contents.
- **Comment language:** KO or EN for the PDF annotation text itself. Default: infer
  from authorship (Korean corresponding author/institution → Korean; otherwise
  English; multinational or uncertain → English). The "Why it matters" explanation to
  the editor is always in Korean.
- **Journal house style:** defaults to **Annals of Coloproctology (ACP)** —
  `references/acp_house_style.md` — since that is this skill's primary use case. If
  the editor names a different journal or supplies different rules, use those
  instead and do not apply the ACP file. If the editor says to skip house-style
  checking entirely, only flag inconsistencies **within** the manuscript.

## Working rules (non-negotiable, apply throughout)

1. **Calculate, don't estimate.** Never do this arithmetic mentally. For the check
   types covered by `scripts/verify_table.py` — percentage vs. numerator/denominator,
   subgroup counts vs. a reported total, CI internal shape, CI-vs-P-value
   significance consistency, P-value range, cross-location rounding consistency, and
   (when applying ACP house style) P-value/percentage notation — build a
   `checks.json` (see `references/verify_table_schema.md`) from values you've
   already quoted verbatim, and run the script:

   ```bash
   python3 <this skill's directory>/scripts/verify_table.py checks.json
   ```

   Use the **absolute path** to the script (the skill directory is not the working
   directory). Write `checks.json` to a scratch location, not into the skill folder.
   In a ChatGPT Custom GPT / Project, the script is an uploaded knowledge file:
   run it from `/mnt/data/verify_table.py` with the Code Interpreter (see README.md).

   Do this **per table/section**, not one number at a time — extract every
   arithmetic relationship (and, for house style, every P-value/percentage's exact
   printed notation) in that table first, then run once. Every `FLAG` becomes a
   candidate finding; use the script's own `detail` and `computed` fields as the
   basis for the "Why it matters" explanation and the shown calculation. Every
   `MATCH` needs no finding. A `FLAG [Input error]` is not a manuscript finding — it
   means the check itself was malformed; fix the entry and re-run. For arithmetic the script doesn't cover (e.g.
   recomputing a mean from raw listed values, unit conversions), run a short Python
   snippet and still show inputs and result.
2. **Quote verbatim.** Every finding must include the exact text/number/table cell as
   it appears in the PDF, before the explanation. If a value can't be read reliably
   (low-res scan, cropped image, overlapping text), say so — never infer it.
3. **No re-analysis requests.** A correction must be resolvable by clarifying wording
   or fixing a reported value. Never ask the authors to re-run a different statistical
   method, add an analysis, or redesign anything. If a discrepancy can't be resolved
   by clarification alone, label it "Verification required — editor decision" and
   leave the call to the editor.
4. **Process systematically.** Go table by table, then figure by figure, in document
   order. Inspect figures and graphical abstracts **visually** — do not rely on
   extracted text alone for anything visual.
5. **Never fabricate.** No invented values, page numbers, or references. Missing
   information is reported as missing, not filled in. Do not web-search to verify
   references unless the editor explicitly asks.

## Scope of proofreading

Read the entire manuscript: title, abstract, main text, Methods, Results, tables,
figures, figure legends, footnotes, references, and supplementary materials.

**Numerical consistency** — numbers, percentages, denominators, subgroup totals,
event counts, means/medians, ranges, missing-data counts, sample sizes; recompute
percentages/totals/sums; check the same value across abstract/text/tables/figures/
graphical abstract/supplement; check rounding consistency.

**Statistical consistency** — P-values plausible and in valid range; HR/OR and 95% CI
mathematically and directionally consistent with the P-value and text; copy-paste or
mismatched P-values; correct risk/protective direction; clear reference categories and
comparison direction; for multi-level categorical variables, whether it's clear
whether a single HR/OR is ordinal or category-specific (flag as a **reporting**
clarification only); variables in multivariable models consistent with the
variable-selection process in Methods (clarification only); statistical test named in
Methods matches what's actually reported. Do not demand a different method just
because one exists.

**Table structure** — headings, subheadings, indentation, hierarchy, denominators,
footnotes; mutually exclusive categories with correct totals; whether one overall
P-value should replace several for complementary categories; whether missing data
explain varying denominators; units/abbreviations/reference categories/tests defined.

**Figures and graphical abstracts** — axis labels/direction/units/scale, legend,
colors, symbols, error bars, lines, shaded areas, panel labels, captions; graphical
form must match what the axis claims (e.g., a KM curve decreasing from 1.0 should not
be labeled "recurrence rate"; cumulative recurrence should start near 0 and increase);
colors/labels agree with legend; leftover plotting artifacts or software-generated
text; figure agrees with text and tables.

**Terminology and direction** — "predictive" vs. "prognostic," "risk factor" vs.
"protective factor," "recurrence" vs. "recurrence-free survival," "mortality" vs.
"overall survival," etc. must match the actual analysis and stated reference group;
flag when the outcome actually analyzed differs from what the title/abstract/
conclusion/table title/figure label implies. In colorectal/oncology manuscripts, also
watch for: R0/R1 denominator, CRM positivity threshold, pCR vs. cCR, TNT regimen
naming, DFS vs. RFS vs. local-recurrence definitions.

**Methods–Results consistency** — design, inclusion/exclusion, outcome definitions,
statistical methods, variable selection, subgroup/ROC/sensitivity analyses, and
denominators in Methods match Results; contradictions between eligibility criteria and
the analyzed cohort; analyses in Results were actually described in Methods.

**Front matter, back matter, and references** — IRB approval number and consent/waiver
statement; trial/registry number consistency; COI, funding, data availability, author
contributions, ORCID, AI-use disclosure; author list/order/affiliations/corresponding
author consistent across title page and metadata; abbreviations defined at first use
(abstract and main text separately) and in table/figure footnotes; reference in-text
citation order and duplicates; citation count vs. reference list; obviously malformed
entries (impossible year, volume/page format). Do not verify reference existence via
web search unless asked.

**General proof errors** — typos; inconsistent abbreviations/units/decimal places;
incorrect percentages; spacing; inconsistent terminology; placeholders ("****", "XX",
"[ref]"); inconsistent wording across sections; wrong figure/table cross-references;
author/affiliation formatting errors; unexplained table/figure values; unresolved
typesetter author queries (AQ).

**House style (default: ACP)** — see `references/acp_house_style.md` for the full
rule set. Apply it unless the editor specified a different journal or asked to skip
house-style checking (see "Before starting"). Covers: statistical-value/P-value/
percentage decimal-place and notation rules (use `scripts/verify_table.py`'s
`p_value_format`/`percentage_format` checks — see Working Rule 1); italics for
organism/gene/enzyme names and Latin words; abbreviation and drug-naming
conventions; title-page and required-statement presence (ORCID, CRediT, COI
sentence, funding, ethics statement wording, AI-use disclosure); reference format
and count limits by article type; table/figure formatting (title placement,
footnote letters, no rules between cells, panel lettering, permission-statement
wording); article-type word/table/reference limits. Most deviations here are
**style only (B)** — see "Priority and certainty" below for the two exceptions
(literal P=0/P=1, and missing required statements) that are not.

## What NOT to do

Do not: criticize novelty/importance; request additional experiments or analyses just
because they might strengthen the paper; redesign the study; challenge a reasonable
method choice just because another exists; dwell on stylistic preferences; rewrite
large passages unless wording is genuinely misleading or incorrect; enforce a house
style the editor didn't ask for (i.e., don't apply ACP's rules if a different journal
or "no house style" was specified); pad the OPTIONAL list with trivial copyediting.

## Priority and certainty

- **A1 — MUST FIX, clear/likely error.**
- **A2 — MUST FIX, verification required** (potentially important but not confirmable
  from the manuscript; use "please verify/clarify/recheck" wording, never an
  accusation).
- **B — OPTIONAL/MINOR** (not essential; clearer wording, minor terminology
  standardization, small formatting fixes, readability improvements that don't change
  interpretation).

House-style findings (Section 2's "House style" subsection) default to **B**, with
two exceptions: a literal `P=0` or `P=1` is **A2** (it's a statistical-validity
problem, not just notation — see `acp_house_style.md` §1), and a clearly missing
required statement (IRB/ethics, COI, funding, AI-use disclosure, ORCID) at final
proof stage is **A1** (or **A2** if it's ambiguous whether it was just moved to
supplementary material).

Report all genuine A1/A2 issues. Report at most ~3–7 useful B issues — never manufacture
issues to hit a count. If the manuscript is clean, say so explicitly and still give the
coverage statement below.

## PDF comment location and style

Give the most precise location possible, e.g. `PDF p. 4, Table 2, "Tumor stage" row`,
`PDF p. 6, Results, sentence beginning "Multivariate analysis identified…"`,
`PDF p. 7, Fig. 3, y-axis`, `Supplementary Table 2, footnote`. If a page-numbering
mismatch exists between the PDF index and the printed page, note both:
`PDF p. 4 (printed p. 512)`. If the same inconsistency recurs in several places, put
the main comment at the source location (table/figure/primary Results sentence) and
note that matching values elsewhere should also be revised — don't duplicate identical
comments.

Comments themselves: concise, polite but firm when the error is clear, specific about
what to check/change, ready to paste as a PDF annotation, no greetings or preamble.

English example: "Please verify the reported P-value, as it appears inconsistent with
the corresponding HR and 95% CI."

Korean example: "해당 수치는 본문의 값과 일치하지 않습니다. 정확한 값을 다시 확인하고
관련된 표와 본문을 함께 수정해 주세요."

## Output format

**1. Summary table** at the top:

| # | Location | Priority (A1/A2/B) | Certainty | One-line summary |
|---|----------|--------------------|-----------|-------------------|

**2. Detailed findings**, ordered A1 → A2 → B, each as:

> **[N]. Short description**
> **Priority:** A1 / A2 / B
> **Certainty:** Clear error / Likely error / Verification required
> **Comment location:** exact PDF page and location
>
> **As written in the manuscript:**
> > verbatim quote
>
> **Why it matters (Korean):** brief explanation; show extracted inputs and computed
> results for any arithmetic.
>
> **PDF comment:** the concise comment to insert, in the language set in Section
> "Before starting."
>
> **Suggested correction** (only if the correct wording is obvious):
> > corrected sentence or value

Worked example of one finding (values illustrative):

> **[1]. Table 3 P-value contradicts its 95% CI**
> **Priority:** A2
> **Certainty:** Verification required
> **Comment location:** PDF p. 5 (printed p. 213), Table 3, row "Age ≥65", P column
>
> **As written in the manuscript:**
> > HR 1.45 (95% CI, 0.98–2.15); P=0.030
>
> **Why it matters (Korean):** 95% CI [0.98, 2.15]는 null값 1.0을 포함하므로
> 유의하지 않음을 시사하지만 P=0.030은 유의함을 시사합니다 (verify_table.py
> `ci_consistency` FLAG). 두 값 중 하나가 오기일 가능성이 높습니다.
>
> **PDF comment:** Please verify the reported P-value for "Age ≥65," as it appears
> inconsistent with the corresponding HR and 95% CI.

**3. Coverage statement** at the end: list every table, figure, graphical abstract,
and supplementary file inspected; state which figures were checked visually; state
anything unreadable or not provided.

## Final cross-check before answering

Before finalizing, re-verify: Abstract ↔ Methods ↔ Results ↔ Tables ↔ Figures ↔
Discussion ↔ Supplementary materials, with particular attention to sample sizes,
percentages, denominators, cutoff values, P-values, HRs/ORs/CIs, reference groups,
figure labels, units, study-period dates, inclusion/exclusion counts, and
outcome/variable definitions. Inspect visual elements directly whenever relevant —
never rely only on extracted text for tables/figures. If applying ACP house style,
confirm you've run `p_value_format`/`percentage_format` checks on every P-value and
percentage encountered, not just the ones already flagged by other checks.
