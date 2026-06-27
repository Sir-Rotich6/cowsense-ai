# CowSense AI — Hackathon Day Schedule
**June 27, 2026 · 8:00 AM – 5:00 PM EAT**
**Venue: Kenya AI Challenge 2026, Nairobi**

---

## ⚡ BEFORE YOU ARRIVE (tonight, June 26)

| Person | Do this tonight |
|---|---|
| **Enock** | Push GitHub repo. Confirm Anthropic API key has credit ($5+). |
| **Larry** | Create Neo4j Aura free instance at console.neo4j.io. Save connection URI + password. Create Render.com account. |
| **Karol** | Create Lovable.dev account. Read the Lovable prompt in `lovable/LOVABLE_PROMPT.md`. |
| **Sandra** | Create Featherless.ai account. Test one API call with Llama 3.1 8B. Save the demo_inputs.json to phone. |

---

## 8:00 AM — SETUP (ALL, 45 min)

**Everyone does:**
```bash
git clone https://github.com/[your-org]/cowsense-ai.git
cd cowsense-ai
chmod +x scripts/setup.sh && ./scripts/setup.sh
cp .env.example .env
# Fill in .env with your API keys
python scripts/check_env.py
```

**Milestone: All 4 people see green ✅ on check_env.py by 8:45am**

---

## 8:45 AM — PARALLEL TRACKS BEGIN

### 🟢 ENOCK (AI Engineer) — app/agent.py
```
8:45 - 10:00  Test Claude tool_use with real symptoms (no Neo4j yet)
              python -c "import asyncio; from app.agent import run_agent; 
              print(asyncio.run(run_agent('cow has high fever', 'health')))"
10:00 - 11:00 Connect agent to Neo4j — test graphrag_disease_query()
11:00 - 12:00 Run: python scripts/generate_embeddings.py
              Verify vector search works in Neo4j Browser
```

### 🟡 LARRY (Backend) — Neo4j + Render
```
8:45 - 9:30   Open Neo4j Browser → run neo4j/schema.cypher → run neo4j/seed.cypher
              Verify: MATCH (n) RETURN labels(n), count(n)
              Expected: Disease:13, Symptom:35, Region:8, Farmer:5
9:30 - 10:30  Update .env with real Neo4j URI. Start server:
              uvicorn app.main:app --reload --port 8000
              Test: curl http://localhost:8000/demo-farmer
10:30 - 12:00 Deploy to Render:
              - Push latest code to GitHub
              - render.com → New Web Service → Connect repo
              - Add env vars from .env
              - Deploy. Get live HTTPS URL.
              - Test: curl https://cowsense-api.onrender.com/
```

### 🔵 KAROL (Frontend) — Lovable Dashboard
```
8:45 - 10:00  Open Lovable.dev → New project → Paste LOVABLE_PROMPT.md content
              Build: farmer prioritization list page
10:00 - 11:30 Build: health triage form + result display
              Connect to localhost:8000/health-check
11:30 - 12:00 Switch API URL to Render live URL when Larry deploys
```

### 🟣 SANDRA (AI / Prompts) — Prompt QA + Demo Prep
```
8:45 - 10:00  Run 10 symptom tests from tests/demo_inputs.json against mock
              python tests/demo_test.py --base-url http://localhost:8000
              Document any wrong outputs
10:00 - 11:30 Edit prompts/*.txt to fix any bad outputs
              Re-test all 3 scenarios (HC-001, MP-001, CP-001)
11:30 - 12:00 Prepare 3 test inputs for live demo on phone via USSD
```

---

## 12:00 PM — LUNCH BREAK (45 min, MANDATORY)
**No code. Eat. Rest. Back at 12:45.**

---

## 12:45 PM — INTEGRATION (ALL, 2 hours)

**Goal: Full end-to-end working before 2:45pm**

```
12:45  Larry: Confirm Render URL is live
12:45  Karol: Update Lovable to call Render URL
13:00  ALL:   Run demo scenario 1 together (Wanjiku, ECF)
              Expected: East Coast Fever · HIGH · Buparvaquone
13:15  ALL:   Run demo scenario 2 (Eldoret market price)
              Expected: KES 46/L · stable · sell recommendation
13:30  ALL:   Run demo scenario 3 (F002 credit profile)
              Expected: Band A · KES 150,000
13:45  ALL:   Test USSD: dial *384# on AT sandbox → enter 'high fever'
14:00  ALL:   Fix any bugs found
14:30  ALL:   Final full walkthrough — all 3 features working ✅
```

---

## 2:45 PM — DEMO PREP (Enock + Karol, 1 hour)

```
14:45  Enock rehearses 3-minute pitch (use PITCH_SCRIPT.md)
15:00  Karol opens demo on screen, walks through farmer list → advisory
15:15  Full rehearsal: Enock speaks, Karol drives screen
15:30  Second full rehearsal — timed
15:45  Final fixes only
```

---

## 3:45 PM — PHASE 2 SUBMISSION (Larry + Sandra, 45 min)

```
Larry:  Final git push (clean commit message)
Sandra: Upload pitch deck to Google Drive → get shareable link
        Open Phase 2 form → paste PHASE2_SUBMISSION.md content
        Submit all links (GitHub, Render URL, Google Drive deck)
```

---

## 4:30 PM — BUFFER + JUDGE PREP

```
16:30  Confirm all systems live one more time
16:45  Review PITCH_SCRIPT.md judge Q&A section
17:00  DONE. Confident. Ready for June 28.
```

---

## 🚨 EMERGENCY FALLBACKS

| If this breaks | Do this |
|---|---|
| Render deploy fails | Use `ngrok http 8000` → get public URL |
| Neo4j Aura unreachable | App auto-uses mock data — demo still works |
| Claude quota exceeded | Featherless fallback activates automatically |
| Lovable build fails | Use `/docs` Swagger UI as demo interface |
| Internet down | Run everything on localhost — bring laptop to judges |

---

## ✅ DONE WHEN (checklist)

- [ ] `https://cowsense-api.onrender.com/` returns `"status": "live"`
- [ ] `/health-check` returns ECF for "high fever + swollen lymph nodes"
- [ ] `/market-price` returns KES 46/L for eldoret
- [ ] `/credit-profile` returns Band A for F002
- [ ] Lovable dashboard loads and shows farmer list
- [ ] USSD sandbox responds to *384# health query
- [ ] GitHub repo is public with no API keys
- [ ] Phase 2 form submitted before midnight EAT

---

*CowSense AI — Kenya AI Challenge 2026 · June 27, 2026*
