#!/usr/bin/env python3
"""Assert that every check in sample_checks.json yields its `_expect` status and
that no check crashes the run. Usage: python3 tests/run_tests.py"""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(here, "..", "scripts", "verify_table.py")
fixture = os.path.join(here, "sample_checks.json")
out = os.path.join(here, "_results.json")

proc = subprocess.run([sys.executable, script, fixture, "--json-out", out, "--only-flags"],
                      capture_output=True, text=True)
if "Traceback" in proc.stderr:
    print("CRASH:\n" + proc.stderr); sys.exit(2)

checks = json.load(open(fixture))["checks"]
results = json.load(open(out))
os.remove(out)
assert len(checks) == len(results), "result count mismatch"

fails = 0
for c, r in zip(checks, results):
    ok = r["status"] == c["_expect"]
    print(f"{'PASS' if ok else 'FAIL'}  [{r['status']:5}] {c['location']}" + ("" if ok else f"\n        {r['detail']}"))
    fails += not ok
print(f"\n{len(checks) - fails}/{len(checks)} passed")
sys.exit(1 if fails else 0)
