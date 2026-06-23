# CowSense AI 🐄
**AI-Powered Farmer Intelligence for Kenya's Youth Extension Agents**

> Kenya AI Challenge 2026 · Mercy Corps AgriFin Track · DigiCow Africa Brief

---

## What We're Building

CowSense AI gives youth extension agents three AI tools they can use during a farm visit:

| Feature | What the agent inputs | What they get back |
|---|---|---|
| **Livestock Health Triage** | Cow symptoms (free text) | Diagnosis · treatment · urgency (sourced from KALRO/ILRI disease data) |
| **Market Price Intelligence** | Region + milk volume | Live KES/litre price · trend · sell recommendation |
| **AgriFin Credit Profile** | Farmer ID | Credit score · band (A–D) · max loan eligibility in KES |

The agent opens CowSense AI and sees a **prioritized list of farmers** who need attention today — ranked by AI across health risk, market opportunity, and AgriFin readiness.

---

## Why This Matters — Research Grounding

All data and domain logic in this repo is sourced directly from named research documents. Zero guesswork.

| Claim | Source |
|---|---|
| Dairy = **3.5% of Kenya GDP**; smallholders produce **80%+** of milk | KALRO Dairy Value Chain ToT Manual (March 2020) |
| **1.8M smallholder dairy households**; national herd 3.3M heads | KALRO Dairy Value Chain ToT Manual (March 2020) |
| **84% of milk sold raw** with minimal processing | KALRO Dairy Value Chain ToT Manual (March 2020) |
| Disease graph: ECF, FMD, Mastitis, LSD, Brucellosis, Bloat, Parasites, Pink Eye | KALRO Module 2: Dairy Animal Health; KALRO TIMPS 31 |
| Feed and fodder advisory content | ILRI Smallholder Dairy Farmer Training Manual, 2nd Ed (2019); KALRO Pasture & Fodder ToT Manual (2020) |
| Climate data layer: 10-day dekadal bulletins, seasonal forecasts | Kenya Meteorological Department — Agrometeorology Services |
| Ward-level climate-agronomic advisory (KAOP) | KMD Seasonal Forecast Products |
| AI advisory + last-mile worker coordination model validated | J-PAL / MIT — LLM-Powered Digital Advisory Services for Agripreneurs (Kenya, Feb 2026–Jan 2027) |
| SMS/USSD + AI hotline: 500,000+ farmers, 70% income increase | GSMA — Crop2Cash Case Study (Nov 2022–Jul 2024, Nigeria — analogous precedent) |
| DigiCow co-founder Peninah Wanja: 15 years as extension agent | AYuTe Africa Champions 2023 — DigiCow Africa profile |
| Kenya CSA triple-win: productivity + resilience + reduced GHG | Kenya Climate Smart Agriculture Strategy 2017–2026 |
| 98% of Kenyan agriculture is rain-fed | Kenya Climate Smart Agriculture Strategy 2017–2026 |

---

## Tech Stack

| Layer | Tool | Role |
|---|---|---|
| **AI Orchestration** | Claude API (`claude-sonnet-4-6`) with `tool_use` | Replaces Masumi. Claude natively calls Neo4j + price + credit tools, generates grounded advisory |
| **Open LLM** | Featherless (Llama 3.1 8B) | Fast symptom pre-classification; fallback if Claude quota is exceeded |
| **Knowledge Graph** | Neo4j Aura (free tier) | Disease graph · price nodes · farmer profiles · relationships with weights |
| **Backend** | FastAPI (Python 3.11) | 4 REST endpoints + Claude tool_use handler + USSD route |
| **Frontend** | Lovable | Agent dashboard: prioritized farmer list + advisory panel (mobile-first) |
| **SMS / USSD** | Africa's Talking | `*384#` → symptom input → SMS advisory. Works on feature phones |
| **Hosting** | Render (free tier) | FastAPI deployed at `https://cowsense-api.onrender.com` |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/[your-org]/cowsense-ai.git
cd cowsense-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your API keys (see .env.example for all required keys)

# 4. Seed Neo4j (requires Neo4j Aura free instance)
# Open Neo4j Browser → paste contents of neo4j/seed.cypher

# 5. Run locally
uvicorn app.main:app --reload --port 8000

# 6. Test all endpoints
python tests/demo_test.py

# 7. View API docs
open http://localhost:8000/docs
```

### Environment check
```bash
python scripts/check_env.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/health-check` | Livestock symptom → AI diagnosis + treatment |
| `POST` | `/market-price` | Region + volume → price + sell recommendation |
| `POST` | `/credit-profile` | Farmer ID → credit score + loan eligibility |
| `GET` | `/prioritize-farmers` | Agent ID → ranked farmer list |
| `GET` | `/demo-farmer` | Pre-seeded demo farmer data |
| `GET` | `/` | Health check + version |

Full API docs: `http://localhost:8000/docs` (Swagger UI)

---

## Demo Scenarios (June 28 Judging)

| # | Farmer | Input | Expected output |
|---|---|---|---|
| 1 | Wanjiku Kamau · Nakuru | `"high fever, swollen lymph nodes"` | East Coast Fever · HIGH · Buparvaquone 2.5mg/kg IM |
| 2 | Kipchumba Rono · Eldoret · 30L | Region: `"eldoret"`, volume: `30` | KES 46/L · stable · consider Nakuru at KES 52 |
| 3 | Kipchumba Rono · F002 | `farmer_id: "F002"` | Score 100 · Band A · KES 150,000 max loan |

---

## Team

| Name | Role | Responsibility |
|---|---|---|
| **Enock Rotich** | Team Lead / AI Engineer | Claude tool_use agent · Neo4j schema · Pitch |
| **Larry Baraza** | Backend Developer | FastAPI · Neo4j · Africa's Talking · Render |
| **Karol Howard** | Frontend / UX | Lovable dashboard · Demo flow · Slides |
| **Sandra Kimiring** | AI Eng / Prompts | Featherless · Prompt engineering · AI QA |

---

## Project Structure

```
cowsense-ai/
├── app/
│   ├── main.py          # FastAPI app + all endpoints
│   ├── agent.py         # Claude tool_use agent loop
│   ├── config.py        # Settings and env management
│   └── routers/         # Feature-specific route handlers
│       ├── health.py
│       ├── market.py
│       └── credit.py
├── neo4j/
│   ├── seed.cypher      # Full knowledge graph seed (KALRO-grounded)
│   └── schema.cypher    # Constraints and indexes
├── prompts/             # System prompts for all 3 features (Sandra owns)
├── tests/
│   ├── demo_test.py     # Runs all 3 demo scenarios
│   └── demo_inputs.json # All scripted test inputs
├── docs/
│   ├── architecture.md  # System architecture diagram
│   └── research_sources.md
├── scripts/
│   ├── setup.sh         # One-command setup
│   └── check_env.py     # API key verification
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Research Sources

See [`docs/research_sources.md`](docs/research_sources.md) for the full mapping of all 11 source documents to their usage in this codebase.

---

*Built at Kenya AI Challenge 2026 · June 27–28, Nairobi*
