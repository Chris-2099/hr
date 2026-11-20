"""Exports every table in the local database to one CSV file per table,
for Power BI to read directly.

    python -m src.export_powerbi                    # writes to ./powerbi_export/
    python -m src.export_powerbi --output-dir PATH   # writes somewhere else

Each table is loaded into a pandas DataFrame (via SQLAlchemy's engine) and
written out as CSV - the simplest format Power BI can consume with no
driver install: "Get Data > Folder" against the output directory picks up
every table at once, or "Get Data > Text/CSV" for one at a time. Re-run
this after src/api/jobvite.py / src/api/dayforce.py (or
src/seed/seed_data.py) brings in new data and
point Power BI's refresh at the same output directory.

CSV, not Parquet, is the deliberate choice here: it needs no extra Power BI
connector/driver and is trivial to open and sanity-check by hand - the
tables involved are a few thousand rows at most (see README's "Known
simplifications"), so Parquet's size/type-fidelity advantages don't matter
at this scale.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect

from src.core.database import engine

logger = logging.getLogger(__name__)


def export_tables(output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inspector = inspect(engine)
    exported = []
    with engine.connect() as conn:
        for table_name in sorted(inspector.get_table_names()):
            df = pd.read_sql_table(table_name, conn)
            df.to_csv(output_dir / f"{table_name}.csv", index=False)
            exported.append(table_name)
    return exported


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--output-dir",
        default="powerbi_export",
        help="Directory to write one CSV per table into (default: ./powerbi_export)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    output_dir = Path(args.output_dir)
    exported = export_tables(output_dir)
    logger.info("Exported %d table(s) to %s:", len(exported), output_dir.resolve())
    for name in exported:
        logger.info("  - %s.csv", name)


if __name__ == "__main__":
    main()
