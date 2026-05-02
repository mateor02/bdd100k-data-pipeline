from pydantic import ValidationError
import polars as pl
import logging
import time

logger = logging.getLogger(__name__)


def validator(df, model):
    start = time.time()

    clean = []
    quarantine = []
    for row in df.iter_rows(named=True):
        try:
            model(**row)
            clean.append(row)
            logger.info("Row passed validation")
        except ValidationError as err:
            quarantine.append(row)
            logger.warning(f"Row: {row['name']} failed validation: {err.errors()}")
    logger.info(
        f"{model.__name__} rows that passed validation: {len(clean)} | {model.__name__} rows that didn't pass validation: {len(quarantine)}"
    )

    clean_attributes, quarantine_attributes = pl.DataFrame(clean), pl.DataFrame(
        quarantine
    )

    elapsed = time.time() - start
    logger.info(f"validation completed in {elapsed:.2f}s")

    return clean_attributes, quarantine_attributes
