#!/usr/bin/env bash
# Runs backend + frontend together for local dev, no Docker needed.
set -e

cd "$(dirname "$0")"

# --- backend ---
cd backend
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
[ -f hr_dashboard.db ] || python -m src.seed.seed_data
uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# --- frontend ---
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM

echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
wait
