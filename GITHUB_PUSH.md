# GitHub Push Guide
## CowSense AI — Exact commands, no guessing

---

## SITUATION: You already pushed a first version

Your first push had files inside a `cowsense_prototype/` folder.
The new repo has the correct flat structure (files at root level).
Here's how to update cleanly.

---

## STEP 1 — Unzip the new repo

```bash
# On your computer, unzip cowsense-ai-github.zip
unzip cowsense-ai-github.zip
cd cowsense-ai
```

---

## STEP 2 — Check if .env is clean (CRITICAL)

```bash
# Must return NOTHING — if it shows keys, fix before pushing
grep -r "sk-ant\|password\|Bearer\|neo4j+s://" . \
  --include="*.py" --include="*.yaml" --include="*.md" \
  --exclude-dir=".git"
```

---

## STEP 3A — If your existing GitHub repo should be updated

```bash
# Clone your existing repo first
git clone https://github.com/[YOUR-USERNAME]/cowsense-ai.git existing-repo
cd existing-repo

# Copy all new files into it (overwrites old versions)
cp -r /path/to/new/cowsense-ai/* .
cp -r /path/to/new/cowsense-ai/.gitignore .
cp -r /path/to/new/cowsense-ai/.env.example .

# Stage everything
git add .

# Check what changed
git status

# Commit
git commit -m "feat: GraphRAG agent, USSD handler, credit router, Render deploy"

# Push
git push origin main
```

---

## STEP 3B — If you want a fresh clean repo

```bash
# 1. Go to github.com → New repository
#    Name: cowsense-ai
#    Visibility: Public
#    Do NOT add README/gitignore (we have them)
#    Click Create repository

# 2. From inside the cowsense-ai folder:
cd cowsense-ai
git init
git add .
git commit -m "feat: CowSense AI — Kenya AI Challenge 2026"
git branch -M main
git remote add origin https://github.com/[YOUR-USERNAME]/cowsense-ai.git
git push -u origin main
```

---

## STEP 4 — Add your teammates as collaborators

```
GitHub → Your repo → Settings → Collaborators → Add people
Add: larry-github-username
Add: karol-github-username
Add: sandra-github-username
```

---

## STEP 5 — Verify the repo looks correct

Your repo should show these files at the ROOT level:
```
cowsense-ai/
├── README.md          ← shows up on GitHub homepage
├── .gitignore         ← hides .env
├── .env.example       ← shows what keys are needed (no values)
├── requirements.txt
├── Procfile
├── render.yaml
├── LICENSE
├── HACKATHON_DAY.md
├── PHASE2_SUBMISSION.md
├── app/
│   ├── main.py
│   ├── agent.py
│   ├── config.py
│   └── routers/
│       ├── health.py
│       ├── market.py
│       └── credit.py
├── neo4j/
│   ├── seed.cypher
│   └── schema.cypher
├── prompts/
├── tests/
├── docs/
├── scripts/
└── lovable/
```

---

## WHAT MUST NOT BE IN THE REPO

```bash
# Run this check — must return NOTHING
grep -r "sk-ant" .       --include="*.py" --include="*.yaml"
grep -r "neo4j+s://.*@" . --include="*.py" --include="*.env*" | grep -v ".example"
grep -r "Bearer " .      --include="*.py"
```

If anything shows up:
1. Remove it from the file
2. `git add . && git commit -m "fix: remove credentials"`
3. `git push`

---

## GITHUB LINK TO SUBMIT

```
https://github.com/[YOUR-USERNAME]/cowsense-ai
```

Make sure this URL:
✅ Opens without login
✅ Shows all files
✅ Has no .env file (only .env.example)
