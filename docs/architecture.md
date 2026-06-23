# CowSense AI — System Architecture

## Overview

CowSense AI is built around a **GraphRAG pattern**: Claude's `tool_use` queries a Neo4j knowledge graph containing KALRO/ILRI-verified livestock data, then generates grounded advisory text. No hallucinated medicines. No invented prices.

---

## Full Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     EXTENSION AGENT (PRIMARY USER)                   │
│                                                                      │
│   Lovable Web Dashboard          Africa's Talking USSD/SMS           │
│   ┌─────────────────────┐        ┌──────────────────────────┐        │
│   │ Prioritized farmer  │        │  *384#                   │        │
│   │ list (real-time AI) │        │  → 1. Check cow health   │        │
│   │ Per-farmer advisory │        │  → 2. Check milk price   │        │
│   │ Outcome logging     │        │  → 3. My credit score    │        │
│   └──────────┬──────────┘        └────────────┬─────────────┘        │
│              │ HTTPS                          │ USSD/SMS callback     │
└──────────────┼────────────────────────────────┼─────────────────────-┘
               │                                │
               ▼                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Render.com)                      │
│                                                                      │
│   POST /health-check           POST /market-price                    │
│   POST /credit-profile         GET  /prioritize-farmers              │
│   POST /ussd-callback          GET  /demo-farmer                     │
│                                                                      │
│   app/main.py ──► app/agent.py ──► tool dispatcher                  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   CLAUDE API (tool_use) — TURN 1                     │
│                                                                      │
│   System prompt (feature-specific, from prompts/ directory)         │
│   + User message + farmer context                                    │
│                                                                      │
│   Claude decides which tool to call:                                 │
│   ┌────────────────────┬──────────────────┬────────────────────┐     │
│   │query_disease_graph │ get_market_price  │calculate_credit_   │     │
│   │(symptoms: list)    │ (region, volume)  │score(farmer_id)    │     │
│   └─────────┬──────────┴────────┬──────────┴──────────┬─────────┘     │
│             │                   │                      │               │
└─────────────┼───────────────────┼──────────────────────┼──────────────┘
              │ tool call         │                      │
              ▼                   ▼                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         NEO4J AURA                                   │
│                  (KALRO/ILRI-grounded knowledge graph)               │
│                                                                      │
│  (:Symptom)-[:INDICATES {weight}]->(:Disease)                        │
│  (:Region)-[:HAS_PRICE]->(:MilkPrice)                                │
│  (:Farmer)-[:FARMS_IN]->(:Region)                                    │
│  (:ExtensionAgent)-[:MANAGES]->(:Farmer)                             │
│  (:ExtensionAgent)-[:SERVES]->(:Region)                              │
│  (:Region)-[:HAS_CLIMATE]->(:ClimateAdvisory)                        │
│                                                                      │
│  Nodes: Disease(10) · Symptom(28) · Region(8) · MilkPrice(8)        │
│         Farmer(5) · ExtensionAgent(2) · ClimateAdvisory(2)           │
│                                                                      │
│  Source: KALRO Dairy Value Chain ToT Manual 2020, Module 2           │
│          ILRI Smallholder Dairy Manual 2nd Ed 2019                   │
│          Kenya CSA Strategy 2017–2026 (region AEZ data)              │
│          KMD Agrometeorology / KAOP (climate nodes)                  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ tool result (JSON)
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   CLAUDE API (tool_use) — TURN 2                     │
│                                                                      │
│   Receives tool result → generates grounded advisory text            │
│   Using prompts from: prompts/health_system.txt                      │
│                        prompts/market_system.txt                     │
│                        prompts/credit_system.txt                     │
│                                                                      │
│   Key guarantee: medicine/dosage ALWAYS from graph, not invented     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ + Featherless fallback
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 FEATHERLESS (Llama 3.1 8B)                           │
│                                                                      │
│   Used for: lightweight symptom pre-classification                   │
│             price trend detection                                    │
│             fallback when Claude quota exceeded                      │
│                                                                      │
│   Not used for: final advisory generation (Claude only)              │
└──────────────────────────────────────────────────────────────────────┘
               │ structured JSON response
               ▼
     Returns to FastAPI → Lovable UI / SMS

```

---

## Neo4j Knowledge Graph Schema

```
(:ExtensionAgent)
      │
      ├─[:MANAGES]──► (:Farmer)
      │                    │
      │                    ├─[:FARMS_IN]──► (:Region)
      │                                          │
      │                                          ├─[:HAS_PRICE]──► (:MilkPrice)
      │                                          └─[:HAS_CLIMATE]─► (:ClimateAdvisory)
      │
      └─[:SERVES]───► (:Region)

(:Symptom)─[:INDICATES {weight: 0.0–1.0}]──► (:Disease)

```

### Node properties at a glance

| Node | Key properties |
|---|---|
| `Disease` | id, name, category, causative_agent, severity, vet_required, medicine, dosage, prevention, source |
| `Symptom` | id, name, category |
| `Farmer` | id, name, cows, breed, milk_daily_l, mpesa_active, months_on_platform, priority_flag |
| `Region` | id, name, county, aez, kcsap_target |
| `MilkPrice` | region_id, price_kes, trend, note, buyer |
| `ClimateAdvisory` | region_id, period, rainfall_forecast, livestock_advisory, source |
| `ExtensionAgent` | id, name, region_id, farmers_assigned, months_active |

---

## Request → Response Flow (Health Check Example)

```
1. Agent enters: "high fever, swollen lymph nodes"

2. FastAPI POST /health-check →
   run_agent("cow showing high fever, swollen lymph nodes", "health")

3. Claude API Turn 1:
   → stop_reason: "tool_use"
   → tool_use: query_disease_graph(symptoms=["high fever","swollen lymph nodes"])

4. Neo4j Cypher:
   MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
   WHERE toLower(s.name) IN ["high fever","swollen lymph nodes"]
   RETURN d.name, d.severity, d.medicine, d.dosage, SUM(r.weight) AS score
   ORDER BY score DESC LIMIT 3
   → Result: East Coast Fever, score=1.80, HIGH, vet_required=true,
             medicine="Buparvaquone (Butalex®)", dosage="2.5mg/kg IM"

5. Claude API Turn 2:
   → Receives tool result
   → Generates 3-sentence advisory using prompts/health_system.txt
   → NEVER invents medicine — uses only what came from graph

6. Response JSON:
   {
     "top_diagnosis": "East Coast Fever (ECF)",
     "severity": "HIGH",
     "vet_required": true,
     "medicine": "Buparvaquone (Butalex®)",
     "dosage": "2.5 mg/kg body weight — single intramuscular injection",
     "ai_advisory": "Your cow most likely has East Coast Fever...",
     "urgency_label": "🚨 URGENT — Call vet now",
     "data_source": "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
   }

7. Lovable renders → Agent reads advisory to farmer on-farm
```

---

## Tech Stack Decision Log

| Decision | Choice | Reason |
|---|---|---|
| Agent orchestration | Claude `tool_use` (not Masumi) | Native to Claude SDK; simpler; no extra dependency |
| LLM inference | Featherless (Llama 3.1 8B) | Free tier; open-source; fallback role only |
| Knowledge graph | Neo4j Aura | Free tier sufficient; relationships + weights = explainable advisory |
| Backend | FastAPI | Fast, async, auto-docs, team knows Python |
| Frontend | Lovable | Rapid build; exports clean React; demo URL in minutes |
| SMS/USSD | Africa's Talking | Kenya-native; free sandbox; works on feature phones |
| Hosting | Render | Free tier; deploy from GitHub in 5 min; HTTPS auto |

---

*Architecture document — CowSense AI · Kenya AI Challenge 2026*
