#!/usr/bin/env python3
import json
import logging
from pathlib import Path

from config import MAPBOX_TOKEN, INPUT_DIR, LOG_LEVEL
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
        for item in items:
            # Skip if already has valid coords
            if item.get("latitude") and item.get("longitude"):
                continue

            # Build address
            if all(k in item for k in ("endereco", "localidade", "estado")):
                full_address = f"{item['endereco']}, {item['localidade']}"
                coords = svc.geocode_address(full_address, item["estado"])
                if coords:
                    item["longitude"], item["latitude"] = coords
                    updated = True
                    logger.info(f"Geocoded {full_address} → {coords}")
                else:
                    logger.warning(f"Failed to geocode: {full_address}")
            else:
                svc.analytics.add_error(
                    "missing_fields", f"Missing fields in item: {item}"
                )

        if updated:
            path.write_text(
                json.dumps(items, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Updated file: {path.name}")

    svc.analytics.end_scraping()


if __name__ == "__main__":
    main()