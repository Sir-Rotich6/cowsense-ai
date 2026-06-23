// ═══════════════════════════════════════════════════════════════════
// CowSense AI — Neo4j Schema: Constraints & Indexes
// Run BEFORE seed.cypher on a fresh Neo4j Aura instance
// ═══════════════════════════════════════════════════════════════════

// ── Uniqueness constraints ─────────────────────────────────────────
CREATE CONSTRAINT disease_id_unique   IF NOT EXISTS FOR (d:Disease)        REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT symptom_id_unique   IF NOT EXISTS FOR (s:Symptom)        REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT farmer_id_unique    IF NOT EXISTS FOR (f:Farmer)         REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT region_id_unique    IF NOT EXISTS FOR (r:Region)         REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT agent_id_unique     IF NOT EXISTS FOR (a:ExtensionAgent) REQUIRE a.id IS UNIQUE;

// ── Indexes for frequent lookups ───────────────────────────────────
CREATE INDEX symptom_name_index   IF NOT EXISTS FOR (s:Symptom)  ON (s.name);
CREATE INDEX farmer_phone_index   IF NOT EXISTS FOR (f:Farmer)   ON (f.phone);
CREATE INDEX region_name_index    IF NOT EXISTS FOR (r:Region)   ON (r.name);
CREATE INDEX disease_sev_index    IF NOT EXISTS FOR (d:Disease)  ON (d.severity);
CREATE INDEX farmer_region_index  IF NOT EXISTS FOR (f:Farmer)   ON (f.region_id);
CREATE INDEX price_region_index   IF NOT EXISTS FOR (p:MilkPrice) ON (p.region_id);

// ── Full-text index for symptom fuzzy matching ────────────────────
CREATE FULLTEXT INDEX symptom_fulltext IF NOT EXISTS
FOR (s:Symptom) ON EACH [s.name, s.category];
