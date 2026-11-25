FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# The SQLite file lives in /data so it survives container restarts when
# mounted as a volume (see docker-compose.yaml).
ENV DATABASE_URL=sqlite:////data/hr_dashboard.db
RUN mkdir -p /data /export

EXPOSE 8000

# Seed on first boot only (skip if the db file already has data), then
# serve. Ingestion (src.api.jobvite/dayforce) and the Power BI CSV export
# (src.export_powerbi) are separate, admin-triggered or scheduled steps -
# run them via `docker compose run --rm backend python -m src.api.jobvite`
# (etc.) or a cron entry, not as part of container startup.
CMD ["sh", "-c", "test -s /data/hr_dashboard.db || python -m src.seed.seed_data; uvicorn src.main:app --host 0.0.0.0 --port 8000"]
