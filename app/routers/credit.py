"""
CowSense AI — AgriFin Credit Profile Router
app/routers/credit.py

POST /credit-profile
Accepts: farmer_id
Returns: credit score 0-100, band A-D, max loan KES, Claude explanation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agent import run_agent

router = APIRouter(prefix="/credit-profile", tags=["AgriFin Credit"])

BAND_LABELS = {
    "A": "⭐ Excellent — eligible for up to KES 150,000",
    "B": "✅ Good — eligible for up to KES 80,000",
    "C": "⚠️ Fair — micro-loan up to KES 30,000 only",
    "D": "🔴 Not yet eligible — build 3 more months of history",
}

BAND_NEXT_STEP = {
    "A": "Refer to partner MFI or SACCO today. Documents: National ID + DigiCow profile.",
    "B": "Eligible for standard loan product. Connect to local SACCO or M-Shwari Biashara.",
    "C": "Eligible for micro-loan only. Recommend: complete 3 more training modules + enable M-Pesa.",
    "D": "Not yet eligible. Action plan: stay active on DigiCow, enable M-Pesa, complete training.",
}


class CreditRequest(BaseModel):
    farmer_id: str = Field(..., example="F002")


@router.post("")
async def credit_profile(req: CreditRequest):
    """
    Feature 3 — AgriFin Credit Profile

    Scores farmer's DigiCow platform activity across 4 factors:
      +30  M-Pesa active account
      +25  6+ months on DigiCow platform
      +25  15+ litres/day milk production
      +20  3+ cattle assets on record

    Returns credit band A-D and max loan eligibility in KES.
    Data grounded in DigiCow Africa Ndume platform field structure.
    """
    if not req.farmer_id:
        raise HTTPException(status_code=400, detail="Provide a farmer_id")

    user_msg = (
        f"Generate an AgriFin credit profile for farmer ID {req.farmer_id} "
        f"based on their DigiCow platform activity. "
        f"Explain the result in plain English."
    )
    result = await run_agent(user_msg, "credit", {"farmer_id": req.farmer_id})
    tr = result.get("tool_result") or {}

    if not tr.get("found", True):
        raise HTTPException(
            status_code=404,
            detail=tr.get("message", f"Farmer {req.farmer_id} not found. Demo IDs: F001-F005")
        )

    band = tr.get("band", "D")

    return {
        "farmer_id":       req.farmer_id,
        "farmer_name":     tr.get("farmer_name"),
        "credit_score":    tr.get("score"),
        "credit_band":     band,
        "band_label":      BAND_LABELS.get(band, ""),
        "max_loan_kes":    tr.get("max_loan_kes"),
        "score_breakdown": tr.get("breakdown", []),
        "next_step":       BAND_NEXT_STEP.get(band, ""),
        "ai_advisory":     result["advisory"],
        "urgency_label":   result["urgency_label"],
        "tool_used":       result["tool_used"],
        "data_source":     "DigiCow Africa Ndume platform activity (AYuTe 2023 profile)",
    }
