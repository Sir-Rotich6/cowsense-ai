"""
CowSense AI — Market Price Router
app/routers/market.py

POST /market-price
Accepts: region name + milk volume in litres
Returns: current KES price + trend + sell recommendation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agent import run_agent

router = APIRouter(prefix="/market-price", tags=["Market Price"])

VALID_REGIONS = [
    "nakuru", "eldoret", "nairobi", "kisii",
    "meru", "embu", "kericho", "bomet"
]


class MarketRequest(BaseModel):
    farmer_id:      Optional[str]   = Field("F001",   example="F001")
    region:         str             = Field(...,       example="eldoret")
    milk_volume_l:  Optional[float] = Field(10.0,     example=30.0)


@router.post("")
async def market_price(req: MarketRequest):
    """
    Feature 2 — Market Price Intelligence

    Flow: region → Neo4j price graph → Claude sell recommendation
    Covers 8 Kenyan dairy regions with live KES/litre prices and trend.
    """
    if req.region.lower() not in VALID_REGIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Region '{req.region}' not found. "
                   f"Available: {', '.join(VALID_REGIONS)}"
        )

    user_msg = (
        f"Farmer in {req.region.title()} wants to sell "
        f"{req.milk_volume_l} litres of milk. "
        f"Get the current price for {req.region} and give a sell recommendation."
    )
    farmer_ctx = {
        "farmer_id": req.farmer_id,
        "region":    req.region,
        "volume_l":  req.milk_volume_l,
    }

    result = await run_agent(user_msg, "market", farmer_ctx)
    tr = result.get("tool_result") or {}

    # Price comparison context
    best_r = tr.get("best_region")
    best_p = tr.get("best_price_kes")
    curr_p = tr.get("price_kes")
    gap    = round(best_p - curr_p, 2) if (best_p and curr_p and best_r != req.region.title()) else 0

    return {
        "farmer_id":            req.farmer_id,
        "region":               req.region.title(),
        "price_kes_per_litre":  curr_p,
        "trend":                tr.get("trend"),
        "buyer":                tr.get("buyer"),
        "market_note":          tr.get("note"),
        "milk_volume_l":        req.milk_volume_l,
        "estimated_revenue_kes":tr.get("estimated_revenue_kes"),
        "best_price_region":    {
            "region":    best_r,
            "price_kes": best_p,
            "gap_kes":   gap,
        },
        "ai_advisory":    result["advisory"],
        "urgency_label":  result["urgency_label"],
        "tool_used":      result["tool_used"],
    }
