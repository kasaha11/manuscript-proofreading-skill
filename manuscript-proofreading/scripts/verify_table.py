#!/usr/bin/env python3
"""
verify_table.py — Deterministic arithmetic/statistical consistency checks for
manuscript proofreading.

Purpose
-------
Replaces mental arithmetic with code-verified checks for the most common
proof-stage numerical errors in medical manuscripts:

  - percentage       : does numerator/denominator*100 match the reported %?
  - subgroup_sum      : do subgroup counts sum to the reported total?
  - ci_consistency    : is the HR/OR/RR (or difference) 95% CI consistent
                        with the reported P-value (does the CI's relationship
                        to the null value agree with significance implied by P)?
  - ci_shape          : is ci_lower < estimate < ci_upper, and ci_lower < ci_upper?
  - p_range           : is the P-value within (0, 1)?
  - rounding_consistency : do two reported roundings of the "same" number
                        agree within tolerance (e.g., text says 45.2%, table
                        says 45%)?
  - p_value_format    : ACP house style — P must not print as exactly 0 or 1,
                        and should use 3 decimal places (trailing zeros kept)
                        unless "<"/">" notation is used.
  - percentage_format : ACP house style — 1 decimal place by default (2 if
                        denominator >= 10,000), and no trailing ".0" on whole
                        numbers (50%, not 50.0%).

This script does NOT decide whether something is scientifically wrong — it only
flags arithmetic/logical inconsistencies for a human editor (or Claude) to
interpret and phrase as a proof comment. Every result includes the raw inputs
and the computed value, so it can be quoted directly in a "Why it matters"
explanation.

Usage
-----
    python3 verify_table.py checks.json
    python3 verify_table.py checks.json --json-out results.json
    python3 verify_table.py checks.json --only-flags

Input format (checks.json)
---------------------------
A JSON object with a "checks" list. Each check has a "type", a free-text
"location" (for citing in the PDF comment), and type-specific fields.
See references/verify_table_schema.md for full documentation and examples,
or run:  python3 verify_table.py --show-schema
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Optional, Union


# --------------------------------------------------------------------------
# Result object
# --------------------------------------------------------------------------

@dataclass
class CheckResult:
    index: int
    type: str
    location: str
    status: str  # "MATCH" or "FLAG"
    certainty: Optional[str]  # "Clear error" / "Likely error" / "Verification required" / "Input error" / None
    detail: str
    computed: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "index": self.index,
            "type": self.type,
            "location": self.location,
            "status": self.status,
            "certainty": self.certainty,
            "detail": self.detail,
            "computed": self.computed,
        }


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def parse_p_value(p: Union[str, float, int]) -> tuple:
    """
    Returns (value, is_bound, bound_type) where:
      - value: float, the numeric P-value (or the threshold if a bound like "<0.001")
      - is_bound: True if the input was a "<" or ">" style string
      - bound_type: "<" , ">" , or None
    """
    if isinstance(p, (float, int)) and not isinstance(p, bool):
        return float(p), False, None
    s = str(p).strip()
    # Tolerate a leading "P", "p", "P =", "P-value=" etc. copied verbatim.
    s = re.sub(r"^[Pp](?:-?value)?\s*=?\s*", "", s).strip()
    for op in ("<", ">", "≤", "≥"):
        if s.startswith(op):
            num = to_float(s[1:], "reported_p")
            norm_op = "<" if op in ("<", "≤") else ">"
            return num, True, norm_op
    return to_float(s, "reported_p"), False, None


def to_float(x, field_name: str = "value") -> float:
    """
    Normalize a numeric field that may arrive as a number or as the exact
    string printed in the manuscript ("40.0%", "1,234", " 300 "). Raises
    ValueError with a readable message if it cannot be interpreted.
    """
    if isinstance(x, bool):
        raise ValueError(f"{field_name}: boolean is not a number")
    if isinstance(x, (int, float)):
        return float(x)
    t = str(x).strip().rstrip("%").replace(",", "").strip()
    try:
        return float(t)
    except ValueError:
        raise ValueError(f"{field_name}='{x}'를 숫자로 해석할 수 없습니다") from None


def _decimals_of(x) -> Optional[int]:
    """Decimal places of the value as originally given (None if not a string)."""
    if isinstance(x, str):
        t = x.strip().rstrip("%").strip()
        return len(t.split(".")[1]) if "." in t else 0
    return None


def fmt(x):
    if isinstance(x, float):
        return f"{x:.4g}"
    return str(x)


# --------------------------------------------------------------------------
# Individual check functions
# --------------------------------------------------------------------------

def check_percentage(c: dict, idx: int) -> CheckResult:
    """
    Required: numerator, denominator, reported_pct
    Optional: tolerance (percentage points; default 0.1)
    """
    loc = c.get("location", "(location not given)")
    num = to_float(c["numerator"], "numerator")
    den = to_float(c["denominator"], "denominator")
    reported_raw = c["reported_pct"]
    reported = to_float(reported_raw, "reported_pct")
    # Tolerance: explicit > derived from the printed precision > default 0.1.
    # A value printed as "33" (0 decimals) may legitimately be 33.33; allow
    # half a unit of the last printed digit plus a small float margin.
    if "tolerance" in c:
        tol = float(c["tolerance"])
    else:
        dec = _decimals_of(reported_raw)
        tol = (0.5 * 10 ** (-dec) + 0.001) if dec is not None else 0.1

    if den == 0:
        return CheckResult(idx, "percentage", loc, "FLAG", "Clear error",
                            "분모가 0입니다 — 퍼센트를 계산할 수 없습니다.",
                            {"numerator": num, "denominator": den})

    computed = num / den * 100
    diff = abs(computed - reported)

    if diff <= tol:
        return CheckResult(idx, "percentage", loc, "MATCH", None,
                            f"{num}/{den} = {computed:.2f}% ≈ reported {reported}% (일치)",
                            {"numerator": num, "denominator": den,
                             "computed_pct": round(computed, 2), "reported_pct": reported,
                             "diff": round(diff, 2)})

    certainty = "Likely error" if diff <= 1.0 else "Clear error"
    return CheckResult(idx, "percentage", loc, "FLAG", certainty,
                        f"{num}/{den} = {computed:.2f}%이지만 본문/표에는 {reported}%로 기재됨 "
                        f"(차이 {diff:.2f}%p).",
                        {"numerator": num, "denominator": den,
                         "computed_pct": round(computed, 2), "reported_pct": reported,
                         "diff": round(diff, 2)})


def check_subgroup_sum(c: dict, idx: int) -> CheckResult:
    """
    Required: parts (dict label->count, or list of counts), reported_total
    """
    loc = c.get("location", "(location not given)")
    parts = c["parts"]
    reported_total = to_float(c["reported_total"], "reported_total")

    if isinstance(parts, dict):
        values = [to_float(v, f"parts[{k}]") for k, v in parts.items()]
        parts_str = ", ".join(f"{k}={v}" for k, v in parts.items())
    else:
        values = [to_float(v, "parts") for v in parts]
        parts_str = ", ".join(str(v) for v in parts)

    computed_total = sum(values)
    diff = computed_total - reported_total
    if computed_total == int(computed_total):
        computed_total = int(computed_total)
    if reported_total == int(reported_total):
        reported_total = int(reported_total)

    if abs(diff) < 1e-9:
        return CheckResult(idx, "subgroup_sum", loc, "MATCH", None,
                            f"{parts_str} 합 = {computed_total} = reported total {reported_total} (일치)",
                            {"parts": parts, "computed_total": computed_total,
                             "reported_total": reported_total})

    certainty = "Clear error"
    return CheckResult(idx, "subgroup_sum", loc, "FLAG", certainty,
                        f"{parts_str}의 합은 {computed_total}이지만, 보고된 총합은 "
                        f"{reported_total}입니다 (차이 {diff:+g}).",
                        {"parts": parts, "computed_total": computed_total,
                         "reported_total": reported_total, "diff": diff})


def check_ci_shape(c: dict, idx: int) -> CheckResult:
    """
    Required: estimate, ci_lower, ci_upper
    """
    loc = c.get("location", "(location not given)")
    est = to_float(c["estimate"], "estimate")
    lo = to_float(c["ci_lower"], "ci_lower")
    hi = to_float(c["ci_upper"], "ci_upper")

    problems = []
    if lo > hi:
        problems.append(f"CI 하한({lo})이 상한({hi})보다 큽니다.")
    if not (lo <= est <= hi):
        problems.append(f"점추정치({est})가 95% CI [{lo}, {hi}] 범위 밖에 있습니다.")

    if not problems:
        return CheckResult(idx, "ci_shape", loc, "MATCH", None,
                            f"estimate {est}, 95% CI [{lo}, {hi}] — 구조적으로 정상.",
                            {"estimate": est, "ci_lower": lo, "ci_upper": hi})

    return CheckResult(idx, "ci_shape", loc, "FLAG", "Clear error",
                        " ".join(problems),
                        {"estimate": est, "ci_lower": lo, "ci_upper": hi})


def check_ci_consistency(c: dict, idx: int) -> CheckResult:
    """
    Checks whether the CI's relationship to the null value agrees with the
    significance implied by the reported P-value.

    Required: ci_lower, ci_upper, reported_p
    Optional: measure ("ratio" default -> null=1, or "difference" -> null=0),
              alpha (default 0.05)
    """
    loc = c.get("location", "(location not given)")
    lo = to_float(c["ci_lower"], "ci_lower")
    hi = to_float(c["ci_upper"], "ci_upper")
    reported_p = c["reported_p"]
    measure = c.get("measure", "ratio")
    alpha = float(c.get("alpha", 0.05))
    null_value = 0.0 if measure == "difference" else 1.0

    ci_excludes_null = (lo > null_value) or (hi < null_value)

    p_val, is_bound, bound_op = parse_p_value(reported_p)
    if is_bound and bound_op == "<":
        if p_val > alpha:
            # e.g. "<0.1" — says nothing about significance at alpha; cannot judge.
            return CheckResult(idx, "ci_consistency", loc, "MATCH", None,
                                f"P{reported_p}는 alpha={alpha} 기준 유의성을 판정할 수 없는 "
                                f"부등호 표기이므로 CI와의 비교를 보류합니다 (판단 불가).",
                                {"ci_lower": lo, "ci_upper": hi, "reported_p": reported_p,
                                 "indeterminate": True})
        p_significant = True
        p_borderline = False
    elif is_bound and bound_op == ">":
        if p_val < alpha:
            # e.g. ">0.01" — could still be < 0.05; cannot judge.
            return CheckResult(idx, "ci_consistency", loc, "MATCH", None,
                                f"P{reported_p}는 alpha={alpha} 기준 유의성을 판정할 수 없는 "
                                f"부등호 표기이므로 CI와의 비교를 보류합니다 (판단 불가).",
                                {"ci_lower": lo, "ci_upper": hi, "reported_p": reported_p,
                                 "indeterminate": True})
        p_significant = False
        p_borderline = False
    else:
        p_significant = p_val < alpha
        p_borderline = abs(p_val - alpha) <= 0.005  # near the alpha boundary -> don't hard-flag

    computed = {
        "ci_lower": lo, "ci_upper": hi, "null_value": null_value,
        "ci_excludes_null": ci_excludes_null,
        "reported_p": reported_p, "p_significant_at_alpha": p_significant,
        "alpha": alpha,
    }

    if ci_excludes_null == p_significant or p_borderline:
        return CheckResult(idx, "ci_consistency", loc, "MATCH", None,
                            f"95% CI [{lo}, {hi}] (null={null_value} "
                            f"{'제외' if ci_excludes_null else '포함'})와 "
                            f"P={reported_p}의 유의성 판정이 서로 일치함.",
                            computed)

    return CheckResult(idx, "ci_consistency", loc, "FLAG", "Likely error",
                        f"95% CI [{lo}, {hi}]는 null값({null_value})을 "
                        f"{'제외' if ci_excludes_null else '포함'}하여 "
                        f"{'유의함' if ci_excludes_null else '유의하지 않음'}을 시사하지만, "
                        f"보고된 P={reported_p}는 "
                        f"{'유의함' if p_significant else '유의하지 않음'}을 시사합니다. "
                        f"서로 모순되므로 원저자에게 확인이 필요합니다.",
                        computed)


def check_p_range(c: dict, idx: int) -> CheckResult:
    """
    Required: reported_p
    """
    loc = c.get("location", "(location not given)")
    reported_p = c["reported_p"]
    p_val, is_bound, bound_op = parse_p_value(reported_p)

    if 0 <= p_val <= 1:
        return CheckResult(idx, "p_range", loc, "MATCH", None,
                            f"P={reported_p} — 유효 범위(0~1) 내.",
                            {"reported_p": reported_p, "parsed_value": p_val})

    return CheckResult(idx, "p_range", loc, "FLAG", "Clear error",
                        f"P={reported_p}는 유효 범위(0~1)를 벗어납니다.",
                        {"reported_p": reported_p, "parsed_value": p_val})


def check_rounding_consistency(c: dict, idx: int) -> CheckResult:
    """
    Compares two reportings of the same underlying number (e.g., abstract vs.
    table) for consistency, allowing for stated rounding precision.

    Required: value_a, value_b, location_a, location_b
    Optional: tolerance (default 0.05 absolute, or based on decimals of the
              coarser value)
    """
    loc = c.get("location", "(location not given)")
    a_raw, b_raw = c["value_a"], c["value_b"]
    a = to_float(a_raw, "value_a")
    b = to_float(b_raw, "value_b")
    loc_a = c.get("location_a", "value A")
    loc_b = c.get("location_b", "value B")
    if "tolerance" in c:
        tol = float(c["tolerance"])
    else:
        # Half a unit of the coarser printed precision (strings only), else 0.05.
        decs = [d for d in (_decimals_of(a_raw), _decimals_of(b_raw)) if d is not None]
        tol = (0.5 * 10 ** (-min(decs)) + 0.001) if decs else 0.05

    diff = abs(a - b)
    if diff <= tol:
        return CheckResult(idx, "rounding_consistency", loc, "MATCH", None,
                            f"{loc_a}={a}, {loc_b}={b} — 허용 오차 내 일치.",
                            {"value_a": a, "value_b": b, "diff": round(diff, 4)})

    certainty = "Likely error" if diff <= 1.0 else "Clear error"
    return CheckResult(idx, "rounding_consistency", loc, "FLAG", certainty,
                        f"{loc_a}={a}이지만 {loc_b}={b}로 서로 다릅니다 (차이 {diff:.4g}).",
                        {"value_a": a, "value_b": b, "diff": round(diff, 4)})


def _decimal_count(s: str) -> int:
    return len(s.split(".")[1]) if "." in s else 0


def check_p_value_format(c: dict, idx: int) -> CheckResult:
    """
    ACP house style: P-values must never be printed as exactly 0 or exactly 1,
    and (when not using "<"/">" notation) should carry 3 decimal places with
    consistent trailing zeros.

    Required: reported_p (the EXACT string as printed in the manuscript, e.g.
               "0.03", "0", "1.000", "<0.001")
    Optional: required_decimals (default 3)
    """
    loc = c.get("location", "(location not given)")
    raw = c["reported_p"]
    s = str(raw).strip()
    required_decimals = c.get("required_decimals", 3)

    s = re.sub(r"^[Pp](?:-?value)?\s*=?\s*", "", s).strip()

    def _is_plain_number(t):
        try:
            float(t)
            return True
        except ValueError:
            return False

    if _is_plain_number(s) and float(s) == 0.0:
        return CheckResult(idx, "p_value_format", loc, "FLAG", "Verification required",
                            f"P={s}로 표기되어 있습니다. P값은 정의상 정확히 0이 될 수 없으므로 "
                            f"ACP 스타일 규정에 따라 P<0.001로 표기해야 합니다. 실제 산출된 정확한 "
                            f"P값을 저자에게 확인해야 합니다.",
                            {"reported_p": s, "expected": "P<0.001"})

    if _is_plain_number(s) and float(s) == 1.0:
        return CheckResult(idx, "p_value_format", loc, "FLAG", "Verification required",
                            f"P={s}로 표기되어 있습니다. P값은 정의상 정확히 1이 될 수 없으므로 "
                            f"ACP 스타일 규정에 따라 P>0.999로 표기해야 합니다.",
                            {"reported_p": s, "expected": "P>0.999"})

    if s.startswith(("<", ">", "≤", "≥")):
        return CheckResult(idx, "p_value_format", loc, "MATCH", None,
                            f"P{s} — 부등호 표기는 ACP 스타일상 허용됩니다.",
                            {"reported_p": s})

    try:
        float(s)
    except ValueError:
        return CheckResult(idx, "p_value_format", loc, "FLAG", None,
                            f"'{s}'를 숫자로 해석할 수 없습니다 — 표기를 확인하세요.",
                            {"reported_p": s})

    decimals = _decimal_count(s)
    if decimals != required_decimals:
        return CheckResult(idx, "p_value_format", loc, "FLAG", None,
                            f"P={s}는 소수점 {decimals}자리입니다. ACP 스타일은 통계값을 "
                            f"소수점 {required_decimals}자리로 일관되게(trailing zero 포함) "
                            f"표기하도록 규정합니다.",
                            {"reported_p": s, "decimals": decimals,
                             "required_decimals": required_decimals})

    return CheckResult(idx, "p_value_format", loc, "MATCH", None,
                        f"P={s} — 소수점 자릿수 규정에 부합.",
                        {"reported_p": s, "decimals": decimals})


def check_percentage_format(c: dict, idx: int) -> CheckResult:
    """
    ACP house style: percentages use 1 decimal place by default (2 if the
    denominator is >=10,000), and whole-number percentages must NOT carry a
    trailing ".0".

    Required: reported_pct (the EXACT string as printed, without the "%" sign,
               e.g. "45.2", "50.0", "50"), denominator
    """
    loc = c.get("location", "(location not given)")
    raw = c["reported_pct"]
    s = str(raw).strip().rstrip("%").strip()
    denominator = to_float(c["denominator"], "denominator")

    try:
        numeric = float(s)
    except ValueError:
        return CheckResult(idx, "percentage_format", loc, "FLAG", None,
                            f"'{s}'를 숫자로 해석할 수 없습니다 — 표기를 확인하세요.",
                            {"reported_pct": s})

    decimals = _decimal_count(s)
    is_whole = numeric == int(numeric)
    expected_decimals = 2 if denominator >= 10000 else 1

    if is_whole:
        if decimals != 0:
            return CheckResult(idx, "percentage_format", loc, "FLAG", None,
                                f"{s}%는 정수 퍼센트이므로 소수점 없이 '{int(numeric)}%'로 "
                                f"표기해야 합니다 (ACP 스타일: 50/100=50%, 50.0% 아님).",
                                {"reported_pct": s, "denominator": denominator})
        return CheckResult(idx, "percentage_format", loc, "MATCH", None,
                            f"{s}% — 정수 퍼센트 표기 규정에 부합.",
                            {"reported_pct": s, "denominator": denominator})

    if decimals != expected_decimals:
        return CheckResult(idx, "percentage_format", loc, "FLAG", None,
                            f"{s}%는 소수점 {decimals}자리입니다. 분모가 {denominator}이므로 "
                            f"ACP 스타일상 소수점 {expected_decimals}자리로 표기해야 합니다.",
                            {"reported_pct": s, "denominator": denominator,
                             "decimals": decimals, "expected_decimals": expected_decimals})

    return CheckResult(idx, "percentage_format", loc, "MATCH", None,
                        f"{s}% — 분모 {denominator}에 대한 소수점 자릿수 규정에 부합.",
                        {"reported_pct": s, "denominator": denominator, "decimals": decimals})


CHECK_DISPATCH = {
    "percentage": check_percentage,
    "subgroup_sum": check_subgroup_sum,
    "ci_shape": check_ci_shape,
    "ci_consistency": check_ci_consistency,
    "p_range": check_p_range,
    "rounding_consistency": check_rounding_consistency,
    "p_value_format": check_p_value_format,
    "percentage_format": check_percentage_format,
}


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def run_checks(checks: list) -> list:
    results = []
    for idx, c in enumerate(checks, start=1):
        ctype = c.get("type")
        fn = CHECK_DISPATCH.get(ctype)
        if fn is None:
            results.append(CheckResult(idx, str(ctype), c.get("location", "?"),
                                        "FLAG", None,
                                        f"알 수 없는 check type '{ctype}' — "
                                        f"지원 유형: {list(CHECK_DISPATCH)}", {}))
            continue
        try:
            results.append(fn(c, idx))
        except KeyError as e:
            results.append(CheckResult(idx, ctype, c.get("location", "?"),
                                        "FLAG", "Input error",
                                        f"필수 필드 누락: {e}", {"raw_check": c}))
        except Exception as e:  # never let one bad item kill the whole run
            results.append(CheckResult(idx, ctype, c.get("location", "?"),
                                        "FLAG", "Input error",
                                        f"입력 오류 ({type(e).__name__}): {e} — 이 항목의 "
                                        f"입력값을 확인하세요. (검산 결과가 아닙니다)",
                                        {"raw_check": c}))
    return results


def print_report(results: list, only_flags: bool = False):
    flags = [r for r in results if r.status == "FLAG"]
    matches = [r for r in results if r.status == "MATCH"]

    print(f"검산 결과: 총 {len(results)}건 — MATCH {len(matches)}건, FLAG {len(flags)}건\n")

    to_show = flags if only_flags else results
    for r in to_show:
        mark = "❌ FLAG" if r.status == "FLAG" else "✅ MATCH"
        cert = f" [{r.certainty}]" if r.certainty else ""
        print(f"[{r.index}] {mark}{cert} — {r.type} — {r.location}")
        print(f"    {r.detail}")
        if r.computed:
            print(f"    computed: {r.computed}")
        print()


SCHEMA_DOC = """
See references/verify_table_schema.md for the full schema and worked examples.

Quick reference — checks.json shape:

{
  "checks": [
    {"type": "percentage", "location": "Table 2, row 'Age <65'",
     "numerator": 120, "denominator": 300, "reported_pct": 45.0},

    {"type": "subgroup_sum", "location": "Table 2, 'Sex' column",
     "parts": {"Male": 180, "Female": 120}, "reported_total": 300},

    {"type": "ci_shape", "location": "Table 3, row 'Age >=65'",
     "estimate": 1.45, "ci_lower": 0.98, "ci_upper": 2.15},

    {"type": "ci_consistency", "location": "Table 3, row 'Age >=65'",
     "ci_lower": 0.98, "ci_upper": 2.15, "reported_p": 0.03, "measure": "ratio"},

    {"type": "p_range", "location": "Table 3, row 'Sex'", "reported_p": "1.20"},

    {"type": "rounding_consistency", "location": "Abstract vs Table 1",
     "value_a": 45.2, "location_a": "Abstract", "value_b": 44.8,
     "location_b": "Table 1", "tolerance": 0.5},

    {"type": "p_value_format", "location": "Table 3, row 'Sex'", "reported_p": "0.03"},

    {"type": "percentage_format", "location": "Table 1, row 'Male'",
     "reported_pct": "50.0", "denominator": 300}
  ]
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("checks_file", nargs="?", help="Path to checks JSON file")
    parser.add_argument("--json-out", help="Write full results as JSON to this path")
    parser.add_argument("--only-flags", action="store_true",
                         help="Only print flagged (inconsistent) checks")
    parser.add_argument("--show-schema", action="store_true",
                         help="Print the input schema quick reference and exit")
    args = parser.parse_args()

    if args.show_schema or not args.checks_file:
        print(SCHEMA_DOC)
        if not args.checks_file:
            sys.exit(0 if args.show_schema else 1)
        return

    with open(args.checks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    checks = data.get("checks", [])
    if not checks:
        print("checks.json에 'checks' 배열이 없거나 비어 있습니다.")
        sys.exit(1)

    results = run_checks(checks)
    print_report(results, only_flags=args.only_flags)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in results], f, ensure_ascii=False, indent=2)
        print(f"결과 JSON 저장: {args.json_out}")

    # Exit code: 1 if any flags found (useful for scripting), 0 otherwise
    sys.exit(1 if any(r.status == "FLAG" for r in results) else 0)


if __name__ == "__main__":
    main()
