"""
CowSense AI — FastAPI Application
app/main.py

Kenya AI Challenge 2026 · Mercy Corps AgriFin Track · DigiCow Africa Brief
Team: Enock Rotich · Larry Baraza · Karol Howard · Sandra Kimiring

Endpoints:
  GET  /                     → status + mode
  GET  /demo-farmer          → pre-seeded demo farmers
  POST /health-check         → livestock health triage (GraphRAG)
  POST /market-price         → milk price + sell advisory
  POST /credit-profile       → AgriFin credit score
  GET  /prioritize-farmers   → ranked farmer list for agent
  POST /ussd                 → Africa's Talking USSD callback
"""

from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from typing import Optional

from app.config import get_settings
from app.agent import get_prioritized_farmers
from app.routers import health, market, credit

settings = get_settings()

# ── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="CowSense AI",
    description=(
        "AI-Powered Farmer Intelligence for Kenya's Youth Extension Agents\n"
        "Kenya AI Challenge 2026 · Mercy Corps AgriFin Track · DigiCow Africa"
    ),
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

# ── Wire routers ───────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(market.router)
app.include_router(credit.router)


# ── Root ───────────────────────────────────────────────────────────
@app.get("/", tags=["Status"])
def root():
    return {
        "service":    "CowSense AI",
        "version":    "1.0.0",
        "status":     "live",
        "mode":       "demo" if settings.is_demo_mode else "production",
        "neo4j":      "connected" if settings.has_neo4j else "localhost",
        "hackathon":  "Kenya AI Challenge 2026",
        "endpoints":  [
            "POST /health-check",
            "POST /market-price",
            "POST /credit-profile",
            "GET  /prioritize-farmers",
            "POST /ussd",
            "GET  /demo-farmer",
            "GET  /docs",
        ],
    }


# ── Demo farmers ───────────────────────────────────────────────────
@app.get("/demo-farmer", tags=["Demo"])
def get_demo_farmers():
    """5 pre-seeded farmers for testing all 3 features."""
    return {
        "farmers": {
            "F001": {
                "name": "Wanjiku Kamau", "region": "Nakuru", "cows": 3,
                "milk_l": 18, "mpesa": True, "months": 8,
                "demo_scenario": "Health → symptoms: 'high fever, swollen lymph nodes' → ECF",
            },
            "F002": {
                "name": "Kipchumba Rono", "region": "Eldoret", "cows": 5,
                "milk_l": 30, "mpesa": True, "months": 14,
                "demo_scenario": "Credit → F002 → Band A, KES 150,000 eligible",
            },
            "F003": {
                "name": "Achieng Otieno", "region": "Kisii", "cows": 2,
                "milk_l": 10, "mpesa": False, "months": 3,
                "demo_scenario": "Credit → F003 → Band D, needs more history",
            },
            "F004": {
                "name": "Mwangi Githinji", "region": "Nakuru", "cows": 4,
                "milk_l": 22, "mpesa": True, "months": 11,
                "demo_scenario": "Market → region: nakuru, volume: 22 → KES 52/L rising",
            },
            "F005": {
                "name": "Jepchirchir Sang", "region": "Eldoret", "cows": 6,
                "milk_l": 35, "mpesa": True, "months": 18,
                "demo_scenario": "Market → region: eldoret, volume: 35 → KES 46/L stable",
            },
        },
        "tip": "Use these IDs in /health-check, /market-price, /credit-profile",
    }


# ── Prioritize farmers ─────────────────────────────────────────────
@app.get("/prioritize-farmers", tags=["Agent Tools"])
@app.post("/prioritize-farmers", tags=["Agent Tools"])
async def prioritize_farmers(agent_id: Optional[str] = "A001"):
    """
    Returns ranked list of farmers for an extension agent.
    Ranked by: health risk > market opportunity > AgriFin readiness.
    """
    result = get_prioritized_farmers(agent_id)
    return {
        "agent_id":        agent_id,
        "total_farmers":   len(result.get("farmers", [])),
        "prioritized_list":result.get("farmers", []),
        "ranking_criteria":[
            "1. Health risk (cow symptoms reported)",
            "2. Market opportunity (sell window open)",
            "3. AgriFin readiness (credit profile ready)",
            "4. Platform engagement (months + training)",
        ],
    }


# ── USSD Handler (Africa's Talking) ───────────────────────────────
@app.post("/ussd", tags=["USSD"])
async def ussd_callback(
    request: Request,
    sessionId:   str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text:        str = Form(default=""),
):
    """
    Africa's Talking USSD callback.
    Dial *384# to access CowSense AI from any phone.

    Flow:
      Level 0: Main menu
      Level 1: Feature selection (Health / Price / Credit)
      Level 2: User input
      Level 3: AI result via SMS
    """
    parts = [p.strip() for p in text.split("*")] if text else []
    level = len(parts)

    # ── Level 0: Main menu ─────────────────────────────────────────
    if level == 0 or text == "":
        return PlainTextResponse(
            "CON Welcome to CowSense AI 🐄\n"
            "Powered by DigiCow Africa\n\n"
            "1. Check cow health\n"
            "2. Check milk price\n"
            "3. My credit score"
        )

    choice = parts[0]

    # ── Level 1: Sub-menus ─────────────────────────────────────────
    if level == 1:
        if choice == "1":
            return PlainTextResponse(
                "CON Describe the main symptom:\n"
                "Examples:\n"
                "- high fever\n"
                "- swollen lymph nodes\n"
                "- swollen udder\n"
                "- bloated left side\n\n"
                "Type your symptom:"
            )
        elif choice == "2":
            return PlainTextResponse(
                "CON Enter your region:\n"
                "1. Nakuru\n"
                "2. Eldoret\n"
                "3. Kisii\n"
                "4. Nairobi\n"
                "5. Meru\n"
                "6. Embu"
            )
        elif choice == "3":
            return PlainTextResponse(
                "CON Enter your Farmer ID:\n"
                "(from your DigiCow profile)\n\n"
                "Example: F001"
            )
        else:
            return PlainTextResponse("END Invalid choice. Dial *384# again.")

    # ── Level 2: Process input ─────────────────────────────────────
    if level == 2:
        user_input = parts[1].strip()

        if choice == "1":
            # Health check — call agent directly
            from app.agent import graphrag_disease_query, _urgency_label
            result = graphrag_disease_query([user_input])

            if result.get("matched"):
                disease  = result["top_disease"]
                severity = result["severity"]
                medicine = result["medicine"]
                dosage   = result["dosage"]
                urgency  = _urgency_label(result)
                vet      = "Call vet NOW" if result["vet_required"] else "Treat at home"

                msg = (
                    f"END {urgency}\n\n"
                    f"Diagnosis: {disease}\n"
                    f"Severity: {severity}\n"
                    f"Medicine: {medicine}\n"
                    f"Dosage: {dosage}\n"
                    f"Action: {vet}"
                )
            else:
                msg = (
                    "END Symptom not clearly matched.\n"
                    "Please consult a vet directly.\n"
                    "Call DVS: 0800 723 111 (free)"
                )
            return PlainTextResponse(msg)

        elif choice == "2":
            # Market price
            region_map = {
                "1": "nakuru", "2": "eldoret", "3": "kisii",
                "4": "nairobi","5": "meru",    "6": "embu",
            }
            region = region_map.get(user_input, user_input.lower())
            from app.agent import get_market_price
            result = get_market_price(region)

            if result.get("found"):
                price  = result["price_kes"]
                trend  = result["trend"]
                buyer  = result.get("buyer", "Local cooperative")
                rev    = result.get("estimated_revenue_kes", "—")
                action = "SELL NOW" if trend == "RISING" else \
                         "CONSIDER HOLDING" if trend == "FALLING" else "SELL AS NORMAL"
                msg = (
                    f"END {region.title()} Milk Price\n\n"
                    f"Price: KES {price}/L\n"
                    f"Trend: {trend}\n"
                    f"Buyer: {buyer}\n"
                    f"Action: {action}"
                )
            else:
                msg = "END Region not found. Try: nakuru, eldoret, kisii, nairobi"

            return PlainTextResponse(msg)

        elif choice == "3":
            # Credit profile
            from app.agent import calculate_credit_score
            result = calculate_credit_score(user_input.upper())

            if result.get("found"):
                score = result["score"]
                band  = result["band"]
                loan  = result["max_loan_kes"]
                labels = {"A":"EXCELLENT","B":"GOOD","C":"FAIR","D":"NOT ELIGIBLE"}
                label = labels.get(band, "")
                msg = (
                    f"END Credit Profile\n\n"
                    f"Farmer: {result['farmer_name']}\n"
                    f"Score: {score}/100\n"
                    f"Band: {band} ({label})\n"
                    f"Max loan: KES {loan:,}\n\n"
                    f"Visit DigiCow app for details."
                )
            else:
                msg = "END Farmer ID not found.\nCheck your DigiCow profile for your ID."

            return PlainTextResponse(msg)

    return PlainTextResponse("END Session ended. Dial *384# to start again.")
