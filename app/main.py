"""
CowSense AI — FastAPI Backend
app/main.py

Kenya AI Challenge 2026 | Mercy Corps AgriFin Track | DigiCow Africa Brief
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from app.agent import run_agent, get_prioritized_farmers, _mock_farmers_response
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="CowSense AI",
    description="AI-Powered Farmer Intelligence for Kenya's Youth Extension Agents — Kenya AI Challenge 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ─────────────────────────────────────────────────────────────

class HealthCheckRequest(BaseModel):
    farmer_id: Optional[str] = Field("F001", example="F001")
    symptoms: list[str] = Field(..., example=["high fever", "swollen lymph nodes"])
    cow_age_years: Optional[int] = Field(3, example=3)
    region: Optional[str] = Field("nakuru", example="nakuru")

class MarketPriceRequest(BaseModel):
    farmer_id: Optional[str] = Field("F001", example="F001")
    region: str = Field(..., example="nakuru")
    milk_volume_l: Optional[float] = Field(10.0, example=18.0)

class CreditRequest(BaseModel):
    farmer_id: str = Field(..., example="F002")

class PrioritizeRequest(BaseModel):
    agent_id: Optional[str] = Field("A001", example="A001")

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Status"])
def root():
    return {
        "service": "CowSense AI",
        "version": "1.0.0",
        "status": "live",
        "mode": "demo" if settings.is_demo_mode else "production",
        "hackathon": "Kenya AI Challenge 2026",
        "endpoints": ["/health-check", "/market-price", "/credit-profile", "/prioritize-farmers", "/demo-farmer"],
    }

@app.get("/demo-farmer", tags=["Demo"])
def get_demo_farmers():
    """Returns the 5 pre-seeded demo farmers for testing."""
    return {
        "farmers": {
            "F001": {"name": "Wanjiku Kamau",  "region": "Nakuru",      "cows": 3, "milk_l": 18, "scenario": "Health — high fever + swollen lymph nodes → ECF"},
            "F002": {"name": "Kipchumba Rono", "region": "Uasin Gishu", "cows": 5, "milk_l": 30, "scenario": "Credit — Band A, KES 150,000 eligible"},
            "F003": {"name": "Achieng Otieno", "region": "Kisii",       "cows": 2, "milk_l": 10, "scenario": "Credit — Band D, needs more platform history"},
            "F004": {"name": "Mwangi Githinji","region": "Nakuru",      "cows": 4, "milk_l": 22, "scenario": "Routine check-in"},
            "F005": {"name": "Jepchirchir Sang","region":"Uasin Gishu", "cows": 6, "milk_l": 35, "scenario": "Market — 30L, Eldoret at KES 46/L"},
        }
    }

@app.post("/health-check", tags=["Features"])
async def health_check(req: HealthCheckRequest):
    """
    Feature 1: Livestock Health Triage
    Input: cow symptoms → Neo4j disease graph → Claude advisory
    Disease data source: KALRO Dairy Value Chain ToT Manual 2020, Module 2
    """
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="Provide at least one symptom")

    user_msg = (
        f"A farmer in {req.region.title()} has a cow (age {req.cow_age_years} years) "
        f"showing these symptoms: {', '.join(req.symptoms)}. "
        f"Query the disease graph and provide an advisory."
    )
    farmer_ctx = {"farmer_id": req.farmer_id, "region": req.region, "cow_age": req.cow_age_years}

    result = await run_agent(user_msg, "health", farmer_ctx)
    return {
        "farmer_id": req.farmer_id,
        "symptoms_received": req.symptoms,
        "region": req.region,
        "top_diagnosis": result["tool_result"].get("top_disease") if result["tool_result"] else "Unknown",
        "severity": result["tool_result"].get("severity") if result["tool_result"] else "UNKNOWN",
        "vet_required": result["tool_result"].get("vet_required") if result["tool_result"] else True,
        "medicine": result["tool_result"].get("medicine") if result["tool_result"] else None,
        "dosage": result["tool_result"].get("dosage") if result["tool_result"] else None,
        "prevention": result["tool_result"].get("prevention") if result["tool_result"] else None,
        "ai_advisory": result["advisory"],
        "urgency_label": result["urgency_label"],
        "data_source": "KALRO Dairy Value Chain ToT Manual 2020, Module 2",
        "tool_used": result["tool_used"],
    }

@app.post("/market-price", tags=["Features"])
async def market_price(req: MarketPriceRequest):
    """
    Feature 2: Market Price Intelligence
    Input: region + volume → Neo4j price graph → Claude sell recommendation
    """
    user_msg = (
        f"Farmer in {req.region.title()} wants to sell {req.milk_volume_l} litres of milk. "
        f"Get the current price for {req.region} and give a sell recommendation."
    )
    farmer_ctx = {"farmer_id": req.farmer_id, "region": req.region, "volume_l": req.milk_volume_l}

    result = await run_agent(user_msg, "market", farmer_ctx)
    tr = result["tool_result"] or {}
    return {
        "farmer_id": req.farmer_id,
        "region": req.region.title(),
        "price_kes_per_litre": tr.get("price_kes"),
        "trend": tr.get("trend"),
        "buyer": tr.get("buyer"),
        "market_note": tr.get("note"),
        "milk_volume_l": req.milk_volume_l,
        "estimated_revenue_kes": tr.get("estimated_revenue_kes"),
        "best_price_region": {"region": tr.get("best_region"), "price_kes": tr.get("best_price_kes")},
        "ai_advisory": result["advisory"],
        "urgency_label": result["urgency_label"],
        "tool_used": result["tool_used"],
    }

@app.post("/credit-profile", tags=["Features"])
async def credit_profile(req: CreditRequest):
    """
    Feature 3: AgriFin Credit Profile
    Input: farmer ID → scoring from DigiCow platform activity → Claude explanation
    """
    user_msg = (
        f"Generate an AgriFin credit profile for farmer ID {req.farmer_id} "
        f"based on their DigiCow platform activity."
    )
    result = await run_agent(user_msg, "credit", {"farmer_id": req.farmer_id})
    tr = result["tool_result"] or {}
    band_labels = {"A": "⭐ Excellent — top loan tier", "B": "✅ Good — standard loan eligible",
                   "C": "⚠️ Fair — micro-loan only",    "D": "🔴 Not yet eligible — build history"}
    return {
        "farmer_id": req.farmer_id,
        "farmer_name": tr.get("farmer_name"),
        "credit_score": tr.get("score"),
        "credit_band": tr.get("band"),
        "band_label": band_labels.get(tr.get("band", ""), ""),
        "max_loan_kes": tr.get("max_loan_kes"),
        "score_breakdown": tr.get("breakdown", []),
        "ai_advisory": result["advisory"],
        "urgency_label": result["urgency_label"],
        "tool_used": result["tool_used"],
    }

@app.get("/prioritize-farmers", tags=["Features"])
@app.post("/prioritize-farmers", tags=["Features"])
async def prioritize_farmers(req: Optional[PrioritizeRequest] = None):
    """
    Feature 4: Farmer Prioritization
    Returns ranked list of farmers for an extension agent by urgency.
    """
    agent_id = req.agent_id if req else "A001"
    result = get_prioritized_farmers(agent_id)
    return {
        "agent_id": agent_id,
        "total_farmers": len(result.get("farmers", [])),
        "prioritized_list": result.get("farmers", []),
        "ranking_criteria": ["Health risk", "Market opportunity", "AgriFin readiness", "Platform engagement"],
    }
