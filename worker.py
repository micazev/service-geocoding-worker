#!/usr/bin/env python3
import json
import logging
from pathlib import Path

from config import (
    MAPBOX_TOKEN,
    INPUT_DIR,
    PROCESSED_DIR,
    REPROCESS_DIR,
    LOG_LEVEL,
)
from service import LocationService
from utils.analytics_utils import ScraperAnalytics


def main():
    # Configure root logger
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger()

    # Initialize services
    svc = LocationService(MAPBOX_TOKEN)
    svc.analytics.start_scraping()

    # Ensure input directory exists
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPROCESS_DIR.mkdir(parents=True, exist_ok=True)


    # Scan for JSON files
    for path in INPUT_DIR.glob("*.json"):
        logger.info(f"Processing file: {path.name}")
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
            svc.analytics.increment_identified(len(items))
        except Exception as e:
            logger.error(f"Failed to read {path.name}: {e}")
            svc.analytics.add_error("file_read_error", str(e))
            continue

        updated = False
        failed_items = []
        for item in items:
            # Skip if already has valid coords
            if item.get("latitude") and item.get("longitude"):
                continue

            # Check required fields
            if not all(k in item for k in ("endereco", "localidade", "estado")):
                svc.analytics.add_error(
                    "missing_fields", f"Missing fields in item: {item}"
                )
                failed_items.append(item)
                continue

            attempts = [
                f"{item['endereco']}, {item['localidade']}",
                item["endereco"],
                item["localidade"],
            ]

            coords = None
            for addr in attempts:
                coords = svc.geocode_address(addr, item["estado"])
                if coords:
                    break

            if coords:
                item["longitude"], item["latitude"] = coords
                updated = True
                logger.info(f"Geocoded {addr} → {coords}")
            else:
                logger.warning(
                    f"Failed to geocode after attempts: {item['endereco']} / {item['localidade']}"
                )
                failed_items.append(item)

        if updated:
            path.write_text(
                json.dumps(items, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Updated file: {path.name}")

        if failed_items:
            repro_path = REPROCESS_DIR / f"reprocessar_{path.name}"
            repro_path.write_text(
                json.dumps(failed_items, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info(
                f"Saved {len(failed_items)} items for reprocessing in {repro_path}"
            )

        # Move processed file to processed directory
        dest = PROCESSED_DIR / path.name
        try:
            path.rename(dest)
            logger.info(f"Moved {path.name} to {dest}")
        except Exception as e:
            logger.error(f"Failed to move {path.name}: {e}")

    svc.analytics.end_scraping()


if __name__ == "__main__":
    main()
