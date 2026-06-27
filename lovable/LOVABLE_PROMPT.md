# CowSense AI — Lovable Build Prompt
**Karol Howard owns this file.**
Paste the prompt below directly into Lovable's chat to build the dashboard.

---

## PASTE THIS INTO LOVABLE:

```
Build a mobile-first web dashboard called CowSense AI for Kenyan dairy extension agents.

Color scheme: dark forest green (#1A3C28) headers, white cards, gold (#C9952C) accents.
Font: Inter or similar clean sans-serif.
Style: clean, simple, works on a phone screen.

The app has 4 screens:

---

SCREEN 1 — HOME (Farmer Priority List)
Header: "CowSense AI" with a small cow emoji 🐄
Subheader: "Good morning, Agent" + today's date

Show a list of farmer cards. Each card has:
- Farmer name (bold)
- Region (small grey text)
- Urgency badge: RED="URGENT", YELLOW="REVIEW", GREEN="ROUTINE"
- One-line reason e.g. "Health alert — cow symptoms reported"
- "View" button

Use this mock data for 3 farmers:
1. Wanjiku Kamau · Nakuru · RED URGENT · "Health alert — cow symptoms reported"
2. Kipchumba Rono · Eldoret · YELLOW REVIEW · "Market opportunity — sell window open"
3. Mwangi Githinji · Nakuru · GREEN ROUTINE · "Regular check-in due"

Clicking "View" on any farmer opens Screen 2.

---

SCREEN 2 — FARMER DETAIL
Back button at top left.
Farmer name as page title.
Three tabs: "🐄 Health" | "💰 Market" | "💳 Credit"

TAB 1 — HEALTH TRIAGE:
- Text area: "Describe cow symptoms..." (placeholder)
- Dropdown: Cow age (1, 2, 3, 4, 5+ years)
- Big green button: "Check Health"
- Result card (shown after submit):
  - Disease name (large bold)
  - Severity badge (RED=HIGH, YELLOW=MEDIUM, GREEN=LOW)
  - Medicine field
  - Dosage field
  - Urgency label e.g. "🚨 URGENT — Call vet now"
  - Grey advisory text box for the AI advisory paragraph

TAB 2 — MARKET PRICE:
- Dropdown: Region (Nakuru, Eldoret, Nairobi, Kisii, Meru, Embu, Kericho, Bomet)
- Number input: "Milk volume (litres)"
- Green button: "Check Price"
- Result card:
  - Price per litre (big number e.g. "KES 52")
  - Trend badge: GREEN=RISING, GREY=STABLE, RED=FALLING
  - Estimated revenue e.g. "KES 936 for 18L"
  - Best region comparison e.g. "Best price: Nairobi at KES 55"
  - Advisory text

TAB 3 — CREDIT PROFILE:
- Text input: "Farmer ID" (pre-filled with farmer's ID)
- Green button: "Generate Credit Profile"
- Result card:
  - Score gauge or big number e.g. "80 / 100"
  - Band badge: A=GOLD, B=GREEN, C=YELLOW, D=RED
  - Max loan e.g. "KES 150,000 eligible"
  - Score breakdown as 4 tick items
  - Advisory text

---

SCREEN 3 — USSD SIMULATOR (bonus screen, simple)
Title: "Test SMS/USSD"
Show a phone mockup with:
- Input: "Type symptom or region"
- Button: "Send"
- Output box showing the SMS response

---

API INTEGRATION:
All API calls go to: https://cowsense-api.onrender.com
Endpoints:
- POST /health-check — body: {farmer_id, symptoms: [string], cow_age_years, region}
- POST /market-price — body: {farmer_id, region, milk_volume_l}
- POST /credit-profile — body: {farmer_id}
- GET /prioritize-farmers — for the home screen list

Show a loading spinner during API calls.
Show error state if API is unreachable (grey card: "Connect to server to get live data").

Make the app work with mock data if the API is offline.
```

---

## AFTER LOVABLE BUILDS IT:

1. Test each tab with demo data from `tests/demo_inputs.json`
2. Replace `https://cowsense-api.onrender.com` with your actual Render URL
3. Test on mobile browser (Chrome on Android)
4. Share the Lovable public URL — this is your demo link

## DEMO SCENARIO TO TEST:
1. Home screen → click Wanjiku Kamau
2. Health tab → type "high fever, swollen lymph nodes" → Check Health
3. Expected: East Coast Fever · HIGH · Buparvaquone
4. Market tab → Nakuru · 18L → Check Price
5. Expected: KES 52/L · Rising · Sell now
6. Credit tab → F001 → Generate
7. Expected: 80/100 · Band A · KES 150,000
