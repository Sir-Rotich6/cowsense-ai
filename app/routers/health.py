"""
CowSense AI — Health Triage Router
app/routers/health.py

POST /health-check
Accepts: cow symptoms (free text list)
Returns: GraphRAG disease match + Claude advisory
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agent import run_agent, graphrag_disease_query

router = APIRouter(prefix="/health-check", tags=["Health Triage"])


class HealthRequest(BaseModel):
    farmer_id:     Optional[str]       = Field("F001",    example="F001")
    symptoms:      list[str]           = Field(...,        example=["high fever", "swollen lymph nodes"])
    cow_age_years: Optional[int]       = Field(3,          example=4)
    region:        Optional[str]       = Field("nakuru",   example="nakuru")
    region_id:     Optional[str]       = Field(None,       example="R001")


@router.post("")
async def health_check(req: HealthRequest):
    """
    Feature 1 — Livestock Health Triage

    GraphRAG flow:
      symptoms (free text) → vector embedding → Neo4j semantic search
      → disease match + co-occurring diseases + seasonal risk
      → Claude advisory (grounded in KALRO/ILRI data)

    Disease data: KALRO Dairy Value Chain ToT Manual 2020, Module 2
    """
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="Provide at least one symptom")

    user_msg = (
        f"A farmer in {req.region.title()} reports their cow "
        f"(age {req.cow_age_years} years) has: {', '.join(req.symptoms)}. "
        f"Query the disease graph and give an advisory."
    )
    farmer_ctx = {
        "farmer_id": req.farmer_id,
        "region":    req.region,
        "region_id": req.region_id,
        "cow_age":   req.cow_age_years,
    }

    result = await run_agent(user_msg, "health", farmer_ctx)
    tr = result.get("tool_result") or {}

    # Build co-occurring disease warning if present
    co_warning = ""
    co = tr.get("co_occurring_diseases", [])
    if co:
        names = [d["name"] for d in co]
        co_warning = f"Also check for: {', '.join(names)} (commonly co-occur)"

    return {
        "farmer_id":           req.farmer_id,
        "symptoms_received":   req.symptoms,
        "region":              req.region,
        "search_method":       tr.get("search_method", "mock"),
        "top_diagnosis":       tr.get("top_disease",   "Unknown"),
        "severity":            tr.get("severity",      "UNKNOWN"),
        "vet_required":        tr.get("vet_required",  True),
        "medicine":            tr.get("medicine"),
        "dosage":              tr.get("dosage"),
        "prevention":          tr.get("prevention"),
        "confidence":          tr.get("confidence"),
        "co_occurring_warning":co_warning,
        "seasonal_risk":       tr.get("seasonal_risk_note", ""),
        "feed_risk":           tr.get("feed_risk_warning",  []),
        "ai_advisory":         result["advisory"],
        "urgency_label":       result["urgency_label"],
        "data_source":         tr.get("source", "KALRO Dairy Value Chain ToT Manual 2020"),
        "tool_used":           result["tool_used"],
    }
