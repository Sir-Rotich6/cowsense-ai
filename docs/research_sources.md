# CowSense AI — Research Sources
> Every fact, data point, and domain decision in this codebase is traced to a named source document. No guesswork.

---

## Document Index

| # | Document | Type | Pages | Used In |
|---|---|---|---|---|
| 1 | KALRO Dairy Value Chain ToT Manual (March 2020) | Technical manual | 109 | Disease graph, farmer context, GDP stats |
| 2 | KALRO TIMPS 31 — Technologies, Innovations and Management Practices | Web reference | 27 | Breed data, management practices |
| 3 | ILRI Smallholder Dairy Farmer Training Manual, 2nd Edition (2019) | Training manual | 119 | Disease treatment backup, feed advisory |
| 4 | KALRO Pasture and Fodder ToT Manual (2020) | Technical manual | 100 | Fodder data, climate-smart pasture advisory |
| 5 | KALRO Pasture Production and Conservation (Module 19) | Reference module | 42 | Pasture/fodder node data |
| 6 | AYuTe Africa Champions 2023 — DigiCow Africa Profile | Case study | 8 | DigiCow context, farmer profile structure |
| 7 | J-PAL / MIT — LLM-Powered Digital Advisory Services for Agripreneurs and Smallholders | Research paper | 3 | Validation of extension agent + LLM model |
| 8 | GSMA — Crop2Cash Case Study (2025) | Case study | 9 | Analogous precedent for AI + SMS advisory |
| 9 | Kenya Climate Smart Agriculture Strategy 2017–2026 | Government strategy | 53 | Region selection, AEZ classification, stats |
| 10 | KMD — Agrometeorology Services | Government web ref | 8 | Climate data structure, dekadal bulletins |
| 11 | KMD — Seasonal Forecast Products | Government web ref | 4 | Seasonal forecast data node structure |

---

## Document-to-Code Mapping

### 1. KALRO Dairy Value Chain ToT Manual (March 2020)
**Location in codebase:** `neo4j/seed.cypher` (all disease nodes + symptoms + relationships)

**Specific content used:**

| Data point | Code location | Raw source reference |
|---|---|---|
| GDP contribution: **3.5%** (not 4%) | `README.md` stats table | KALRO TIMPS 31 intro, p.1 |
| National dairy herd: **3.3 million heads** | `README.md` | KALRO TIMPS 31, p.1 |
| Smallholder dairy: **80%+ of national milk** | `README.md`, `seed.cypher` comments | KALRO Dairy Value Chain, p.1 |
| **84% of milk sold raw** | `README.md` | KALRO Dairy Value Chain, production stats |
| Disease: ECF — causative agent, Buparvaquone 2.5mg/kg | `seed.cypher` D001 | Module 2: Dairy Animal Health |
| Disease: Anaplasmosis — Oxytetracycline 20mg/kg | `seed.cypher` D002 | Module 2 |
| Disease: Babesiosis — Imidocarb, red urine sign | `seed.cypher` D003 | Module 2 |
| Disease: FMD — supportive care, isolate, notify DVS | `seed.cypher` D004 | Module 2 |
| Disease: LSD — supportive, Oxytetracycline secondary | `seed.cypher` D005 | Module 2 |
| Disease: Mastitis — Amoxicillin/Cloxacillin intramammary | `seed.cypher` D006 | Module 2, Section 2.6.6 |
| Disease: Brucellosis — notifiable, test-and-slaughter | `seed.cypher` D007 | Module 2 |
| Disease: Internal Parasites — Albendazole 7.5mg/kg | `seed.cypher` D008 | Module 2 |
| Disease: Bloat — 500ml oil, trocar for free-gas | `seed.cypher` D009 | Module 2 |
| Disease: Pink Eye — Oxytetracycline eye spray | `seed.cypher` D010 | Module 2 |
| Symptom: Prescapular lymph node → ECF (weight 0.95) | `seed.cypher` INDICATES relationships | Module 2, ECF section |
| Symptom: Red/dark urine → Babesiosis (weight 0.95) | `seed.cypher` | Module 2, Babesiosis section |
| Symptom: Repeated abortion → Brucellosis (weight 0.90) | `seed.cypher` | Module 2, Brucellosis section |
| Symptom: Left flank bloat → Bloat (weight 0.95) | `seed.cypher` | Module 2, Bloat section |

---

### 2. KALRO TIMPS 31 (Technologies, Innovations, Management Practices)
**Location in codebase:** `neo4j/seed.cypher` (breed data), `README.md` (sector stats)

| Data point | Code location | Raw source |
|---|---|---|
| Kenya: over **1 million small-scale dairy farmers** | `README.md` | TIMPS 31 Introduction |
| 3.5 million dairy cattle → 4.2 billion litres annually | `README.md` stats | TIMPS 31 Introduction |
| Sahiwal-Friesian cross: 5–15L/day, suited to dry areas (Machakos, Baringo, Kajiado) | `seed.cypher` farmer breeds | TIMPS 31 Dairy Breeds |
| Holstein-Friesian: 40–60L/day; heavy feeder 90–110kg/day | `seed.cypher` + `README.md` breed notes | TIMPS 31 |
| Ayrshire: 30L/day, hardy across Kenyan climatic zones | `seed.cypher` breed reference | TIMPS 31 |

---

### 3. ILRI Smallholder Dairy Farmer Training Manual, 2nd Ed (2019)
**Location:** `neo4j/seed.cypher` (disease treatment backup), `prompts/health_system.txt`

| Data point | Code location |
|---|---|
| Bloat treatment: vegetable oil + walk animal | `seed.cypher` D009 |
| Internal parasite deworming: Albendazole 7.5mg/kg, repeat 21 days | `seed.cypher` D008 |
| FAMACHA scoring for anaemia assessment | `tests/demo_inputs.json` notes |
| Feed requirements for lactating cows | Referenced in fodder advisory prompts |

---

### 4. Kenya Climate Smart Agriculture Strategy 2017–2026
**Location:** `neo4j/seed.cypher` (region nodes), `README.md`

| Data point | Code location | Raw source |
|---|---|---|
| **98% of Kenyan agriculture is rain-fed** | `README.md` | Strategy p.1 |
| Temperature rise: +1°C by 2020, +2.3°C by 2050 | `README.md` | Strategy projections |
| KCSAP target counties (24 counties) | `seed.cypher` Region nodes — `kcsap_target: true` | Strategy Annex |
| Agro-Ecological Zones (AEZ) classification | `seed.cypher` Region nodes — `aez:` field | Strategy AEZ mapping |

---

### 5. AYuTe Africa Champions 2023 — DigiCow Africa Profile
**Location:** `README.md`, `neo4j/seed.cypher` (farmer + agent node structure)

| Data point | Code location | Source |
|---|---|---|
| Co-founder Peninah Wanja: 15 years as extension agent | `README.md` research table | AYuTe 2023, p.1–2 |
| Co-founders: Vincent Kimani (comms/marketing), Jemimah Wanjiku (partnerships) | `README.md` | AYuTe 2023, p.2 |
| AYuTe Africa Challenge **2022 winner** (Heifer International) | `README.md` | AYuTe 2023, p.3 |
| 60,000 farmers reached as of 2023 | `README.md` | AYuTe 2023, p.6 |
| DigiCow platform fields: vet records, breeding dates, pregnancy alerts, Electronic Record Management | `seed.cypher` farmer node fields | AYuTe 2023, p.2 |
| Group training model (parasite control, Magadi) | `tests/demo_inputs.json` training module field | AYuTe 2023, p.4 (photo caption) |

---

### 6. J-PAL / MIT — LLM-Powered Digital Advisory Services (Kenya, 2026–27)
**Location:** `README.md` (validation section), `docs/research_sources.md`

| Data point | Code location | Source |
|---|---|---|
| AI advisory + coordination dual model | `README.md`, Phase One submission | J-PAL p.1 |
| Last-mile agripreneur (extension agent) = same role as our brief | `README.md` | J-PAL p.1: "last-mile agricultural service providers (agripreneurs)" |
| Kenya pilot Feb 2026 – Jan 2027, OCP Kenya + CGA | `README.md` | J-PAL p.1–2 |
| Embedded in Kenya's Farmer Service Centers (FSC) model | `README.md` | J-PAL p.2 |
| WhatsApp chatbot — same delivery pattern we use for USSD/SMS | Architecture decision | J-PAL p.1 |
| Cluster-randomized RCT design | Research validation | J-PAL p.1 |

---

### 7. GSMA — Crop2Cash Case Study (2025, Nigeria)
**Location:** `README.md` (analogous precedent — flagged as Nigeria, not Kenya)

| Data point | Code location | Source |
|---|---|---|
| 500,000+ farmers reached total | `README.md` | GSMA 2025 |
| $2.8M total credit unlocked | `README.md` | GSMA 2025 |
| 70% income increase reported | `README.md` | GSMA 2025 |
| AI-powered IVR hotline (generative AI) — one of few Gen-AI deployments at scale in Africa | `README.md` | GSMA 2025 |
| SMS: 50–70 advisories per farmer per season | Architecture context | GSMA 2025 |
| **NOTE: This is Nigeria (Crop2Cash), not DigiCow Kenya** | `README.md` disclaimer | Verified from PDF URL |

---

### 8. KMD — Agrometeorology Services
**Location:** `neo4j/seed.cypher` (ClimateAdvisory nodes)

| Data point | Code location | Source |
|---|---|---|
| Dekadal (10-day) Agrometeorological Bulletins — year-round | `seed.cypher` ClimateAdvisory `bulletin_type` field | KMD Agrometeorology, p.2 |
| Products: Daily, 5-day, 7-day forecasts | Referenced in Climate node structure | KMD Agrometeorology |
| KAOP: Kenya Agrometeorological Observation Programme | `seed.cypher` `source` field | KMD Agrometeorology |
| Supports agriculture and food security sectors | Architecture rationale | KMD Agrometeorology, p.2 |

---

### 9. KMD — Seasonal Forecast Products
**Location:** `neo4j/seed.cypher` (ClimateAdvisory nodes), data layer design

| Data point | Code location | Source |
|---|---|---|
| Seasonal forecast: rainfall + temperature outlook for upcoming months | `seed.cypher` ClimateAdvisory node | KMD Seasonal Forecast, p.1 |
| Covers all socio-economic sectors: agriculture, health, water | Architecture decision for multi-sector advisory | KMD Seasonal Forecast |
| Anticipates weather-related impacts by region | `seed.cypher` `rainfall_forecast`, `livestock_advisory` fields | KMD Seasonal Forecast |

---

## Key Corrections from Research

These are places where earlier versions of this project had errors that the documents corrected:

| Error (old) | Correction (from document) | Source |
|---|---|---|
| "Dairy = 4% of GDP" | **Dairy = 3.5% of GDP** | KALRO TIMPS 31 Introduction |
| "1.8M smallholder households" | **1M+ small-scale dairy farmers; 2.5M dairy cows** | KALRO TIMPS 31 |
| "Crop2Cash is DigiCow's case study" | **Crop2Cash is a separate Nigerian company** — the GSMA link was mislabelled | GSMA PDF URL verification |
| "AYuTe 2023 winner" (listed in some docs) | **AYuTe 2022 winner** | AYuTe 2023 profile, p.3 |

---

*Last updated: June 22, 2026 — CowSense AI Team*
