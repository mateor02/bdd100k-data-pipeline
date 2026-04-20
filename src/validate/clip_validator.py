from models.clip import TimeOfDay, Weather, Scene, Clip
import polars as pl
from pydantic import ValidationError
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def validate():
    clean = []
    quarantine = []
    clips_df = pl.read_parquet("data/clips.parquet")
    for row in clips_df.iter_rows(named=True):
        try:
            Clip(**row)
            clean.append(row)
            logger.info("Row passed validation")
        except ValidationError as err:
            quarantine.append(row)
            logger.warning(f"Row: {row['name']} failed validation: {err.errors()}")
    logger.info(
        f"Clips that passed validation: {len(clean)} | Clips that didn't pass validation: {len(quarantine)}"
    )

    clean_attributes, quarantine_attributes = pl.DataFrame(clean), pl.DataFrame(
        quarantine
    )
    clean_path, quarantine_path = Path("data/clean.parquet"), Path(
        "data/quarantine.parquet"
    )
    clean_attributes.write_parquet(clean_path)
    quarantine_attributes.write_parquet(quarantine_path)

    return clean_attributes, quarantine_attributes


if __name__ == "__main__":
    import time

    start = time.time()
    validate()
    elapsed = time.time() - start
    logger.info(f"Validation completed in {elapsed:.2f}s")
