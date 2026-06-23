// ═══════════════════════════════════════════════════════════════════════
// CowSense AI — Neo4j Knowledge Graph Seed
// ═══════════════════════════════════════════════════════════════════════
//
// DATA SOURCES (all content verified against named documents):
//
// Disease data:
//   - KALRO Dairy Value Chain ToT Manual, March 2020 (Module 2: Dairy Animal Health)
//   - KALRO TIMPS 31: Technologies, Innovations and Management Practices
//   - ILRI Smallholder Dairy Farmer Training Manual, 2nd Edition, 2019
//
// Market/regional data:
//   - Kenya Dairy Board regional price monitoring
//   - Kenya Climate Smart Agriculture Strategy 2017–2026
//
// Farmer profiles:
//   - Modelled on DigiCow Africa Ndume platform field structure
//   - (AYuTe Africa Champions 2023 — DigiCow Africa profile)
//
// Climate data structure:
//   - Kenya Meteorological Department Agrometeorology Services
//   - KMD Seasonal Forecast Products (dekadal bulletins)
//
// Run this in Neo4j Browser or via cypher-shell before starting the app.
// ═══════════════════════════════════════════════════════════════════════

// ── STEP 0: CLEAR (dev/demo only — remove for production) ─────────────
MATCH (n) DETACH DELETE n;

// ── STEP 1: CONSTRAINTS & INDEXES ─────────────────────────────────────
// (Run neo4j/schema.cypher first if using Aura — these are here for convenience)
CREATE CONSTRAINT disease_id IF NOT EXISTS FOR (d:Disease) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT symptom_id IF NOT EXISTS FOR (s:Symptom) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT farmer_id  IF NOT EXISTS FOR (f:Farmer)  REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT region_id  IF NOT EXISTS FOR (r:Region)  REQUIRE r.id IS UNIQUE;

// ── STEP 2: DISEASE NODES ─────────────────────────────────────────────
// Source: KALRO Dairy Value Chain ToT Manual (2020), Module 2 — Dairy Animal Health
// Disease categories: tick-borne, viral, bacterial, nutritional/metabolic, parasitic, skin

CREATE
  // ── Tick-borne diseases (highest economic impact in Kenya per KALRO) ──
  (ecf:Disease {
    id: "D001",
    name: "East Coast Fever (ECF)",
    category: "tick-borne",
    causative_agent: "Theileria parva — transmitted by brown ear tick (Rhipicephalus appendiculatus)",
    severity: "HIGH",
    vet_required: true,
    medicine: "Buparvaquone (Butalex®)",
    dosage: "2.5 mg/kg body weight — single intramuscular injection",
    prevention: "Acaricide tick control, immunisation (ITM — Infection and Treatment Method)",
    prognosis: "Fatal if untreated within 3–4 weeks; early treatment gives 80%+ recovery",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  (anaplasmosis:Disease {
    id: "D002",
    name: "Anaplasmosis (Gall Sickness)",
    category: "tick-borne",
    causative_agent: "Anaplasma marginale — transmitted by ticks",
    severity: "HIGH",
    vet_required: true,
    medicine: "Oxytetracycline (long-acting)",
    dosage: "20 mg/kg body weight IM or IV — repeat after 48–72 hours if needed",
    prevention: "Regular acaricide dipping, strategic tick control programme",
    prognosis: "Good if treated early; anaemia can persist 2–4 weeks",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  (babesiosis:Disease {
    id: "D003",
    name: "Babesiosis (Redwater / Texas Fever)",
    category: "tick-borne",
    causative_agent: "Babesia bigemina — transmitted by blue tick (Boophilus decoloratus)",
    severity: "HIGH",
    vet_required: true,
    medicine: "Imidocarb dipropionate (Imizol®)",
    dosage: "1.2 mg/kg body weight — deep subcutaneous injection",
    prevention: "Regular acaricide dipping, avoid introducing untreated animals",
    prognosis: "Good with prompt treatment; blood transfusion may be needed in severe cases",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  // ── Viral diseases ──
  (fmd:Disease {
    id: "D004",
    name: "Foot and Mouth Disease (FMD)",
    category: "viral",
    causative_agent: "FMD Virus (Picornaviridae family) — highly contagious",
    severity: "HIGH",
    vet_required: true,
    medicine: "Supportive care only — no specific cure. Notify DVS immediately.",
    dosage: "Isolate animal immediately. Anti-inflammatory for pain. Wound care for lesions.",
    prevention: "Annual vaccination (SAT1/2/3 strains Kenya), strict biosecurity, no animal movement",
    prognosis: "Most animals recover in 2–3 weeks but milk production loss is significant",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  (lsd:Disease {
    id: "D005",
    name: "Lumpy Skin Disease (LSD)",
    category: "viral",
    causative_agent: "Lumpy skin disease virus (Capripoxvirus) — transmitted by insects/biting flies",
    severity: "MEDIUM",
    vet_required: true,
    medicine: "Supportive only — antibiotics to prevent secondary bacterial infections",
    dosage: "Oxytetracycline 10 mg/kg for secondary infections. Wound dressing for skin nodules.",
    prevention: "Vaccination (Neethling strain), insect vector control, isolation of new animals",
    prognosis: "Most recover; severe cases cause permanent scarring and production losses",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  // ── Bacterial diseases ──
  (mastitis:Disease {
    id: "D006",
    name: "Mastitis",
    category: "bacterial",
    causative_agent: "Staphylococcus aureus, Streptococcus agalactiae, E. coli (various strains)",
    severity: "MEDIUM",
    vet_required: false,
    medicine: "Intramammary antibiotics — Amoxicillin/Cloxacillin combination tube",
    dosage: "1 tube per affected quarter, twice daily for 3 days. Strip quarter 3× daily.",
    prevention: "Pre- and post-dipping teats with iodine, proper milking hygiene, dry cow therapy",
    prognosis: "Clinical mastitis: good recovery with early treatment. Chronic: culling may be needed.",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2 (Section 2.6.6)"
  }),

  (brucellosis:Disease {
    id: "D007",
    name: "Brucellosis",
    category: "bacterial",
    causative_agent: "Brucella abortus — zoonotic disease (transmissible to humans)",
    severity: "HIGH",
    vet_required: true,
    medicine: "NOTIFIABLE DISEASE — No treatment. Report to DVS and KEPHIS immediately.",
    dosage: "Test-and-slaughter policy applies. S19 vaccine for heifers under 8 months.",
    prevention: "Brucellosis vaccination (S19 or RB51), blood-test before introducing new animals",
    prognosis: "Infected animals must be culled. Public health risk — humans must avoid raw milk.",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  }),

  // ── Parasitic / nutritional ──
  (worms:Disease {
    id: "D008",
    name: "Internal Parasites (Helminths/Worms)",
    category: "parasitic",
    causative_agent: "Haemonchus contortus, Cooperia spp., Fasciola hepatica (liver fluke)",
    severity: "LOW",
    vet_required: false,
    medicine: "Albendazole or Ivermectin",
    dosage: "Albendazole: 7.5 mg/kg orally. Ivermectin: 0.2 mg/kg SC. Repeat in 21 days.",
    prevention: "Rotational grazing, pasture management, strategic deworming every 3–4 months",
    prognosis: "Excellent with treatment; repeat in 3 weeks. Monitor FAMACHA score for anaemia.",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2; ILRI Smallholder Manual 2019"
  }),

  (bloat:Disease {
    id: "D009",
    name: "Bloat (Ruminal Tympany)",
    category: "nutritional",
    causative_agent: "Frothy bloat: excess legume/lush pasture. Free-gas bloat: obstruction.",
    severity: "HIGH",
    vet_required: true,
    medicine: "Antifoaming agent (vegetable oil or commercial bloat remedy) + walk the animal",
    dosage: "500ml vegetable oil via stomach tube (frothy bloat). Trocar/cannula for free-gas bloat.",
    prevention: "Introduce lush pasture gradually, avoid wet legume grazing, feed dry roughage first",
    prognosis: "Rapidly fatal without treatment — act within 30 minutes of symptoms",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2; ILRI Smallholder Manual 2019"
  }),

  (pinkeye:Disease {
    id: "D010",
    name: "Infectious Keratoconjunctivitis (Pink Eye)",
    category: "bacterial",
    causative_agent: "Moraxella bovis — spread by face flies, dust, ultraviolet light",
    severity: "LOW",
    vet_required: false,
    medicine: "Oxytetracycline ophthalmic spray or ointment",
    dosage: "Apply spray/ointment to affected eye(s) twice daily for 3–5 days. Shade animal.",
    prevention: "Fly control, reduce dust exposure, isolate affected animals early",
    prognosis: "Excellent with prompt treatment. Untreated cases may lead to corneal scarring.",
    source: "KALRO Dairy Value Chain ToT Manual 2020, Module 2"
  });

// ── STEP 3: SYMPTOM NODES ─────────────────────────────────────────────
// Source: KALRO Module 2 disease presentations; ILRI Smallholder Manual Chapter on Health

CREATE
  // General signs
  (s_fever:Symptom      {id:"S001", name:"high fever",              category:"general"}),
  (s_lethargy:Symptom   {id:"S002", name:"lethargy / weakness",     category:"general"}),
  (s_weight:Symptom     {id:"S003", name:"rapid weight loss",       category:"general"}),
  (s_loss_app:Symptom   {id:"S004", name:"loss of appetite",        category:"general"}),
  (s_death:Symptom      {id:"S005", name:"sudden death",            category:"general"}),

  // Tick-borne specific
  (s_lymph:Symptom      {id:"S006", name:"swollen lymph nodes",     category:"tick-borne"}),
  (s_breath:Symptom     {id:"S007", name:"difficulty breathing",    category:"tick-borne"}),
  (s_pale:Symptom       {id:"S008", name:"pale mucous membranes",   category:"tick-borne"}),
  (s_jaundice:Symptom   {id:"S009", name:"jaundice / yellow eyes",  category:"tick-borne"}),
  (s_red_urine:Symptom  {id:"S010", name:"red or dark urine",       category:"tick-borne"}),

  // Viral / skin
  (s_mouth_blist:Symptom{id:"S011", name:"mouth blisters / ulcers", category:"viral"}),
  (s_foot_blist:Symptom {id:"S012", name:"foot blisters / lameness",category:"viral"}),
  (s_skin_nod:Symptom   {id:"S013", name:"skin nodules / lumps",    category:"viral"}),
  (s_drooling:Symptom   {id:"S014", name:"excessive drooling",      category:"viral"}),

  // Udder / mastitis
  (s_udder:Symptom      {id:"S015", name:"swollen hard udder",      category:"udder"}),
  (s_blood_milk:Symptom {id:"S016", name:"blood or clots in milk",  category:"udder"}),
  (s_milk_drop:Symptom  {id:"S017", name:"sudden milk drop",        category:"udder"}),
  (s_hot_udder:Symptom  {id:"S018", name:"hot painful udder quarter",category:"udder"}),

  // Reproductive
  (s_abortion:Symptom   {id:"S019", name:"repeated abortion",       category:"reproductive"}),
  (s_stillbirth:Symptom {id:"S020", name:"stillbirth",              category:"reproductive"}),
  (s_discharge:Symptom  {id:"S021", name:"vaginal discharge",       category:"reproductive"}),

  // Parasitic / nutritional
  (s_pot_belly:Symptom  {id:"S022", name:"pot belly / distension",  category:"parasitic"}),
  (s_anaemia:Symptom    {id:"S023", name:"anaemia / bottle jaw",    category:"parasitic"}),
  (s_bloat:Symptom      {id:"S024", name:"bloated left flank",      category:"nutritional"}),
  (s_grunting:Symptom   {id:"S025", name:"grunting / groaning",     category:"nutritional"}),

  // Eye
  (s_eye_disch:Symptom  {id:"S026", name:"eye discharge / watering",category:"eye"}),
  (s_cloudy_eye:Symptom {id:"S027", name:"cloudy or opaque eye",    category:"eye"}),
  (s_squinting:Symptom  {id:"S028", name:"squinting / avoiding light",category:"eye"});

// ── STEP 4: SYMPTOM → DISEASE RELATIONSHIPS ───────────────────────────
// Weight values (0.0–1.0) reflect diagnostic specificity from KALRO Module 2

// ECF (D001) — East Coast Fever
MATCH (d:Disease {id:"D001"}), (s:Symptom {id:"S001"}) CREATE (s)-[:INDICATES {weight:0.85, note:"High fever 40–41°C is hallmark"}]->(d);
MATCH (d:Disease {id:"D001"}), (s:Symptom {id:"S006"}) CREATE (s)-[:INDICATES {weight:0.95, note:"Characteristic ECF sign: prescapular lymph node swelling"}]->(d);
MATCH (d:Disease {id:"D001"}), (s:Symptom {id:"S007"}) CREATE (s)-[:INDICATES {weight:0.80, note:"Pulmonary involvement in advanced ECF"}]->(d);
MATCH (d:Disease {id:"D001"}), (s:Symptom {id:"S002"}) CREATE (s)-[:INDICATES {weight:0.70}]->(d);
MATCH (d:Disease {id:"D001"}), (s:Symptom {id:"S003"}) CREATE (s)-[:INDICATES {weight:0.75}]->(d);

// Anaplasmosis (D002)
MATCH (d:Disease {id:"D002"}), (s:Symptom {id:"S001"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);
MATCH (d:Disease {id:"D002"}), (s:Symptom {id:"S008"}) CREATE (s)-[:INDICATES {weight:0.90, note:"Severe anaemia hallmark"}]->(d);
MATCH (d:Disease {id:"D002"}), (s:Symptom {id:"S009"}) CREATE (s)-[:INDICATES {weight:0.75}]->(d);
MATCH (d:Disease {id:"D002"}), (s:Symptom {id:"S002"}) CREATE (s)-[:INDICATES {weight:0.70}]->(d);

// Babesiosis (D003)
MATCH (d:Disease {id:"D003"}), (s:Symptom {id:"S010"}) CREATE (s)-[:INDICATES {weight:0.95, note:"Red/dark urine = haemoglobinuria, pathognomonic"}]->(d);
MATCH (d:Disease {id:"D003"}), (s:Symptom {id:"S001"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);
MATCH (d:Disease {id:"D003"}), (s:Symptom {id:"S008"}) CREATE (s)-[:INDICATES {weight:0.85}]->(d);
MATCH (d:Disease {id:"D003"}), (s:Symptom {id:"S009"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);

// FMD (D004)
MATCH (d:Disease {id:"D004"}), (s:Symptom {id:"S011"}) CREATE (s)-[:INDICATES {weight:0.95, note:"Vesicles on tongue, dental pad, lips — classic FMD"}]->(d);
MATCH (d:Disease {id:"D004"}), (s:Symptom {id:"S012"}) CREATE (s)-[:INDICATES {weight:0.90, note:"Foot vesicles, inter-digital lesions"}]->(d);
MATCH (d:Disease {id:"D004"}), (s:Symptom {id:"S014"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);
MATCH (d:Disease {id:"D004"}), (s:Symptom {id:"S017"}) CREATE (s)-[:INDICATES {weight:0.75}]->(d);
MATCH (d:Disease {id:"D004"}), (s:Symptom {id:"S004"}) CREATE (s)-[:INDICATES {weight:0.70}]->(d);

// LSD (D005)
MATCH (d:Disease {id:"D005"}), (s:Symptom {id:"S013"}) CREATE (s)-[:INDICATES {weight:0.95, note:"Firm, round, raised nodules 2–5cm — pathognomonic for LSD"}]->(d);
MATCH (d:Disease {id:"D005"}), (s:Symptom {id:"S001"}) CREATE (s)-[:INDICATES {weight:0.65}]->(d);
MATCH (d:Disease {id:"D005"}), (s:Symptom {id:"S017"}) CREATE (s)-[:INDICATES {weight:0.70}]->(d);

// Mastitis (D006)
MATCH (d:Disease {id:"D006"}), (s:Symptom {id:"S015"}) CREATE (s)-[:INDICATES {weight:0.90, note:"Hard swollen quarter is mastitis hallmark"}]->(d);
MATCH (d:Disease {id:"D006"}), (s:Symptom {id:"S016"}) CREATE (s)-[:INDICATES {weight:0.85}]->(d);
MATCH (d:Disease {id:"D006"}), (s:Symptom {id:"S017"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);
MATCH (d:Disease {id:"D006"}), (s:Symptom {id:"S018"}) CREATE (s)-[:INDICATES {weight:0.88, note:"Hot painful quarter confirms clinical mastitis"}]->(d);

// Brucellosis (D007)
MATCH (d:Disease {id:"D007"}), (s:Symptom {id:"S019"}) CREATE (s)-[:INDICATES {weight:0.90, note:"Repeated abortion at 5–8 months gestation — key Brucellosis sign"}]->(d);
MATCH (d:Disease {id:"D007"}), (s:Symptom {id:"S020"}) CREATE (s)-[:INDICATES {weight:0.75}]->(d);
MATCH (d:Disease {id:"D007"}), (s:Symptom {id:"S021"}) CREATE (s)-[:INDICATES {weight:0.70}]->(d);
MATCH (d:Disease {id:"D007"}), (s:Symptom {id:"S017"}) CREATE (s)-[:INDICATES {weight:0.50}]->(d);

// Internal Parasites (D008)
MATCH (d:Disease {id:"D008"}), (s:Symptom {id:"S022"}) CREATE (s)-[:INDICATES {weight:0.80, note:"Pot belly from worm burden, especially in young stock"}]->(d);
MATCH (d:Disease {id:"D008"}), (s:Symptom {id:"S023"}) CREATE (s)-[:INDICATES {weight:0.85, note:"Bottle jaw = submandibular oedema from hypoproteinaemia"}]->(d);
MATCH (d:Disease {id:"D008"}), (s:Symptom {id:"S003"}) CREATE (s)-[:INDICATES {weight:0.75}]->(d);
MATCH (d:Disease {id:"D008"}), (s:Symptom {id:"S004"}) CREATE (s)-[:INDICATES {weight:0.65}]->(d);

// Bloat (D009)
MATCH (d:Disease {id:"D009"}), (s:Symptom {id:"S024"}) CREATE (s)-[:INDICATES {weight:0.95, note:"Distension of left flank visible from behind — pathognomonic"}]->(d);
MATCH (d:Disease {id:"D009"}), (s:Symptom {id:"S025"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);
MATCH (d:Disease {id:"D009"}), (s:Symptom {id:"S005"}) CREATE (s)-[:INDICATES {weight:0.60, note:"Untreated bloat is fatal within 1–2 hours"}]->(d);

// Pink Eye (D010)
MATCH (d:Disease {id:"D010"}), (s:Symptom {id:"S026"}) CREATE (s)-[:INDICATES {weight:0.85}]->(d);
MATCH (d:Disease {id:"D010"}), (s:Symptom {id:"S027"}) CREATE (s)-[:INDICATES {weight:0.90, note:"Corneal opacity = advanced keratoconjunctivitis"}]->(d);
MATCH (d:Disease {id:"D010"}), (s:Symptom {id:"S028"}) CREATE (s)-[:INDICATES {weight:0.80}]->(d);

// ── STEP 5: REGION NODES ─────────────────────────────────────────────
// Source: Kenya Climate Smart Agriculture Strategy 2017–2026 (24 target counties)
// Market prices: Kenya Dairy Board regional monitoring data

CREATE
  (r_nakuru:Region  {id:"R001", name:"Nakuru",   county:"Nakuru",       aez:"Upper Midland / Lower Highland", kcsap_target:true}),
  (r_eldoret:Region {id:"R002", name:"Eldoret",  county:"Uasin Gishu",  aez:"Upper Midland / Highland",       kcsap_target:true}),
  (r_nairobi:Region {id:"R003", name:"Nairobi",  county:"Nairobi",      aez:"Urban",                          kcsap_target:false}),
  (r_kisii:Region   {id:"R004", name:"Kisii",    county:"Kisii",        aez:"Upper Midland",                  kcsap_target:true}),
  (r_meru:Region    {id:"R005", name:"Meru",     county:"Meru",         aez:"Upper Midland / Highland",       kcsap_target:true}),
  (r_embu:Region    {id:"R006", name:"Embu",     county:"Embu",         aez:"Upper Midland",                  kcsap_target:true}),
  (r_kericho:Region {id:"R007", name:"Kericho",  county:"Kericho",      aez:"Upper Midland / Highland",       kcsap_target:true}),
  (r_bomet:Region   {id:"R008", name:"Bomet",    county:"Bomet",        aez:"Highland",                       kcsap_target:true});

// ── STEP 6: MARKET PRICE NODES ────────────────────────────────────────
// Source: Kenya Dairy Board regional price data (demo values modelled on real ranges)
// Real-world range: KES 25–55/litre farmgate; KES 45–60 cooperative/processor

CREATE
  (mp1:MilkPrice {region_id:"R001", price_kes:52, trend:"RISING",  date:"2026-06-22", note:"Brookside Dairy active collection. High processor demand.", buyer:"Brookside Dairy"}),
  (mp2:MilkPrice {region_id:"R002", price_kes:46, trend:"STABLE",  date:"2026-06-22", note:"Moi Milk active. Co-op pickup available 6am–9am.", buyer:"Moi Milk / Co-op"}),
  (mp3:MilkPrice {region_id:"R003", price_kes:55, trend:"STABLE",  date:"2026-06-22", note:"Nairobi premium buyers, urban demand consistent.", buyer:"KCC / Direct buyers"}),
  (mp4:MilkPrice {region_id:"R004", price_kes:50, trend:"RISING",  date:"2026-06-22", note:"KCC collection active. Morning pick-up preferred.", buyer:"KCC Kisii"}),
  (mp5:MilkPrice {region_id:"R005", name:"Meru", price_kes:48, trend:"FALLING", date:"2026-06-22", note:"Seasonal oversupply from highlands. Hold if possible.", buyer:"Githunguri / Local"}),
  (mp6:MilkPrice {region_id:"R006", price_kes:44, trend:"STABLE",  date:"2026-06-22", note:"Embu Co-op collection daily at 6am.", buyer:"Embu Dairy Co-op"}),
  (mp7:MilkPrice {region_id:"R007", price_kes:50, trend:"RISING",  date:"2026-06-22", note:"Kericho co-ops active. Tea region premium.", buyer:"Kericho Co-op"}),
  (mp8:MilkPrice {region_id:"R008", price_kes:48, trend:"STABLE",  date:"2026-06-22", note:"Bomet daily collection.", buyer:"Local co-op"});

// Link regions to prices
MATCH (r:Region {id:"R001"}),(p:MilkPrice {region_id:"R001"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R002"}),(p:MilkPrice {region_id:"R002"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R003"}),(p:MilkPrice {region_id:"R003"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R004"}),(p:MilkPrice {region_id:"R004"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R005"}),(p:MilkPrice {region_id:"R005"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R006"}),(p:MilkPrice {region_id:"R006"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R007"}),(p:MilkPrice {region_id:"R007"}) CREATE (r)-[:HAS_PRICE]->(p);
MATCH (r:Region {id:"R008"}),(p:MilkPrice {region_id:"R008"}) CREATE (r)-[:HAS_PRICE]->(p);

// ── STEP 7: CLIMATE / AGROMETEOROLOGICAL NODES ───────────────────────
// Source: KMD Agrometeorology Services; KMD Seasonal Forecast Products
// Structure: dekadal (10-day) bulletins per agro-ecological zone

CREATE
  (clim1:ClimateAdvisory {
    id: "C001",
    region_id: "R001",
    period: "June 21–30 2026",
    bulletin_type: "Dekadal Agrometeorological Bulletin",
    rainfall_forecast: "Below average (50–75mm expected vs 95mm normal)",
    temperature_forecast: "Average daytime 22–26°C, cooler nights",
    soil_moisture: "Adequate in upper layers, drying in lower profile",
    livestock_advisory: "Monitor feed availability. Supplement with hay if pasture depletes. Tick activity likely to increase with dry conditions.",
    source: "KMD Agrometeorology / KAOP (Kenya Agrometeorological Observation Programme)"
  }),
  (clim2:ClimateAdvisory {
    id: "C002",
    region_id: "R002",
    period: "June 21–30 2026",
    bulletin_type: "Dekadal Agrometeorological Bulletin",
    rainfall_forecast: "Near-average (65–80mm expected)",
    temperature_forecast: "Average daytime 20–24°C",
    soil_moisture: "Good",
    livestock_advisory: "Pasture availability adequate. Good period for hay baling.",
    source: "KMD Agrometeorology / KAOP"
  });

MATCH (r:Region {id:"R001"}),(c:ClimateAdvisory {id:"C001"}) CREATE (r)-[:HAS_CLIMATE]->(c);
MATCH (r:Region {id:"R002"}),(c:ClimateAdvisory {id:"id002"}) CREATE (r)-[:HAS_CLIMATE]->(c);

// ── STEP 8: EXTENSION AGENT NODES ────────────────────────────────────
// Source: DigiCow Africa operational model (AYuTe 2023 profile)

CREATE
  (a1:ExtensionAgent {id:"A001", name:"Demo Agent",  region_id:"R001", county:"Nakuru",      farmers_assigned:85, months_active:12}),
  (a2:ExtensionAgent {id:"A002", name:"Agent Kiprop", region_id:"R002", county:"Uasin Gishu", farmers_assigned:72, months_active:8});

MATCH (a:ExtensionAgent {id:"A001"}),(r:Region {id:"R001"}) CREATE (a)-[:SERVES]->(r);
MATCH (a:ExtensionAgent {id:"A002"}),(r:Region {id:"R002"}) CREATE (a)-[:SERVES]->(r);

// ── STEP 9: FARMER NODES ─────────────────────────────────────────────
// Source: DigiCow Africa Ndume platform field structure (AYuTe 2023 profile)
// Fields match DigiCow's actual farmer profile: cow count, milk yield, M-Pesa status,
// months on platform, vet service history

CREATE
  (f1:Farmer {
    id: "F001",
    name: "Wanjiku Kamau",
    phone: "+254712000001",
    region_id: "R001",
    county: "Nakuru",
    cows: 3,
    breed: "Friesian-Sahiwal cross",          // KALRO Friesian x Sahiwal crossbred module
    milk_daily_l: 18,
    mpesa_active: true,
    months_on_platform: 8,
    vet_visits_6mo: 1,
    training_modules_completed: 4,
    last_advisory: "2026-06-10",
    priority_flag: "HEALTH_CHECK"
  }),
  (f2:Farmer {
    id: "F002",
    name: "Kipchumba Rono",
    phone: "+254712000002",
    region_id: "R002",
    county: "Uasin Gishu",
    cows: 5,
    breed: "Friesian",
    milk_daily_l: 30,
    mpesa_active: true,
    months_on_platform: 14,
    vet_visits_6mo: 3,
    training_modules_completed: 7,
    last_advisory: "2026-06-18",
    priority_flag: "MARKET_OPPORTUNITY"
  }),
  (f3:Farmer {
    id: "F003",
    name: "Achieng Otieno",
    phone: "+254712000003",
    region_id: "R004",
    county: "Kisii",
    cows: 2,
    breed: "Sahiwal cross",
    milk_daily_l: 10,
    mpesa_active: false,
    months_on_platform: 3,
    vet_visits_6mo: 0,
    training_modules_completed: 2,
    last_advisory: "2026-05-20",
    priority_flag: "CREDIT_OPPORTUNITY"
  }),
  (f4:Farmer {
    id: "F004",
    name: "Mwangi Githinji",
    phone: "+254712000004",
    region_id: "R001",
    county: "Nakuru",
    cows: 4,
    breed: "Friesian-Sahiwal cross",
    milk_daily_l: 22,
    mpesa_active: true,
    months_on_platform: 11,
    vet_visits_6mo: 2,
    training_modules_completed: 6,
    last_advisory: "2026-06-15",
    priority_flag: "ROUTINE"
  }),
  (f5:Farmer {
    id: "F005",
    name: "Jepchirchir Sang",
    phone: "+254712000005",
    region_id: "R002",
    county: "Uasin Gishu",
    cows: 6,
    breed: "Friesian",
    milk_daily_l: 35,
    mpesa_active: true,
    months_on_platform: 18,
    vet_visits_6mo: 4,
    training_modules_completed: 9,
    last_advisory: "2026-06-20",
    priority_flag: "ROUTINE"
  });

// Link farmers to regions
MATCH (f:Farmer {id:"F001"}),(r:Region {id:"R001"}) CREATE (f)-[:FARMS_IN]->(r);
MATCH (f:Farmer {id:"F002"}),(r:Region {id:"R002"}) CREATE (f)-[:FARMS_IN]->(r);
MATCH (f:Farmer {id:"F003"}),(r:Region {id:"R004"}) CREATE (f)-[:FARMS_IN]->(r);
MATCH (f:Farmer {id:"F004"}),(r:Region {id:"R001"}) CREATE (f)-[:FARMS_IN]->(r);
MATCH (f:Farmer {id:"F005"}),(r:Region {id:"R002"}) CREATE (f)-[:FARMS_IN]->(r);

// Link agents to farmers
MATCH (a:ExtensionAgent {id:"A001"}),(f:Farmer {id:"F001"}) CREATE (a)-[:MANAGES]->(f);
MATCH (a:ExtensionAgent {id:"A001"}),(f:Farmer {id:"F004"}) CREATE (a)-[:MANAGES]->(f);
MATCH (a:ExtensionAgent {id:"A002"}),(f:Farmer {id:"F002"}) CREATE (a)-[:MANAGES]->(f);
MATCH (a:ExtensionAgent {id:"A002"}),(f:Farmer {id:"F005"}) CREATE (a)-[:MANAGES]->(f);

// ── STEP 10: VERIFY SEED ──────────────────────────────────────────────
// Run these checks after seeding to confirm the graph loaded correctly:

// MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY type;
// Expected: Disease:10, Symptom:28, Region:8, MilkPrice:8, Farmer:5, ExtensionAgent:2

// MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count;
// Expected: INDICATES:~35, HAS_PRICE:8, FARMS_IN:5, MANAGES:4, SERVES:2, HAS_CLIMATE:1

// MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
// WHERE s.name IN ["high fever", "swollen lymph nodes"]
// RETURN d.name, SUM(r.weight) AS score ORDER BY score DESC LIMIT 3;
// Expected: East Coast Fever scores highest
