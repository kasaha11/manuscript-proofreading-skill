# verify_table.py — Input Schema Reference

`scripts/verify_table.py` takes a JSON file with a top-level `"checks"` array.
Each item is one deterministic check. Build this file from values you have
**already quoted verbatim** from the manuscript (per the skill's verbatim
rule) — never invent a number to fill a field.

Run it with:

```bash
python3 <skill-dir>/scripts/verify_table.py checks.json
python3 <skill-dir>/scripts/verify_table.py checks.json --only-flags
python3 <skill-dir>/scripts/verify_table.py checks.json --json-out results.json
```

**Input tolerance.** Every numeric field accepts either a number or the exact
printed string (`"40.0%"`, `"1,234"`, `"P<0.001"`, `"300"`). A malformed entry
yields `FLAG [Input error]` for that item only — the rest of the file still runs.
`FLAG [Input error]` is never a manuscript finding.

A complete fixture covering every check type lives in `tests/sample_checks.json`;
copy entries from it rather than writing from scratch.

Exit code is `1` if any check is flagged, `0` if all match — useful if
chaining calls.

Every check needs `"type"` and `"location"` (free text — copy the location
string you'll use in the PDF comment, e.g. `"Table 2, row 'Age <65'"`).

---

## 1. `percentage`

Recomputes `numerator / denominator * 100` and compares to the value printed
in the manuscript.

```json
{"type": "percentage", "location": "Table 2, row 'Age <65'",
 "numerator": 120, "denominator": 300, "reported_pct": 45.0}
```

Optional: `"tolerance"` (percentage points). If omitted **and** `reported_pct`
is given as a string, tolerance is derived from the printed precision (`"33"` →
±0.5, `"33.3"` → ±0.05), so integer-rounded percentages are not false-flagged.
Prefer passing the printed string. If a bare number is given, default is `0.1`.

---

## 2. `subgroup_sum`

Checks whether mutually-exclusive subgroup counts sum to the reported total
(e.g., stage I+II+III+IV vs. the table's overall N, or Male+Female vs. total).

```json
{"type": "subgroup_sum", "location": "Table 1, 'Stage' column",
 "parts": {"I": 50, "II": 80, "III": 90, "IV": 95}, "reported_total": 314}
```

`"parts"` can be a dict (labels shown in the detail message) or a plain list
of numbers.

---

## 3. `ci_shape`

Checks that a 95% CI is internally well-formed: lower < upper, and the point
estimate falls inside the interval. Catches swapped bounds and copy-paste
mismatches between the estimate and its own CI.

```json
{"type": "ci_shape", "location": "Table 3, row 'Age >=65'",
 "estimate": 1.45, "ci_lower": 0.98, "ci_upper": 2.15}
```

---

## 4. `ci_consistency`

Checks whether the CI's relationship to the null value (1 for HR/OR/RR, 0 for
a mean/risk difference) agrees with the significance implied by the reported
P-value. This is the single highest-yield check for "obvious copy-and-paste
P-value" errors.

```json
{"type": "ci_consistency", "location": "Table 3, row 'Age >=65'",
 "ci_lower": 0.98, "ci_upper": 2.15, "reported_p": 0.03, "measure": "ratio"}
```

- `"measure"`: `"ratio"` (HR/OR/RR, null = 1; default) or `"difference"`
  (mean/risk difference, null = 0).
- `"reported_p"` accepts a number, or a string like `"<0.001"` / `">0.05"`.
- `"alpha"`: significance threshold, default `0.05`.
- P-values landing within 0.005 of alpha are treated as borderline and not
  flagged — the manuscript may report an unrounded value you don't have.
- Bounds that cannot decide significance at alpha (e.g. `"<0.1"`, `">0.01"`)
  return MATCH with `"indeterminate": true` — they are not evidence either way.
- A leading `P=` / `p<` copied verbatim is tolerated.

This check does **not** verify that the P-value is the mathematically exact
one for that CI (that requires the underlying model and isn't recoverable
from summary statistics) — it only catches the common case where the CI and
P flatly contradict each other's significance verdict. Report a FLAG here as
"Verification required" or "Likely error" per the skill's certainty rules,
never as proof of a specific correct value.

---

## 5. `p_range`

Confirms a P-value string/number lies in the valid `[0, 1]` range.

```json
{"type": "p_range", "location": "Table 3, row 'Sex'", "reported_p": "1.20"}
```

---

## 6. `rounding_consistency`

Generic cross-location check for "the same underlying number reported twice"
— e.g., a percentage stated in the Abstract vs. the same value in Table 1, or
a mean reported in Results text vs. a figure legend.

```json
{"type": "rounding_consistency", "location": "Abstract vs Table 1",
 "value_a": 45.2, "location_a": "Abstract",
 "value_b": 44.8, "location_b": "Table 1",
 "tolerance": 0.5}
```

If `"tolerance"` is omitted and the values are given as printed strings, it is
derived from the coarser printed precision (`"45"` vs `"45.2"` → ±0.5). Pass the
strings as printed rather than hand-picking a tolerance.

---

## 7. `p_value_format` (ACP house style)

Checks P-value **notation**, not the value's plausibility (use `p_range` /
`ci_consistency` for that). Flags:
- any value numerically equal to `0` or `1` (`0`, `0.000`, `0.0000`, `1.00`…; P
  can never be exactly 0 or 1 — treat as
  "Verification required", not pure style, since it may hide the real value)
- inconsistent decimal places (ACP: 3 decimals with trailing zeros, unless
  `<`/`>` notation is used)

```json
{"type": "p_value_format", "location": "Table 3, row 'Sex'", "reported_p": "0.03"}
```

Pass `"reported_p"` as the **exact string** printed in the manuscript (not a
parsed float) so trailing zeros and inequality signs are preserved. Optional
`"required_decimals"` (default `3`).

---

## 8. `percentage_format` (ACP house style)

Checks percentage **notation**: 1 decimal place by default, 2 if the
denominator is ≥10,000, and no trailing `.0` on a whole-number percentage.

```json
{"type": "percentage_format", "location": "Table 1, row 'Male'",
 "reported_pct": "50.0", "denominator": 300}
```

Pass `"reported_pct"` as the exact string printed (with or without a `%`
sign — both are accepted).

This is independent of the `percentage` check (which verifies the *value* is
arithmetically correct) — a percentage can be correctly calculated but
incorrectly formatted, or vice versa. Run both when relevant.

---

## Workflow inside the proofreading skill

1. While reading a table/section, pull out every number that participates in
   an arithmetic relationship (numerator/denominator/percent, subgroup counts
   and their total, estimate/CI/P triples) **and** every P-value/percentage's
   exact printed notation (for the ACP `p_value_format`/`percentage_format`
   checks).
2. Write them into a `checks.json` using the schema above — one check per
   relationship, `"location"` matching what you'll cite in the PDF comment.
3. Run `verify_table.py` on the whole file once per table/section rather than
   one check at a time.
4. For every `FLAG`, turn it into a finding using the script's own `detail`
   text as the basis for "Why it matters" (translate/phrase in Korean as the
   skill's output format requires), and use `computed` as the shown
   calculation.
5. For every `MATCH`, no finding is needed — the arithmetic held up.

This turns Working Rule 1 ("calculate, don't estimate") from a general
instruction into an actual deterministic pass over every extracted number.
