"""
CowSense AI — Embedding Generator
scripts/generate_embeddings.py

Generates vector embeddings for all Symptom nodes in Neo4j.
This makes GraphRAG work — semantic symptom matching instead of exact strings.

Model: sentence-transformers/all-MiniLM-L6-v2
  - 384 dimensions
  - Runs locally on CPU (no API cost)
  - ~80MB download on first run

Run ONCE after seeding Neo4j, before starting the server:
  python scripts/generate_embeddings.py

What it does:
  1. Loads all Symptom nodes from Neo4j
  2. Builds a rich text string: name + description + lay_terms
  3. Generates a 384-dimension embedding for each
  4. Stores the embedding back into the Symptom node as s.embedding

After this, the vector index (schema.cypher) becomes usable for
semantic symptom matching in the GraphRAG query.

Owns: Enock Rotich (Team Lead / AI Engineer)
Run on: Day 1 (June 22) after seed.cypher
"""

import os
import sys
import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "cowsense2026")

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"


def load_model():
    """Load sentence-transformers model. Downloads ~80MB on first run."""
    print(f"  Loading embedding model (all-MiniLM-L6-v2)...")
    print(f"  {YELLOW}First run downloads ~80MB — normal.{RESET}")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print(f"  {GREEN}✅ Model loaded{RESET}")
    return model


def build_symptom_text(symptom: dict) -> str:
    """
    Build a rich text string from symptom fields.
    The richer this string, the better semantic matching works.
    """
    parts = [symptom.get("name", "")]
    desc = symptom.get("description", "")
    lay  = symptom.get("lay_terms", "")
    cat  = symptom.get("category", "")
    if desc:  parts.append(desc)
    if lay:   parts.append(lay)
    if cat:   parts.append(f"category: {cat}")
    return ". ".join(p.strip() for p in parts if p.strip())


def fetch_symptoms(driver) -> list[dict]:
    """Fetch all Symptom nodes from Neo4j."""
    with driver.session() as session:
        result = session.run("""
            MATCH (s:Symptom)
            RETURN s.id AS id, s.name AS name,
                   coalesce(s.description, '') AS description,
                   coalesce(s.lay_terms, '')   AS lay_terms,
                   coalesce(s.category, '')    AS category
            ORDER BY s.id
        """)
        return [dict(r) for r in result]


def store_embeddings(driver, embeddings: list[dict]):
    """Write embedding vectors back to Neo4j Symptom nodes."""
    with driver.session() as session:
        for item in embeddings:
            session.run("""
                MATCH (s:Symptom {id: $id})
                CALL db.create.setNodeVectorProperty(s, 'embedding', $embedding)
            """, id=item["id"], embedding=item["embedding"])


def main():
    print(f"\n{GREEN}🐄  CowSense AI — Embedding Generator{RESET}")
    print(f"{'─'*55}")

    # ── Connect to Neo4j ──────────────────────────────────────────
    print(f"\n  Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print(f"  {GREEN}✅ Connected to Neo4j{RESET}")
    except Exception as e:
        print(f"  {RED}❌ Neo4j connection failed: {e}{RESET}")
        print(f"  Make sure Neo4j is running and seed.cypher has been applied.")
        sys.exit(1)

    # ── Fetch symptoms ────────────────────────────────────────────
    symptoms = fetch_symptoms(driver)
    if not symptoms:
        print(f"  {RED}❌ No Symptom nodes found. Run neo4j/seed.cypher first.{RESET}")
        sys.exit(1)
    print(f"\n  Found {len(symptoms)} symptom nodes to embed")

    # ── Load model ────────────────────────────────────────────────
    model = load_model()

    # ── Generate embeddings ───────────────────────────────────────
    print(f"\n  Generating embeddings...")
    texts = [build_symptom_text(s) for s in symptoms]

    # Show what's being embedded
    for i, (sym, text) in enumerate(zip(symptoms, texts)):
        print(f"  [{i+1:02d}] {sym['id']}: {text[:70]}...")

    # Batch encode
    embeddings_matrix = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True   # normalize for cosine similarity
    )

    print(f"  {GREEN}✅ Generated {len(embeddings_matrix)} embeddings "
          f"(shape: {embeddings_matrix.shape}){RESET}")

    # ── Store in Neo4j ────────────────────────────────────────────
    print(f"\n  Storing embeddings in Neo4j...")
    batch = [
        {"id": sym["id"], "embedding": emb.tolist()}
        for sym, emb in zip(symptoms, embeddings_matrix)
    ]
    store_embeddings(driver, batch)
    driver.close()

    print(f"  {GREEN}✅ All {len(batch)} embeddings stored{RESET}")

    # ── Verify ────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    print(f"  {GREEN}✅ Done! GraphRAG vector search is now active.{RESET}")
    print(f"\n  Verify in Neo4j Browser:")
    print(f"  MATCH (s:Symptom) WHERE s.embedding IS NOT NULL")
    print(f"  RETURN count(s) AS embedded_symptoms;")
    print(f"  Expected: {len(batch)}")
    print(f"\n  Test semantic search:")
    print(f"  CALL db.index.vector.queryNodes('symptom_embeddings', 3, <embedding>)")
    print(f"  YIELD node, score RETURN node.name, score;\n")


if __name__ == "__main__":
    main()
