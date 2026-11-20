FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# The SQLite file lives in /data so it survives container restarts when
# mounted as a volume (see docker-compose.yaml).
ENV DATABASE_URL=sqlite:////data/hr_dashboard.db
RUN mkdir -p /data /export

# No long-running server - this is a one-shot pipeline container. Seed on
# first boot only (skip if the db file already has data), run each source's
# sync, then export to CSV for Power BI. Run on a schedule (cron, Task
# Scheduler, `docker compose run`, etc.) rather than left running.
CMD ["sh", "-c", "test -s /data/hr_dashboard.db || python -m src.seed.seed_data; python -m src.api.jobvite; python -m src.api.dayforce; python -m src.export_powerbi --output-dir /export"]
