# Annals of Coloproctology (ACP) — House Style Reference

Extracted from ACP's Instructions to Authors. This is the **default house style**
applied by the manuscript-proofreading skill unless the editor specifies a different
journal. All of these are ACP-specific presentation/administrative rules — they are
distinct from the general scientific-consistency checks in SKILL.md, and unless noted
otherwise they are **style deviations (Priority B / OPTIONAL)**, not scientific
errors. Two exceptions are called out explicitly below because they can double as
scientific-validity or required-element problems (Priority A1/A2).

Only flag a deviation from this file if the manuscript's own text/tables contradict
it — do not invent values to "fix" formatting, and do not flag anything not covered
here as if it were an ACP rule.

---

## 1. Numeric and statistical formatting (mechanically checkable)

These three rules are implemented as script checks in `scripts/verify_table.py`
(`p_value_format`, `percentage_format`) — see `references/verify_table_schema.md`.
Run them for every P-value and percentage in the manuscript, the same pass as the
arithmetic checks.

- **Statistical values (HR, OR, means, SDs, etc.):** report to **3 decimal places**,
  with consistent decimal places maintained via trailing zeros (e.g., `1.450`, not
  `1.45`).
- **P-values:**
  - Must never be printed as exactly `0` or exactly `1`.
    - `P=0` → should be `P<0.001`.
    - `P=1` → should be `P>0.999`.
    - **This is not pure style** — a P-value is asymptotically never exactly 0 or 1,
      so a literal `P=0`/`P=1` is also a statistical-validity problem. Classify as
      **A2 (verification required)**, not B.
  - Otherwise reported to 3 decimal places with consistent trailing zeros (style
    only → **B**).
- **Percentages:**
  - 1 decimal place by default.
  - 2 decimal places allowed only when the denominator is ≥ 10,000.
  - **No trailing zero on a whole-number percentage**: `50/100 = 50%`, not `50.0%`.
  - Style only → **B**, unless the underlying number itself is wrong (in which case
    it's the `percentage` arithmetic check in the main skill, not this one).

## 2. Units and nomenclature

- Measurements in **SI units** (conventional units used per ICMJE/SI convention).
- **Italics required** for:
  - Biological organism names (e.g., *Saccharomyces cerevisiae*, *E. coli*)
  - Restriction enzymes and select other enzymes (e.g., *EcoRI*, *Taq* polymerase)
  - Gene names (e.g., *src*, *c-H-ras*, *myc*)
  - Words of Latin origin (e.g., *in vivo*, *in vitro*, *in situ*)
  - Centrifugation force (e.g., *100,000 g*)
- **Abbreviations:** spelled out at first use with the abbreviation in parentheses,
  used consistently thereafter; standard abbreviations only; **not used in the
  title**.
- **Drug names:** nonproprietary (generic) name first in text; proprietary name
  capitalized in parentheses if used; manufacturer need not follow the proprietary
  name in text (but should appear elsewhere per Methods conventions for
  reagents/equipment).
- **Title:** sentence case; generic (not brand) drug names; should indicate study
  design; should state the country if the study involved human participants.

## 3. Title page and required statements

Check presence and internal consistency, not correctness of content the editor must
judge:

- **ORCID** for all authors.
- **Author contributions** using CRediT taxonomy roles.
- **Conflict of interest** statement — if none, the manuscript should contain
  exactly: *"No potential conflict of interest relevant to this article was
  reported."*
- **Funding** statement — all funding sources explicitly stated (FundRef ID/grant
  number when available).
- **Ethics statement** (Methods, for studies with clinical samples/data or animals)
  — expected form:
  > "We conducted this study in compliance with the principles of the Declaration of
  > Helsinki. The study's protocol was reviewed and approved by the Institutional
  > Review Board of OO (No. OO). Written informed consents were obtained from the
  > patients." / "The requirement for informed consent was waived."
- **Any inapplicable section** should still appear with the heading and the text
  "Not applicable." — a missing heading (rather than "Not applicable") may indicate
  an accidentally deleted section.
- **AI-assisted technology disclosure** — if generative AI was used in preparing the
  manuscript, this should be disclosed (tool, version, role) in Methods or
  Acknowledgments; AI must not be listed as an author or cited as a primary source.
- Missing IRB/registration/COI/funding/AI-disclosure at final proof stage is a
  **required element**, not a style nicety → classify as **A1 (clear error)** if
  clearly absent, or **A2** if ambiguous (e.g., unclear whether it was moved to
  supplementary material).

## 4. References

- Numbered in order of first appearance in text (Arabic numerals in brackets).
- List all authors if ≤6; if >6, list first 6 then "et al."
- Journal titles abbreviated per NLM Catalog style.
- Online-ahead-of-print articles: supply DOI.
- **Reference count limits by article type** — see the table in Section 7. Exceeding
  the limit should have been caught before acceptance; if still present at proof
  stage, flag as **B** and suggest the editorial office confirm whether an exception
  was granted, rather than asserting it's an error.
- Do not verify whether cited references actually exist via web search unless the
  editor explicitly asks (per the main skill's working rules) — only check internal
  consistency (citation order, duplicate numbers, citation count vs. reference list
  length, obviously malformed entries such as an impossible year or volume/page
  format).

## 5. Tables

- Numbered in order of citation in text.
- Table title placed immediately **above** the table, concise enough to stand alone.
- Explanatory notes go in **footnotes below** the table, not in the title.
- Footnotes indicated by superscript **lowercase letters** (a, b, c…), not numbers or
  symbols.
- All nonstandard abbreviations used in a table must be explained in that table's own
  footnote (even if already defined in text).
- No vertical or horizontal rules between entries (open/three-line table style).
- Dispersion measures (SD, SE, etc.) identified explicitly.

## 6. Figures and figure legends

- Legends on a separate page in the main text; figures numbered with Arabic
  numerals in citation order.
- Multi-panel figures: panels lettered (e.g., Fig. 1A, Fig. 2B, C).
- Microscopy images: staining method and magnification stated (e.g.,
  "hematoxylin-eosin, original magnification ×100").
- Bar/line graphs of averages or proportions: should include a dispersion measure
  (SD or SE) and P-values where relevant.
- Reused table/figure permission statement format:
  > "Reprinted/Modified/Adapted from Tanaka et al. [48], with permission of
  > Elsevier." / "Reprinted/Modified/Adapted from Weiss et al. [2], available under
  > the Creative Commons License."

## 7. Article-type structure and limits

| Article type | Abstract | Text structure | Max text length | Max Tables+Figures | Max references |
|---|---|---|---|---|---|
| Original article | Structured (Purpose/Methods/Results/Conclusion, ≤250 words) | Introduction, Methods, Results, Discussion | No stated word limit | 7 | 50* |
| Review article (invited) | Unstructured, ≤200 words | Introduction, Body, Conclusion | ≤7,500 words | — | 100 |
| Study protocol | Structured (Background/Study design/Outcome/Trial Registration, ≤250 words) | Introduction, Methods, Discussion | ≤5,000 words | 7 | 50 |
| Technical note | Not required | Introduction, Technique, Discussion | ≤1,500 words | — | 15 |
| Brief communication | Not required | (no fixed sections) | ≤1,500 words | — | 15 |
| Guideline | Unstructured, ≤250 words | Introduction, Body, Conclusion | ≤7,500 words | — | No limit |
| Editorial (invited) | Not required | (no fixed sections) | ≤2,000 words | — | 10 |
| Letter to the editor | Not required | (no fixed sections) | ≤1,000 words | — | 10 |
| Video | Not required | (no fixed sections) | ≤1,500 words | — | 15 |

Word-count limits exclude abstract, references, tables, and figure legends.
Exceptions to any limit require editor approval.

\* **Note on a source discrepancy:** the ACP Instructions to Authors document
contains two different tables for "Original article" reference limits — the main
"Article types" section states 50 (and the running text explicitly says "The number
of references for original articles is limited to 50"), while a later
"SUMMARY OF MANUSCRIPT PREPARATION" table lists "No limit" for the same row. Treat
**50** as authoritative (it matches the explicit prose statement), but if this
matters for a specific manuscript, verify against the current live Instructions to
Authors page rather than relying on this file alone.

Use this table only to flag a manuscript that is **clearly and substantially** over
its stated limit (e.g., 90 references on an original article) — do not nitpick
being one or two references over, and never count words/tables/figures yourself with
high precision from a PDF; note it as "please verify against the word/reference
limit" (A2) if genuinely unclear, or B if minor.

## 8. Ethics, consent, and participant description specifics

- IRB approval (human studies) or IACUC approval (animal studies) required; approval
  number should be traceable in the ethics statement.
- Informed consent obtained or explicitly waived by IRB/ethics committee; for
  vulnerable populations, consent from a legally authorized representative or
  guardian.
- Clinical trials must be registered (CRIS, WHO-accredited registry, or
  ClinicalTrials.gov) and the registration number should appear consistently in the
  abstract/Methods where required by the article type (e.g., Study protocol
  abstracts require a Trial Registration field).
- "Sex" (biological) vs. "gender" (identity/psychosocial) terminology should be used
  correctly and distinctly, per the manuscript's own described population.
- No directly identifying patient information (names, initials, hospital numbers,
  DOB) should appear in text, tables, or figures.

## 9. What this file does NOT cover

This file only captures **ACP's own explicit administrative/formatting rules**. It
does not substitute for the scientific-consistency checks in the main
`manuscript-proofreading` skill (numerical/statistical/Methods–Results consistency,
etc.) — apply both. If the editor specifies a non-ACP journal or a different
house style, do not apply this file; ask for or use the journal-specific rules
instead, per the main skill's "Before starting" section.
