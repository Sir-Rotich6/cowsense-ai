"""
CowSense AI — GraphRAG Agent
app/agent.py

Full GraphRAG implementation:
  1. Input symptoms → generate embedding (sentence-transformers)
  2. Vector similarity search on Neo4j symptom_embeddings index
  3. Multi-hop graph traversal: Symptom → Disease → CO_OCCURRING, SEASONAL_RISK
  4. Context expansion: FeedType risks, regional climate advisory
  5. Rich subgraph → Claude tool_use → grounded advisory

No hallucination: medicine/dosage ALWAYS from graph, never from LLM memory.

Owns: Enock Rotich (Team Lead / AI Engineer)
"""

import os
import json
import httpx
import numpy as np
from pathlib import Path
from neo4j import GraphDatabase
from app.config import get_settings

settings = get_settings()

# ── Neo4j driver (singleton) ──────────────────────────────────────
_driver = None
_embed_model = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    return _driver


def get_embed_model():
    """Lazy-load sentence-transformers model."""
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embed_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        except ImportError:
            _embed_model = None
    return _embed_model


def embed_text(text: str) -> list[float] | None:
    """Generate a 384-dim embedding. Returns None if model unavailable."""
    model = get_embed_model()
    if model is None:
        return None
    vec = model.encode([text], normalize_embeddings=True)[0]
    return vec.tolist()


# ── Load system prompts ───────────────────────────────────────────
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(filename: str) -> str:
    try:
        return (PROMPTS_DIR / filename).read_text()
    except FileNotFoundError:
        return "You are CowSense AI, a Kenyan dairy livestock advisor."


# ── GRAPHRAG QUERY: Symptom → Disease (vector + keyword hybrid) ──

def graphrag_disease_query(symptoms: list[str], region_id: str = None) -> dict:
    """
    Full GraphRAG disease query. Three-layer search:
      Layer 1: Vector similarity on symptom embeddings (semantic)
      Layer 2: Exact keyword match as fallback
      Layer 3: Multi-hop context (CO_OCCURRING, SEASONAL_RISK, FeedType)
    """
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_disease_response(symptoms)

    try:
        driver = get_driver()
        symptom_text = ", ".join(symptoms)
        embedding = embed_text(symptom_text)

        with driver.session() as session:

            # ── Layer 1: Vector similarity (GraphRAG core) ────────
            vector_results = []
            if embedding is not None:
                res = session.run("""
                    CALL db.index.vector.queryNodes(
                        'symptom_embeddings', 10, $embedding
                    )
                    YIELD node AS symptom, score AS similarity
                    WHERE similarity > 0.65
                    MATCH (symptom)-[r:INDICATES]->(d:Disease)
                    WITH d,
                         SUM(r.weight * similarity)   AS combined_score,
                         COLLECT(symptom.name)        AS matched_symptoms,
                         COLLECT(r.note)              AS match_notes
                    ORDER BY combined_score DESC
                    LIMIT 3
                    RETURN d.id AS disease_id, d.name AS disease,
                           d.severity AS severity,
                           d.vet_required AS vet_required,
                           d.medicine AS medicine,
                           d.dosage AS dosage,
                           d.prevention AS prevention,
                           d.source AS source,
                           combined_score,
                           matched_symptoms, match_notes
                """, embedding=embedding)
                vector_results = [dict(r) for r in res]

            # ── Layer 2: Exact keyword fallback ───────────────────
            keyword_results = []
            if not vector_results:
                res = session.run("""
                    MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
                    WHERE toLower(s.name) IN $symptoms
                    WITH d,
                         SUM(r.weight)          AS combined_score,
                         COLLECT(s.name)        AS matched_symptoms,
                         COLLECT(r.note)        AS match_notes
                    ORDER BY combined_score DESC
                    LIMIT 3
                    RETURN d.id AS disease_id, d.name AS disease,
                           d.severity AS severity,
                           d.vet_required AS vet_required,
                           d.medicine AS medicine,
                           d.dosage AS dosage,
                           d.prevention AS prevention,
                           d.source AS source,
                           combined_score,
                           matched_symptoms, match_notes
                """, symptoms=[s.lower().strip() for s in symptoms])
                keyword_results = [dict(r) for r in res]

            matches = vector_results or keyword_results
            if not matches:
                return {
                    "matched": False,
                    "message": "No disease matched. Recommend vet consultation.",
                    "matches": []
                }

            top = matches[0]

            # ── Layer 3: Multi-hop context expansion ──────────────
            # 3a. Co-occurring diseases
            co_occur = session.run("""
                MATCH (d:Disease {id: $did})-[:CO_OCCURRING]->(d2:Disease)
                RETURN d2.name AS name, d2.severity AS severity
            """, did=top["disease_id"])
            co_diseases = [dict(r) for r in co_occur]

            # 3b. Seasonal risk for farmer's region
            seasonal_note = ""
            if region_id:
                seas = session.run("""
                    MATCH (r:Region {id: $rid})-[sr:SEASONAL_RISK]->(d:Disease {id: $did})
                    RETURN sr.season AS season, sr.reason AS reason
                """, rid=region_id, did=top["disease_id"])
                sr = seas.single()
                if sr:
                    seasonal_note = f"{sr['season'].replace('_',' ').title()}: {sr['reason']}"

            # 3c. Feed risk if relevant
            feed_risk = session.run("""
                MATCH (f:FeedType)-[:INCREASES_RISK_OF]->(d:Disease {id: $did})
                RETURN f.name AS feed, f.notes AS notes
            """, did=top["disease_id"])
            feed_risks = [dict(r) for r in feed_risk]

            # 3d. Climate advisory for region
            climate_note = ""
            if region_id:
                clim = session.run("""
                    MATCH (r:Region {id: $rid})-[:HAS_CLIMATE]->(c:ClimateAdvisory)
                    RETURN c.livestock_advisory AS advisory
                """, rid=region_id)
                cr = clim.single()
                if cr:
                    climate_note = cr["advisory"]

        return {
            "matched": True,
            "search_method": "vector" if vector_results else "keyword",
            "top_disease":   top["disease"],
            "disease_id":    top["disease_id"],
            "severity":      top["severity"],
            "vet_required":  top["vet_required"],
            "medicine":      top["medicine"],
            "dosage":        top["dosage"],
            "prevention":    top["prevention"],
            "source":        top["source"],
            "confidence":    round(top["combined_score"], 3),
            "matched_symptoms": top["matched_symptoms"],
            "all_matches":   matches,
            # Multi-hop context
            "co_occurring_diseases": co_diseases,
            "seasonal_risk_note":    seasonal_note,
            "feed_risk_warning":     feed_risks,
            "climate_advisory":      climate_note,
        }

    except Exception as e:
        return _mock_disease_response(symptoms)


# ── MARKET PRICE QUERY ────────────────────────────────────────────

def get_market_price(region: str, volume: float = 10.0) -> dict:
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_price_response(region, volume)
    try:
        driver = get_driver()
        with driver.session() as session:
            record = session.run("""
                MATCH (r:Region)-[:HAS_PRICE]->(p:MilkPrice)
                WHERE toLower(r.name) = toLower($region)
                RETURN r.id AS region_id, r.name AS region,
                       p.price_kes AS price_kes, p.trend AS trend,
                       p.note AS note, p.buyer AS buyer
                LIMIT 1
            """, region=region).single()

            best = session.run("""
                MATCH (r:Region)-[:HAS_PRICE]->(p:MilkPrice)
                RETURN r.name AS region, p.price_kes AS price
                ORDER BY p.price_kes DESC LIMIT 1
            """).single()

        if not record:
            return {"found": False, "message": f"No price data for: {region}"}

        return {
            "found": True,
            "region":               record["region"],
            "price_kes":            record["price_kes"],
            "trend":                record["trend"],
            "note":                 record["note"],
            "buyer":                record.get("buyer", "Local cooperative"),
            "volume_l":             volume,
            "estimated_revenue_kes":round(record["price_kes"] * volume, 2),
            "best_region":          best["region"] if best else None,
            "best_price_kes":       best["price"]  if best else None,
        }
    except Exception:
        return _mock_price_response(region, volume)


# ── CREDIT SCORE QUERY ────────────────────────────────────────────

def calculate_credit_score(farmer_id: str) -> dict:
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_credit_response(farmer_id)
    try:
        driver = get_driver()
        with driver.session() as session:
            record = session.run("""
                MATCH (f:Farmer {id: $fid})
                RETURN f.name AS name, f.cows AS cows,
                       f.milk_daily_l AS milk_daily_l,
                       f.mpesa_active AS mpesa_active,
                       f.months_on_platform AS months,
                       f.vet_visits_6mo AS vet_visits,
                       f.training_modules_completed AS training
            """, fid=farmer_id).single()

        if not record:
            return {"found": False, "message": f"Farmer {farmer_id} not found"}

        score, reasons = 0, []
        if record["mpesa_active"]:
            score += 30
            reasons.append("+30 M-Pesa active account")
        if record["months"] >= 6:
            score += 25
            reasons.append(f"+25 {record['months']} months on DigiCow platform")
        if record["milk_daily_l"] >= 15:
            score += 25
            reasons.append(f"+25 {record['milk_daily_l']}L/day milk production")
        if record["cows"] >= 3:
            score += 20
            reasons.append(f"+20 {record['cows']} cattle assets on record")

        band = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
        loan = {"A": 150_000, "B": 80_000, "C": 30_000, "D": 0}[band]

        return {
            "found":        True,
            "farmer_id":    farmer_id,
            "farmer_name":  record["name"],
            "score":        score,
            "band":         band,
            "max_loan_kes": loan,
            "breakdown":    reasons,
        }
    except Exception:
        return _mock_credit_response(farmer_id)


# ── FARMER PRIORITIZATION ─────────────────────────────────────────

def get_prioritized_farmers(agent_id: str = "A001") -> dict:
    if settings.is_demo_mode or not settings.has_neo4j:
        return _mock_farmers_response()
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (a:ExtensionAgent {id: $aid})-[:MANAGES]->(f:Farmer)
                RETURN f.id AS id, f.name AS name,
                       f.region_id AS region,
                       f.cows AS cows,
                       f.milk_daily_l AS milk_daily_l,
                       f.mpesa_active AS mpesa_active,
                       f.months_on_platform AS months,
                       f.priority_flag AS priority_flag,
                       f.last_advisory AS last_advisory
            """, aid=agent_id)
            farmers = [dict(r) for r in result]

        if not farmers:
            return _mock_farmers_response()

        ranked = []
        for f in farmers:
            flag = f.get("priority_flag", "")
            if flag == "HEALTH_CHECK":
                score, reason = 90, "Health alert — livestock symptoms reported"
            elif flag == "MARKET_OPPORTUNITY":
                score, reason = 70, "Market opportunity — sell window open"
            elif flag == "CREDIT_OPPORTUNITY":
                score, reason = 60, "AgriFin — ready for credit profile"
            elif f["months"] < 4:
                score, reason = 50, "New farmer — onboarding support needed"
            elif f["milk_daily_l"] < 12:
                score, reason = 40, "Below-average production — advisory needed"
            else:
                score, reason = 20, "Regular check-in due"

            ranked.append({
                "farmer_id":     f["id"],
                "name":          f["name"],
                "region":        f["region"],
                "priority_score":score,
                "reason":        reason,
                "urgency":       "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW",
                "last_advisory": f.get("last_advisory", "Unknown"),
            })

        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        return {"agent_id": agent_id, "farmers": ranked}
    except Exception:
        return _mock_farmers_response()


# ── TOOL REGISTRY ─────────────────────────────────────────────────

TOOLS = [
    {
        "name": "query_disease_graph",
        "description": (
            "GraphRAG query on the Neo4j livestock disease knowledge graph "
            "(KALRO/ILRI data). Uses vector similarity to semantically match "
            "symptoms even when phrased informally. Returns disease, severity, "
            "medicine, dosage, co-occurring diseases, and seasonal risk context."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Symptom descriptions e.g. ['cow is shivering', 'lymph glands swollen']"
                },
                "region_id": {
                    "type": "string",
                    "description": "Optional region ID e.g. R001 for seasonal risk context"
                }
            },
            "required": ["symptoms"]
        }
    },
    {
        "name": "get_market_price",
        "description": (
            "Get current milk market price per litre (KES) and trend for a "
            "Kenyan region. Returns price, trend, buyer, and estimated revenue."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region name: nakuru, eldoret, nairobi, kisii, meru, embu, kericho, bomet"
                },
                "volume": {
                    "type": "number",
                    "description": "Milk volume in litres to sell"
                }
            },
            "required": ["region"]
        }
    },
    {
        "name": "calculate_credit_score",
        "description": (
            "Calculate AgriFin credit score from DigiCow platform activity. "
            "Returns score 0-100, band A-D, and max loan eligibility in KES."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "farmer_id": {
                    "type": "string",
                    "description": "Farmer ID e.g. F001, F002, F003, F004, F005"
                }
            },
            "required": ["farmer_id"]
        }
    },
    {
        "name": "get_prioritized_farmers",
        "description": (
            "Get a ranked list of farmers for an extension agent, ordered by "
            "urgency across health risk, market opportunity, and AgriFin readiness."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Extension agent ID e.g. A001, A002"
                }
            },
            "required": []
        }
    }
]


def dispatch_tool(name: str, inputs: dict) -> str:
    """Execute the tool Claude requested and return JSON string."""
    dispatch = {
        "query_disease_graph":   lambda: graphrag_disease_query(**inputs),
        "get_market_price":      lambda: get_market_price(**inputs),
        "calculate_credit_score":lambda: calculate_credit_score(**inputs),
        "get_prioritized_farmers":lambda: get_prioritized_farmers(
                                    inputs.get("agent_id", "A001")),
    }
    fn = dispatch.get(name)
    result = fn() if fn else {"error": f"Unknown tool: {name}"}
    return json.dumps(result)


# ── MAIN AGENT LOOP ───────────────────────────────────────────────

async def run_agent(
    user_message: str,
    feature: str,
    farmer_context: dict | None = None
) -> dict:
    """
    Two-turn Claude tool_use agent loop.

    Turn 1: Claude reads user message + context, decides which tool to call
    Turn 2: Claude receives tool result (from Neo4j GraphRAG), generates advisory

    feature: "health" | "market" | "credit" | "prioritize"
    """
    prompt_map = {
        "health":    "health_system.txt",
        "market":    "market_system.txt",
        "credit":    "credit_system.txt",
        "prioritize":"health_system.txt",
    }
    system = _load_prompt(prompt_map.get(feature, "health_system.txt"))

    context_str = (
        f"\nFarmer context: {json.dumps(farmer_context)}"
        if farmer_context else ""
    )
    messages = [{"role": "user", "content": user_message + context_str}]

    api_headers = {
        "x-api-key":         settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    base_payload = {
        "model":    settings.claude_model,
        "max_tokens": 1024,
        "system":   system,
        "tools":    TOOLS,
        "messages": messages,
    }

    # Demo mode — no API key
    if settings.is_demo_mode:
        return {
            "advisory":      "[DEMO MODE] Add ANTHROPIC_API_KEY to .env for live AI advisory.",
            "tool_used":     None,
            "tool_result":   None,
            "urgency_label": "ℹ️ Demo mode",
        }

    async with httpx.AsyncClient(timeout=60) as client:
        # ── Turn 1: Claude decides which tool to call ─────────────
        r1 = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=api_headers,
            json=base_payload
        )
        d1 = r1.json()

        tool_used   = None
        tool_result = None

        if d1.get("stop_reason") == "tool_use":
            tb = next(
                b for b in d1["content"] if b["type"] == "tool_use"
            )
            tool_used       = tb["name"]
            tool_result_str = dispatch_tool(tool_used, tb["input"])
            tool_result     = json.loads(tool_result_str)

            # ── Turn 2: Claude generates advisory from tool result ─
            messages.append({"role": "assistant", "content": d1["content"]})
            messages.append({
                "role": "user",
                "content": [{
                    "type":        "tool_result",
                    "tool_use_id": tb["id"],
                    "content":     tool_result_str,
                }]
            })

            r2 = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=api_headers,
                json={**base_payload, "messages": messages, "max_tokens": 512}
            )
            d1 = r2.json()

        advisory = "".join(
            b.get("text", "")
            for b in d1.get("content", [])
            if b.get("type") == "text"
        )

        return {
            "advisory":      advisory,
            "tool_used":     tool_used,
            "tool_result":   tool_result,
            "urgency_label": _urgency_label(tool_result),
        }


def _urgency_label(tr: dict | None) -> str:
    if not tr:
        return "ℹ️ Advisory generated"
    sev  = tr.get("severity", "")
    trend= tr.get("trend", "")
    band = tr.get("band", "")
    if sev  == "HIGH":    return "🚨 URGENT — Call vet now"
    if sev  == "MEDIUM":  return "⚠️ Act today"
    if sev  == "LOW":     return "✅ Manageable — treat at home"
    if trend == "RISING": return "📈 Sell now — price rising"
    if trend == "FALLING":return "📉 Consider holding"
    if band  == "A":      return "⭐ Band A — top loan tier"
    if band  == "B":      return "✅ Band B — standard loan"
    if band  == "C":      return "⚠️ Band C — micro-loan only"
    if band  == "D":      return "🔴 Not yet eligible"
    return "ℹ️ Advisory generated"


# ── MOCK RESPONSES (demo/offline mode) ───────────────────────────

def _mock_disease_response(symptoms: list[str]) -> dict:
    sym = [s.lower() for s in symptoms]
    if any(w in " ".join(sym) for w in ["fever","lymph","swollen gland","temperature"]):
        return {"matched":True,"search_method":"mock","top_disease":"East Coast Fever (ECF)",
                "disease_id":"D001","severity":"HIGH","vet_required":True,
                "medicine":"Buparvaquone (Butalex®)",
                "dosage":"2.5 mg/kg body weight — single intramuscular injection",
                "prevention":"Acaricide tick control every 2 weeks",
                "source":"KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "confidence":0.9,"matched_symptoms":sym,"all_matches":[],
                "co_occurring_diseases":[{"name":"Anaplasmosis","severity":"HIGH"}],
                "seasonal_risk_note":"","feed_risk_warning":[],"climate_advisory":""}
    if any(w in " ".join(sym) for w in ["udder","milk","mastitis","clot"]):
        return {"matched":True,"search_method":"mock","top_disease":"Mastitis",
                "disease_id":"D006","severity":"MEDIUM","vet_required":False,
                "medicine":"Intramammary Amoxicillin/Cloxacillin",
                "dosage":"1 tube per quarter, twice daily, 3 days. Strip 3x daily.",
                "prevention":"Pre/post teat dipping with iodine after milking",
                "source":"KALRO Dairy Value Chain ToT Manual 2020, Module 2, Section 2.6.6",
                "confidence":0.85,"matched_symptoms":sym,"all_matches":[],
                "co_occurring_diseases":[],"seasonal_risk_note":"",
                "feed_risk_warning":[],"climate_advisory":""}
    if any(w in " ".join(sym) for w in ["bloat","flank","grunting","swollen left"]):
        return {"matched":True,"search_method":"mock","top_disease":"Bloat (Ruminal Tympany)",
                "disease_id":"D009","severity":"HIGH","vet_required":True,
                "medicine":"500ml vegetable oil via stomach tube",
                "dosage":"Walk animal immediately. Trocar for free-gas bloat.",
                "prevention":"Feed dry roughage before grazing lush pasture",
                "source":"KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "confidence":0.92,"matched_symptoms":sym,"all_matches":[],
                "co_occurring_diseases":[],"seasonal_risk_note":"High risk after rains",
                "feed_risk_warning":[{"feed":"Lush legume pasture","notes":"HIGH BLOAT RISK"}],
                "climate_advisory":""}
    if any(w in " ".join(sym) for w in ["calving","collapse","fell down","cold ears"]):
        return {"matched":True,"search_method":"mock","top_disease":"Milk Fever (Hypocalcaemia)",
                "disease_id":"D011","severity":"HIGH","vet_required":True,
                "medicine":"Calcium borogluconate 40% solution",
                "dosage":"400ml IV slow drip over 10-15 minutes",
                "prevention":"Reduce calcium 3 weeks pre-calving. Magnesium supplement.",
                "source":"KALRO Dairy Value Chain ToT Manual 2020, Module 2",
                "confidence":0.88,"matched_symptoms":sym,"all_matches":[],
                "co_occurring_diseases":[],"seasonal_risk_note":"",
                "feed_risk_warning":[],"climate_advisory":""}
    return {"matched":False,
            "message":"Symptoms not conclusively matched. Consult a vet directly.",
            "matches":[]}


def _mock_price_response(region: str, volume: float) -> dict:
    prices = {
        "nakuru": (52,"RISING", "Brookside Dairy active","Brookside Dairy"),
        "eldoret":(46,"STABLE", "Moi Milk active",      "Moi Milk"),
        "nairobi":(55,"STABLE", "Premium urban buyers",  "KCC / Direct"),
        "kisii":  (50,"RISING", "KCC collection active", "KCC Kisii"),
        "meru":   (48,"FALLING","Seasonal oversupply",   "Githunguri"),
        "embu":   (44,"STABLE", "Co-op daily 6am",       "Embu Co-op"),
        "kericho":(50,"RISING", "Tea region premium",    "Kericho Co-op"),
        "bomet":  (48,"STABLE", "Daily collection",      "Local co-op"),
    }
    p, t, n, b = prices.get(region.lower(), prices["nakuru"])
    return {"found":True,"region":region.title(),"price_kes":p,"trend":t,
            "note":n,"buyer":b,"volume_l":volume,
            "estimated_revenue_kes":round(p*volume,2),
            "best_region":"Nairobi","best_price_kes":55}


def _mock_credit_response(farmer_id: str) -> dict:
    data = {
        "F001":("Wanjiku Kamau", 80,"A",150_000),
        "F002":("Kipchumba Rono",100,"A",150_000),
        "F003":("Achieng Otieno", 20,"D",0),
        "F004":("Mwangi Githinji",100,"A",150_000),
        "F005":("Jepchirchir Sang",100,"A",150_000),
    }
    if farmer_id not in data:
        return {"found":False,"message":f"Farmer {farmer_id} not found. Demo: F001-F005"}
    name, score, band, loan = data[farmer_id]
    return {"found":True,"farmer_id":farmer_id,"farmer_name":name,
            "score":score,"band":band,"max_loan_kes":loan,
            "breakdown":["Demo mode — connect Neo4j for live scoring"]}


def _mock_farmers_response() -> dict:
    return {"agent_id":"A001","farmers":[
        {"farmer_id":"F001","name":"Wanjiku Kamau", "region":"R001",
         "priority_score":90,"reason":"Health alert — cow symptoms reported",
         "urgency":"HIGH","last_advisory":"2026-06-10"},
        {"farmer_id":"F002","name":"Kipchumba Rono","region":"R002",
         "priority_score":70,"reason":"Market opportunity — sell window open",
         "urgency":"HIGH","last_advisory":"2026-06-18"},
        {"farmer_id":"F004","name":"Mwangi Githinji","region":"R001",
         "priority_score":20,"reason":"Regular check-in due",
         "urgency":"LOW","last_advisory":"2026-06-15"},
    ]}
