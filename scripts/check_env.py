"""
CowSense AI — Environment & Connection Checker
scripts/check_env.py

Run this on Day 1 (June 22) and again on June 27 morning before judging.
Verifies every external service is reachable with valid credentials.

Usage:
  python scripts/check_env.py
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}✅  {msg}{RESET}")
def fail(msg):print(f"  {RED}❌  {msg}{RESET}")
def warn(msg):print(f"  {YELLOW}⚠️   {msg}{RESET}")

results = {"passed": 0, "failed": 0, "warned": 0}

def check(label, condition, fail_msg, warn_msg=None):
    if condition:
        ok(label)
        results["passed"] += 1
    elif warn_msg:
        warn(f"{label} — {warn_msg}")
        results["warned"] += 1
    else:
        fail(f"{label} — {fail_msg}")
        results["failed"] += 1

# ── 1. Check env vars set ─────────────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  1. ENVIRONMENT VARIABLES")
print(f"{'─'*55}")

ANTHROPIC  = os.getenv("ANTHROPIC_API_KEY", "")
FEATHERLESS= os.getenv("FEATHERLESS_API_KEY", "")
NEO4J_URI  = os.getenv("NEO4J_URI", "")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "")
AT_KEY     = os.getenv("AT_API_KEY", "")

check("ANTHROPIC_API_KEY set",   ANTHROPIC.startswith("sk-ant") and len(ANTHROPIC) > 20,  "Missing or looks wrong. Get from console.anthropic.com")
check("FEATHERLESS_API_KEY set", len(FEATHERLESS) > 10,                                    "Missing. Get from featherless.ai", "Set but may not be valid")
check("NEO4J_URI set",           "neo4j" in NEO4J_URI.lower(),                             "Missing. Get from console.neo4j.io")
check("NEO4J_PASSWORD set",      len(NEO4J_PASS) > 5,                                      "Missing or too short")
check("AT_API_KEY set",          len(AT_KEY) > 5,                                          "Missing. Get from africastalking.com", "Sandbox key — OK for dev")

# ── 2. Test Anthropic API ─────────────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  2. ANTHROPIC CLAUDE API")
print(f"{'─'*55}")

async def test_anthropic():
    if not ANTHROPIC.startswith("sk-ant"):
        warn("Skipping Claude test — key not configured")
        return
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-6", "max_tokens": 50, "messages": [{"role": "user", "content": "Say: CowSense AI ready"}]}
            )
            if r.status_code == 200:
                ok(f"Claude API reachable — claude-sonnet-4-6 ✓")
                results["passed"] += 1
            else:
                fail(f"Claude API error: {r.status_code} — {r.text[:100]}")
                results["failed"] += 1
    except Exception as e:
        fail(f"Claude API unreachable: {e}")
        results["failed"] += 1

asyncio.run(test_anthropic())

# ── 3. Test Featherless ───────────────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  3. FEATHERLESS (Llama 3.1 8B)")
print(f"{'─'*55}")

async def test_featherless():
    if len(FEATHERLESS) < 5:
        warn("Skipping Featherless test — key not configured")
        return
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.featherless.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {FEATHERLESS}", "Content-Type": "application/json"},
                json={"model": "meta-llama/Meta-Llama-3.1-8B-Instruct", "max_tokens": 20,
                      "messages": [{"role": "user", "content": "Say: ready"}]}
            )
            if r.status_code == 200:
                ok("Featherless API reachable — Llama 3.1 8B ✓")
                results["passed"] += 1
            else:
                fail(f"Featherless error: {r.status_code} — {r.text[:100]}")
                results["failed"] += 1
    except Exception as e:
        fail(f"Featherless unreachable: {e}")
        results["failed"] += 1

asyncio.run(test_featherless())

# ── 4. Test Neo4j ─────────────────────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  4. NEO4J AURA")
print(f"{'─'*55}")

def test_neo4j():
    if "localhost" in NEO4J_URI:
        warn("NEO4J_URI points to localhost — update to Aura URL for production")
        return
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=("neo4j", NEO4J_PASS))
        with driver.session() as s:
            r = s.run("MATCH (n) RETURN count(n) AS total").single()
            total = r["total"] if r else 0
            if total >= 10:
                ok(f"Neo4j Aura connected — {total} nodes found (seed applied ✓)")
                results["passed"] += 1
            elif total > 0:
                warn(f"Neo4j connected but only {total} nodes — run seed.cypher!")
                results["warned"] += 1
            else:
                warn("Neo4j connected but EMPTY — run neo4j/seed.cypher first!")
                results["warned"] += 1
        driver.close()
    except Exception as e:
        fail(f"Neo4j connection failed: {e}")
        results["failed"] += 1

test_neo4j()

# ── 5. Test FastAPI running ────────────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  5. FASTAPI SERVER (localhost:8000)")
print(f"{'─'*55}")

async def test_fastapi():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:8000/")
            if r.status_code == 200:
                ok(f"FastAPI running — mode: {r.json().get('mode', '?')}")
                results["passed"] += 1
            else:
                warn(f"FastAPI returned {r.status_code}")
                results["warned"] += 1
    except Exception:
        warn("FastAPI not running — start with: uvicorn app.main:app --reload --port 8000")
        results["warned"] += 1

asyncio.run(test_fastapi())

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'═'*55}")
print(f"  RESULTS: {GREEN}{results['passed']} passed{RESET}  "
      f"{YELLOW}{results['warned']} warnings{RESET}  "
      f"{RED}{results['failed']} failed{RESET}")
print('═'*55)

if results["failed"] > 0:
    print(f"\n  {RED}Fix the failures above before proceeding.{RESET}\n")
    sys.exit(1)
elif results["warned"] > 0:
    print(f"\n  {YELLOW}Warnings exist — OK for dev, fix before hackathon day.{RESET}\n")
else:
    print(f"\n  {GREEN}All checks passed. You are ready to build. 🐄{RESET}\n")
