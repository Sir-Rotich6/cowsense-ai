"""
CowSense AI — Demo Test Runner
tests/demo_test.py

Runs all 3 judging scenarios and validates outputs.
Run this before every demo rehearsal.

Usage:
  python tests/demo_test.py
  python tests/demo_test.py --base-url https://cowsense-api.onrender.com
"""

import httpx
import json
import sys
import argparse

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8000")
    return p.parse_args()

def section(num, title):
    print(f"\n{'═'*60}")
    print(f"  SCENARIO {num}: {title}")
    print('═'*60)

def ok(label, value):
    print(f"  ✅  {label}: {value}")

def warn(label, value):
    print(f"  ⚠️   {label}: {value}")

def show(data, keys):
    for k in keys:
        val = data.get(k, "—")
        if val:
            print(f"  {k:25s}: {val}")

def main():
    args = parse_args()
    BASE = args.base_url.rstrip("/")
    print(f"\n🐄 CowSense AI — Demo Test Runner")
    print(f"   Base URL: {BASE}")

    # ── STATUS CHECK ──────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("  STATUS CHECK")
    print(f"{'─'*60}")
    try:
        r = httpx.get(f"{BASE}/", timeout=10)
        d = r.json()
        ok("Service", d.get("service"))
        ok("Version", d.get("version"))
        ok("Mode",    d.get("mode"))
        ok("Status",  d.get("status"))
    except Exception as e:
        print(f"  ❌  Cannot reach {BASE}: {e}")
        sys.exit(1)

    # ── SCENARIO 1: HEALTH TRIAGE ─────────────────────────────────────
    section(1, "HEALTH TRIAGE — East Coast Fever (Wanjiku, Nakuru)")
    payload = {"farmer_id": "F001", "symptoms": ["high fever", "swollen lymph nodes"], "cow_age_years": 4, "region": "nakuru"}
    print(f"\n  Input: {json.dumps(payload, indent=4)}\n")

    r = httpx.post(f"{BASE}/health-check", json=payload, timeout=30)
    d = r.json()

    ok("Status code",   r.status_code)
    ok("Top diagnosis", d.get("top_diagnosis"))
    ok("Severity",      d.get("severity"))
    ok("Vet required",  d.get("vet_required"))
    ok("Medicine",      d.get("medicine"))
    ok("Urgency",       d.get("urgency_label"))
    print(f"\n  AI Advisory:\n  {'─'*50}")
    print(f"  {d.get('ai_advisory', '')}")
    print(f"  {'─'*50}")

    assert "East Coast Fever" in str(d.get("top_diagnosis", "")), "❌ Expected East Coast Fever!"
    assert d.get("severity") == "HIGH", "❌ Expected HIGH severity!"
    print("\n  ✅  Scenario 1 PASSED")

    # ── SCENARIO 2: MARKET PRICE ──────────────────────────────────────
    section(2, "MARKET PRICE — Kipchumba, Eldoret, 30L")
    payload = {"farmer_id": "F002", "region": "eldoret", "milk_volume_l": 30}
    print(f"\n  Input: {json.dumps(payload, indent=4)}\n")

    r = httpx.post(f"{BASE}/market-price", json=payload, timeout=30)
    d = r.json()

    ok("Status code",   r.status_code)
    ok("Region",        d.get("region"))
    ok("Price (KES/L)", d.get("price_kes_per_litre"))
    ok("Trend",         d.get("trend"))
    ok("Buyer",         d.get("buyer"))
    ok("Revenue (KES)", d.get("estimated_revenue_kes"))
    ok("Urgency",       d.get("urgency_label"))
    print(f"\n  AI Advisory:\n  {'─'*50}")
    print(f"  {d.get('ai_advisory', '')}")
    print(f"  {'─'*50}")

    assert d.get("price_kes_per_litre") is not None, "❌ No price returned!"
    print("\n  ✅  Scenario 2 PASSED")

    # ── SCENARIO 3: CREDIT PROFILE ────────────────────────────────────
    section(3, "CREDIT PROFILE — Kipchumba Rono (F002)")
    payload = {"farmer_id": "F002"}
    print(f"\n  Input: {json.dumps(payload, indent=4)}\n")

    r = httpx.post(f"{BASE}/credit-profile", json=payload, timeout=30)
    d = r.json()

    ok("Status code",   r.status_code)
    ok("Farmer name",   d.get("farmer_name"))
    ok("Credit score",  d.get("credit_score"))
    ok("Credit band",   d.get("credit_band"))
    ok("Max loan (KES)",d.get("max_loan_kes"))
    ok("Urgency",       d.get("urgency_label"))
    print("\n  Score breakdown:")
    for item in d.get("score_breakdown", []):
        print(f"    · {item}")
    print(f"\n  AI Advisory:\n  {'─'*50}")
    print(f"  {d.get('ai_advisory', '')}")
    print(f"  {'─'*50}")

    assert d.get("credit_band") in ["A", "B", "C", "D"], "❌ Invalid credit band!"
    print("\n  ✅  Scenario 3 PASSED")

    # ── FARMER PRIORITIZATION ─────────────────────────────────────────
    section("4", "PRIORITIZE FARMERS — Agent A001")
    r = httpx.get(f"{BASE}/prioritize-farmers", timeout=15)
    d = r.json()
    ok("Total farmers", d.get("total_farmers"))
    for i, f in enumerate(d.get("prioritized_list", [])[:3]):
        print(f"  #{i+1}  [{f.get('urgency')}] {f.get('name')} — {f.get('reason')}")
    print("\n  ✅  Farmer list returned")

    # ── SUMMARY ───────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  ✅  ALL SCENARIOS PASSED — CowSense AI is demo-ready")
    print('═'*60)
    print(f"\n  API docs: {BASE}/docs")
    print(f"  Run again before every demo rehearsal.\n")

if __name__ == "__main__":
    main()
