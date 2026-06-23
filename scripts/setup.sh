#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# CowSense AI — One-Command Setup Script
# scripts/setup.sh
#
# Run once on Day 1 after cloning the repo:
#   chmod +x scripts/setup.sh && ./scripts/setup.sh
#
# Works on: Ubuntu 22.04+, macOS 13+, WSL2
# ═══════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
GOLD='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}🐄  CowSense AI — Setup${NC}"
echo -e "${GOLD}    Kenya AI Challenge 2026 | Mercy Corps AgriFin Track${NC}"
echo ""

# ── Check Python version ──────────────────────────────────────────
echo "  Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED="3.11"
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"; then
  echo -e "  ${GREEN}✅  Python $PYTHON_VERSION${NC}"
else
  echo -e "  ${RED}❌  Python 3.11+ required. You have $PYTHON_VERSION${NC}"
  exit 1
fi

# ── Create virtual environment ────────────────────────────────────
echo ""
echo "  Creating virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "  ${GREEN}✅  Virtual environment created${NC}"
else
  echo -e "  ${GREEN}✅  Virtual environment already exists${NC}"
fi

# ── Activate venv ─────────────────────────────────────────────────
source venv/bin/activate

# ── Install dependencies ──────────────────────────────────────────
echo ""
echo "  Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "  ${GREEN}✅  Dependencies installed${NC}"

# ── Set up .env ───────────────────────────────────────────────────
echo ""
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "  ${GOLD}⚠️   .env created from .env.example${NC}"
  echo -e "  ${GOLD}    → Edit .env and add your API keys before continuing${NC}"
else
  echo -e "  ${GREEN}✅  .env already exists${NC}"
fi

# ── Verify structure ──────────────────────────────────────────────
echo ""
echo "  Checking project structure..."
REQUIRED_FILES=(
  "app/main.py"
  "app/agent.py"
  "app/config.py"
  "neo4j/seed.cypher"
  "neo4j/schema.cypher"
  "prompts/health_system.txt"
  "prompts/market_system.txt"
  "prompts/credit_system.txt"
  "tests/demo_test.py"
  "tests/demo_inputs.json"
)
ALL_OK=true
for f in "${REQUIRED_FILES[@]}"; do
  if [ -f "$f" ]; then
    echo -e "  ${GREEN}✅  $f${NC}"
  else
    echo -e "  ${RED}❌  Missing: $f${NC}"
    ALL_OK=false
  fi
done

if [ "$ALL_OK" = false ]; then
  echo ""
  echo -e "  ${RED}Some files are missing. Re-clone the repo and try again.${NC}"
  exit 1
fi

# ── Final instructions ────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅  Setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Edit .env with your API keys"
echo "     - ANTHROPIC_API_KEY  → console.anthropic.com"
echo "     - FEATHERLESS_API_KEY → featherless.ai"
echo "     - NEO4J_URI + NEO4J_PASSWORD → console.neo4j.io"
echo "     - AT_API_KEY → africastalking.com"
echo ""
echo "  2. Seed Neo4j knowledge graph:"
echo "     → Open Neo4j Browser → paste neo4j/schema.cypher → run"
echo "     → Paste neo4j/seed.cypher → run"
echo ""
echo "  3. Check all connections:"
echo "     python scripts/check_env.py"
echo ""
echo "  4. Start the server:"
echo "     uvicorn app.main:app --reload --port 8000"
echo ""
echo "  5. Test everything:"
echo "     python tests/demo_test.py"
echo ""
echo "  6. View API docs:"
echo "     open http://localhost:8000/docs"
echo ""
echo -e "  ${GOLD}🐄  Let's build. — CowSense AI Team${NC}"
echo ""
