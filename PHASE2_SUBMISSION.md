# CowSense AI — Phase 2 Submission
## Copy-paste each section into the Oxbridge form

---

## 1. PROJECT TITLE
```
CowSense AI
```

---

## 2. TEAM NAME AND MEMBERS
```
Team Name: CowSense AI

Members:
- Enock Rotich     — Team Lead / AI Engineer
- Larry Baraza     — Backend Developer
- Karol Howard     — Frontend / UX
- Sandra Kimiring  — AI Engineer / Prompts
```

---

## 3. SELECTED CHALLENGE BRIEF
```
DigiCow Africa Ltd — AI powered farmer intelligence system
to improve adoption and productivity
```
**Form selection:** Official Mercy Corps brief → Advisory → DigiCow Africa Ltd

---

## 4. WHAT IS YOUR SOLUTION? (200 words)

**First sentence (44 chars — must be ≤50):**
```
AI advisor for Kenya dairy extension agents.
```

**Full solution description (paste this into the form):**
```
AI advisor for Kenya dairy extension agents.

CowSense AI gives youth extension agents three AI tools they
use during farm visits — powered by Claude API and a Neo4j
knowledge graph of KALRO-verified Kenyan livestock data.

1. Livestock Health Triage: The agent types cow symptoms in
   plain text. CowSense AI semantically matches them against
   13 diseases sourced from the KALRO Dairy Value Chain
   Manual and returns a diagnosis, medicine, dosage, and
   urgency level — grounded in the graph, never invented.

2. Market Price Intelligence: The agent enters the farmer's
   region and milk volume. CowSense AI returns the current
   KES/litre price, trend, buyer name, and whether to sell
   now or hold — across 8 Kenyan dairy regions.

3. AgriFin Credit Profile: The agent enters a farmer ID.
   CowSense AI scores their DigiCow platform activity and
   returns a credit band (A–D) and maximum loan eligibility
   in KES for MFI/SACCO referral.

The agent opens the dashboard to a prioritized farmer list
ranked by health risk, market opportunity, and AgriFin
readiness. Works on web and via USSD on any phone.
```

**Word count: 178 words ✅ (under 200)**

---

## 5. PITCH DECK LINK
```
[Upload CowSense_AI_Team_Deck.pptx to Google Drive]

Steps to get link:
1. Go to drive.google.com
2. Upload CowSense_AI_Team_Deck.pptx
3. Right-click → Share → Anyone with link → Viewer
4. Copy link → paste here
```

**OR upload to Google Slides:**
1. Go to slides.google.com → Import → Upload the PPTX
2. File → Share → Anyone with link → Viewer
3. Copy link

---

## 6. PRESENTATION VIDEO LINK
```
[Record on Loom: loom.com]

3-MINUTE VIDEO SCRIPT:

[0:00 - 0:20] HOOK
"1.8 million Kenyan dairy farming families.
When a cow gets sick at 6pm, there is no vet.
When milk prices drop, farmers don't know.
When they need a loan, the bank says no data.
We built CowSense AI."

[0:20 - 0:50] PROBLEM
"Youth extension agents serve 80–200 farmers each
with no tool to know who needs help today, what
advice to give, or which farmer qualifies for credit.
They plan every visit on intuition, not intelligence."

[0:50 - 1:40] LIVE DEMO — Health Triage
"Let me show you this working right now.
I type: high fever, swollen lymph nodes.
[SHOW SCREEN — type into dashboard]
CowSense AI queries our Neo4j disease graph —
sourced from the KALRO Dairy Value Chain Manual —
and returns: East Coast Fever. HIGH severity.
Medicine: Buparvaquone, 2.5mg/kg. Call vet now.
This is grounded data. The AI writes the words.
The graph provides the facts. No hallucination."

[1:40 - 2:10] DEMO — Market + Credit
"Same agent, same dashboard.
[SHOW market tab] Eldoret, 30 litres — KES 46/L, stable.
Best price is Nairobi at KES 55. AI recommends holding.
[SHOW credit tab] Farmer F002 — score 100/100, Band A.
Eligible for KES 150,000 through partner MFIs.
One click. Agent makes the referral today."

[2:10 - 2:40] TECH + SCALE
"Built on Claude API with tool_use — Claude calls
Neo4j directly. No Masumi. No extra framework.
Featherless runs Llama 3.1 8B as our open LLM fallback.
Africa's Talking handles SMS and USSD — any phone, no
internet needed. DigiCow already has 370,000 farmers
across 23 counties. We are the intelligence layer."

[2:40 - 3:00] CLOSE
"CowSense AI: the farmer's doctor, trader, and banker
— in one dashboard and one SMS.
Team: Enock, Larry, Karol, Sandra. Thank you."
```

---

## 7. PROTOTYPE / DEPLOYED LINK
```
https://cowsense-api.onrender.com

(FastAPI backend — judges can test live at /docs)
Interactive API docs: https://cowsense-api.onrender.com/docs

If Lovable is ready:
https://cowsense-ai.lovable.app
```

**If Render is not deployed yet — temporary link:**
```
Use the /docs Swagger UI from your local ngrok:
  ngrok http 8000
  → Copy the https URL
  → Submit that as temporary link
  → Update in Phase 3
```

---

## 8. GITHUB LINK

### Push commands (run these now):

**If starting fresh (new repo):**
```bash
cd cowsense-ai
git init
git add .
git commit -m "feat: CowSense AI — Kenya AI Challenge 2026 Phase 2"
git branch -M main
git remote add origin https://github.com/[YOUR-USERNAME]/cowsense-ai.git
git push -u origin main
```

**If repo already exists (update it):**
```bash
cd cowsense-ai
git add .
git commit -m "feat: add GraphRAG, USSD handler, routers, render deploy"
git push origin main
```

**Make sure repo is PUBLIC:**
GitHub → repo → Settings → Danger Zone → Change visibility → Public

**Confirm NO secrets in the repo:**
```bash
grep -r "sk-ant\|neo4j+s://.*@\|Bearer " . --include="*.py" --include="*.yaml"
# Must return nothing
```

**Submit this link:**
```
https://github.com/[YOUR-USERNAME]/cowsense-ai
```

---

## CHECKLIST BEFORE SUBMITTING

- [ ] Pitch deck link is public (anyone with link can view)
- [ ] Video link is public (anyone can watch on Loom)
- [ ] Prototype link loads without login
- [ ] GitHub repo is public
- [ ] GitHub has NO API keys / passwords
- [ ] All 8 form fields filled
- [ ] Submitted before June 25, midnight EAT

---

*CowSense AI · Kenya AI Challenge 2026 · Mercy Corps AgriFin Track*
