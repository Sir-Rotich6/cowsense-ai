"""
CowSense AI — Claude tool_use Agent
app/agent.py

Claude's native tool_use replaces Masumi as the agent framework.
Claude receives farmer context, decides which Neo4j tool to call,
executes it, and returns a grounded advisory.

Owns: Enock Rotich (Team Lead / AI Engineer)
Built: Day 2 — June 23, 2026
"""

import os
import json
import httpx
from pathlib import Path
from neo4j import GraphDatabase
from app.config import get_settings

settings = get_settings()

# ── Neo4j driver (singleton) ──────────────────────────────────────────────────
_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    return _driver

# ── Load system prompts from files ────────────────────────────────────────────
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(filename: str) -> str:
    try:
        return (PROMPTS_DIR / filename).read_text()
    except FileNotFoundError:
        return "You are CowSense AI, a livestock and agricultural advisor."

# ── Tool implementations ───────────────────────────────────────────────────────

def query_disease_graph(symptoms: list[str]) -> dict:
    """Query Neo4j disease knowledge graph. Source: KALRO/ILRI disease data."""
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_disease_response(symptoms)
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
                WHERE toLower(s.name) IN $symptoms
                RETURN d.name AS disease, d.id AS disease_id,
                       d.severity AS severity, d.vet_required AS vet_required,
                       d.medicine AS medicine, d.dosage AS dosage,
                       d.prevention AS prevention, d.source AS source,
                       SUM(r.weight) AS score
                ORDER BY score DESC LIMIT 3
                """,
                symptoms=[s.lower().strip() for s in symptoms]
            )
            records = [dict(r) for r in result]
        if not records:
            return {"matched": False, "message": "No matching disease found. Consider consulting a vet.", "matches": []}
        return {
            "matched": True,
            "top_disease": records[0]["disease"],
            "severity": records[0]["severity"],
            "vet_required": records[0]["vet_required"],
            "medicine": records[0]["medicine"],
            "dosage": records[0]["dosage"],
            "prevention": records[0]["prevention"],
            "source": records[0]["source"],
            "all_matches": records,
        }
    except Exception as e:
        return _mock_disease_response(symptoms)


def get_market_price(region: str, volume: float = 10.0) -> dict:
    """Get current milk price and trend from Neo4j."""
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_price_response(region, volume)
    try:
        driver = get_driver()
        with driver.session() as session:
            record = session.run(
                """
                MATCH (r:Region)-[:HAS_PRICE]->(p:MilkPrice)
                WHERE toLower(r.name) = toLower($region)
                RETURN r.name AS region, p.price_kes AS price_kes,
                       p.trend AS trend, p.note AS note, p.buyer AS buyer
                LIMIT 1
                """,
                region=region
            ).single()
            best = session.run(
                """
                MATCH (r:Region)-[:HAS_PRICE]->(p:MilkPrice)
                RETURN r.name AS region, p.price_kes AS price
                ORDER BY p.price_kes DESC LIMIT 1
                """
            ).single()
        if not record:
            return {"found": False, "message": f"No price data for: {region}"}
        return {
            "found": True,
            "region": record["region"],
            "price_kes": record["price_kes"],
            "trend": record["trend"],
            "note": record["note"],
            "buyer": record.get("buyer", "Local cooperative"),
            "volume_l": volume,
            "estimated_revenue_kes": round(record["price_kes"] * volume, 2),
            "best_region": best["region"] if best else None,
            "best_price_kes": best["price"] if best else None,
        }
    except Exception:
        return _mock_price_response(region, volume)


def calculate_credit_score(farmer_id: str) -> dict:
    """Calculate AgriFin credit score from DigiCow platform activity."""
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_credit_response(farmer_id)
    try:
        driver = get_driver()
        with driver.session() as session:
            record = session.run(
                """
                MATCH (f:Farmer {id: $farmer_id})
                RETURN f.name AS name, f.cows AS cows, f.milk_daily_l AS milk_daily_l,
                       f.mpesa_active AS mpesa_active, f.months_on_platform AS months,
                       f.vet_visits_6mo AS vet_visits,
                       f.training_modules_completed AS training
                """,
                farmer_id=farmer_id
            ).single()
        if not record:
            return {"found": False, "message": f"Farmer ID {farmer_id} not found"}
        score, reasons = 0, []
        if record["mpesa_active"]:
            score += 30; reasons.append("+30 M-Pesa active account")
        if record["months"] >= 6:
            score += 25; reasons.append(f"+25 {record['months']} months on DigiCow platform")
        if record["milk_daily_l"] >= 15:
            score += 25; reasons.append(f"+25 {record['milk_daily_l']}L/day milk production")
        if record["cows"] >= 3:
            score += 20; reasons.append(f"+20 {record['cows']} cattle assets on record")
        band = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
        loan = {"A": 150_000, "B": 80_000, "C": 30_000, "D": 0}[band]
        return {
            "found": True,
            "farmer_id": farmer_id,
            "farmer_name": record["name"],
            "score": score,
            "band": band,
            "max_loan_kes": loan,
            "breakdown": reasons,
        }
    except Exception:
        return _mock_credit_response(farmer_id)


def get_prioritized_farmers(agent_id: str = "A001") -> dict:
    """Return farmers ranked by urgency for an extension agent."""
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_farmers_response()
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (a:ExtensionAgent {id: $agent_id})-[:MANAGES]->(f:Farmer)
                RETURN f.id AS id, f.name AS name, f.region_id AS region,
                       f.cows AS cows, f.milk_daily_l AS milk_daily_l,
                       f.mpesa_active AS mpesa_active, f.months_on_platform AS months,
                       f.priority_flag AS priority_flag, f.last_advisory AS last_advisory
                """,
                agent_id=agent_id
            )
            farmers = [dict(r) for r in result]
        if not farmers:
            return _mock_farmers_response()
        ranked = []
        for f in farmers:
            p, reason = 0, "Routine check"
            flag = f.get("priority_flag", "")
            if flag == "HEALTH_CHECK":
                p, reason = 90, "Health alert — livestock symptoms reported"
            elif flag == "MARKET_OPPORTUNITY":
                p, reason = 70, "Market opportunity — sell window open"
            elif flag == "CREDIT_OPPORTUNITY":
                p, reason = 60, "AgriFin — ready for credit profile"
            elif f["months"] < 4:
                p, reason = 50, "New farmer — onboarding support needed"
            elif f["milk_daily_l"] < 12:
                p, reason = 40, "Below-average production — advisory needed"
            else:
                p, reason = 20, "Regular check-in due"
            ranked.append({
                "farmer_id": f["id"],
                "name": f["name"],
                "region": f["region"],
                "priority_score": p,
                "reason": reason,
                "urgency": "HIGH" if p >= 70 else "MEDIUM" if p >= 40 else "LOW",
                "last_advisory": f.get("last_advisory", "Unknown"),
            })
        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        return {"agent_id": agent_id, "farmers": ranked}
    except Exception:
        return _mock_farmers_response()

# ── Mock responses (demo mode / Neo4j offline) ────────────────────────────────

def _mock_disease_response(symptoms: list[str]) -> dict:
    sym = [s.lower() for s in symptoms]
    if any(s in sym for s in ["high fever", "swollen lymph nodes", "difficulty breathing"]):
        return {"matched": True, "top_disease": "East Coast Fever (ECF)", "severity": "HIGH",
                "vet_required": True, "medicine": "Buparvaquone (Butalex®)",
                "dosage": "2.5 mg/kg body weight — single intramuscular injection",
                "prevention": "Acaricide tick control, immunisation (ITM)",
                "source": "KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "all_matches": []}
    if any(s in sym for s in ["swollen udder", "blood in milk", "hot udder"]):
        return {"matched": True, "top_disease": "Mastitis", "severity": "MEDIUM",
                "vet_required": False, "medicine": "Intramammary Amoxicillin/Cloxacillin",
                "dosage": "1 tube per affected quarter, twice daily for 3 days. Strip 3× daily.",
                "prevention": "Pre/post-dip teats with iodine after every milking",
                "source": "KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "all_matches": []}
    if any(s in sym for s in ["bloated", "bloated left flank", "grunting"]):
        return {"matched": True, "top_disease": "Bloat (Ruminal Tympany)", "severity": "HIGH",
                "vet_required": True, "medicine": "500ml vegetable oil via stomach tube",
                "dosage": "Walk the animal immediately. Trocar/cannula for free-gas bloat.",
                "prevention": "Introduce lush pasture gradually; feed dry roughage first",
                "source": "KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "all_matches": []}
    return {"matched": False, "message": "Symptoms not conclusively matched. Consult a vet."}

def _mock_price_response(region: str, volume: float) -> dict:
    prices = {
        "nakuru": {"price_kes": 52, "trend": "RISING",  "note": "Brookside Dairy active", "buyer": "Brookside Dairy"},
        "eldoret": {"price_kes": 46, "trend": "STABLE",  "note": "Moi Milk active",        "buyer": "Moi Milk"},
        "nairobi": {"price_kes": 55, "trend": "STABLE",  "note": "Premium urban buyers",   "buyer": "KCC / Direct"},
        "kisii":   {"price_kes": 50, "trend": "RISING",  "note": "KCC collection active",   "buyer": "KCC Kisii"},
        "meru":    {"price_kes": 48, "trend": "FALLING", "note": "Seasonal oversupply",     "buyer": "Githunguri"},
        "embu":    {"price_kes": 44, "trend": "STABLE",  "note": "Co-op daily 6am",         "buyer": "Embu Co-op"},
        "kericho": {"price_kes": 50, "trend": "RISING",  "note": "Tea region premium",      "buyer": "Kericho Co-op"},
        "bomet":   {"price_kes": 48, "trend": "STABLE",  "note": "Daily collection",        "buyer": "Local co-op"},
    }
    r = region.lower().strip()
    data = prices.get(r, prices["nakuru"])
    return {
        "found": True, "region": region.title(),
        "price_kes": data["price_kes"], "trend": data["trend"],
        "note": data["note"], "buyer": data["buyer"],
        "volume_l": volume,
        "estimated_revenue_kes": round(data["price_kes"] * volume, 2),
        "best_region": "Nairobi", "best_price_kes": 55,
    }

def _mock_credit_response(farmer_id: str) -> dict:
    farmers = {
        "F001": {"name": "Wanjiku Kamau",  "cows": 3, "milk": 18, "mpesa": True,  "months": 8,  "score": 80, "band": "A", "loan": 150_000},
        "F002": {"name": "Kipchumba Rono", "cows": 5, "milk": 30, "mpesa": True,  "months": 14, "score": 100,"band": "A", "loan": 150_000},
        "F003": {"name": "Achieng Otieno", "cows": 2, "milk": 10, "mpesa": False, "months": 3,  "score": 20, "band": "D", "loan": 0},
        "F004": {"name": "Mwangi Githinji","cows": 4, "milk": 22, "mpesa": True,  "months": 11, "score": 100,"band": "A", "loan": 150_000},
        "F005": {"name": "Jepchirchir Sang","cows": 6, "milk": 35,"mpesa": True,  "months": 18, "score": 100,"band": "A", "loan": 150_000},
    }
    f = farmers.get(farmer_id)
    if not f:
        return {"found": False, "message": f"Farmer {farmer_id} not found. Demo IDs: F001–F005"}
    return {"found": True, "farmer_id": farmer_id, "farmer_name": f["name"],
            "score": f["score"], "band": f["band"], "max_loan_kes": f["loan"],
            "breakdown": ["Demo mode — connect Neo4j for live scoring"]}

def _mock_farmers_response() -> dict:
    return {"agent_id": "A001", "farmers": [
        {"farmer_id": "F001", "name": "Wanjiku Kamau",  "region": "R001", "priority_score": 90, "reason": "Health alert — cow symptoms reported", "urgency": "HIGH", "last_advisory": "2026-06-10"},
        {"farmer_id": "F002", "name": "Kipchumba Rono", "region": "R002", "priority_score": 70, "reason": "Market opportunity — sell window open",  "urgency": "HIGH", "last_advisory": "2026-06-18"},
        {"farmer_id": "F004", "name": "Mwangi Githinji","region": "R001", "priority_score": 20, "reason": "Regular check-in due",                  "urgency": "LOW",  "last_advisory": "2026-06-15"},
    ]}

# ── Tool registry ─────────────────────────────────────────────────────────────
TOOLS = [
    {"name": "query_disease_graph", "description": "Query the Neo4j livestock disease knowledge graph (KALRO/ILRI data) to find the most likely disease(s) for given symptoms. Returns disease name, severity, vet requirement, medicine, and dosage.", "input_schema": {"type": "object", "properties": {"symptoms": {"type": "array", "items": {"type": "string"}, "description": "Symptom list e.g. ['high fever', 'swollen lymph nodes']"}}, "required": ["symptoms"]}},
    {"name": "get_market_price", "description": "Get current milk market price per litre (KES) and trend for a Kenyan region, plus estimated revenue for the farmer's volume.", "input_schema": {"type": "object", "properties": {"region": {"type": "string", "description": "Region name: nakuru, eldoret, nairobi, kisii, meru, embu, kericho, bomet"}, "volume": {"type": "number", "description": "Milk volume in litres"}}, "required": ["region"]}},
    {"name": "calculate_credit_score", "description": "Calculate AgriFin credit score from DigiCow platform activity. Returns score (0–100), band (A–D), max loan eligibility in KES.", "input_schema": {"type": "object", "properties": {"farmer_id": {"type": "string", "description": "Farmer ID e.g. F001, F002, F003"}}, "required": ["farmer_id"]}},
    {"name": "get_prioritized_farmers", "description": "Get ranked list of farmers for an extension agent, ordered by urgency across health risk, market opportunity, and AgriFin readiness.", "input_schema": {"type": "object", "properties": {"agent_id": {"type": "string", "description": "Extension agent ID e.g. A001"}}, "required": []}},
]

def dispatch_tool(name: str, inputs: dict) -> str:
    if name == "query_disease_graph":     result = query_disease_graph(**inputs)
    elif name == "get_market_price":       result = get_market_price(**inputs)
    elif name == "calculate_credit_score": result = calculate_credit_score(**inputs)
    elif name == "get_prioritized_farmers":result = get_prioritized_farmers(**inputs)
    else:                                  result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result)

# ── Main agent loop ────────────────────────────────────────────────────────────
async def run_agent(user_message: str, feature: str, farmer_context: dict | None = None) -> dict:
    """
    Two-turn Claude tool_use agent.
    feature: "health" | "market" | "credit" | "prioritize"
    """
    prompt_map = {"health": "health_system.txt", "market": "market_system.txt", "credit": "credit_system.txt"}
    system = _load_prompt(prompt_map.get(feature, "health_system.txt"))

    context = f"\nFarmer context: {json.dumps(farmer_context)}" if farmer_context else ""
    messages = [{"role": "user", "content": user_message + context}]

    headers = {"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": settings.claude_model, "max_tokens": 1024, "system": system, "tools": TOOLS, "messages": messages}

    if settings.is_demo_mode:
        return {"advisory": "[DEMO MODE] Set ANTHROPIC_API_KEY to enable live Claude advisory.", "tool_used": None, "tool_result": None, "urgency_label": "ℹ️ Demo mode"}

    async with httpx.AsyncClient(timeout=60) as client:
        r1 = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        d1 = r1.json()

        tool_used, tool_result = None, None
        if d1.get("stop_reason") == "tool_use":
            tb = next(b for b in d1["content"] if b["type"] == "tool_use")
            tool_used = tb["name"]
            tool_result = json.loads(dispatch_tool(tool_used, tb["input"]))
            messages.append({"role": "assistant", "content": d1["content"]})
            messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": tb["id"], "content": json.dumps(tool_result)}]})
            r2 = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json={**payload, "messages": messages, "max_tokens": 512})
            d1 = r2.json()

        advisory = "".join(b.get("text", "") for b in d1.get("content", []) if b.get("type") == "text")
        urgency = _urgency_label(tool_result)
        return {"advisory": advisory, "tool_used": tool_used, "tool_result": tool_result, "urgency_label": urgency}

def _urgency_label(tr: dict | None) -> str:
    if not tr: return "ℹ️ Advisory generated"
    if tr.get("severity") == "HIGH":    return "🚨 URGENT — Call vet now"
    if tr.get("severity") == "MEDIUM":  return "⚠️ Act today"
    if tr.get("severity") == "LOW":     return "✅ Manageable — treat at home"
    if tr.get("trend") == "RISING":     return "📈 Sell now — price rising"
    if tr.get("trend") == "FALLING":    return "📉 Consider holding"
    band = tr.get("band", "")
    if band == "A": return "⭐ Band A — top loan tier"
    if band == "B": return "✅ Band B — standard loan eligible"
    if band == "C": return "⚠️ Band C — micro-loan only"
    if band == "D": return "🔴 Not yet eligible — build history"
    return "ℹ️ Advisory generated"
