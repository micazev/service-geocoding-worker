import requests
import unicodedata
import re
import logging
from typing import Optional, Tuple

from utils.analytics_utils import ScraperAnalytics

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self, mapbox_token: str):
        self.mapbox_token = mapbox_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        self.analytics = ScraperAnalytics("geocoding_service")
        self.geocoding_metrics = {
            "state_distribution": {},
            "geocoded_by_state": {},
            "failed_by_state": {},
            "error_types": {},
            "address_length_distribution": {
                "short": 0,
                "medium": 0,
                "long": 0,
                "very_long": 0,
            },
        }

    def _preprocess_address(self, address: str) -> str:
        txt = (
            unicodedata.normalize("NFKD", address)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        txt = txt.upper()
        txt = re.sub(r"[^\w\s,.-]", " ", txt)
        txt = re.sub(r"\s+", " ", txt)

        patterns = [
            r"APT\.?\s*\d+.*?(?=,|$)",
            r"BLOCO\s*\d+.*?(?=,|$)",
            r"TORRE\s*\d+.*?(?=,|$)",
            r"\(.*?\)",
            # add others as needed
        ]
        for pat in patterns:
            txt = re.sub(pat, "", txt, flags=re.IGNORECASE)

        txt = re.sub(r",\s*,", ",", txt)
        txt = re.sub(r"^\s*,|,\s*$", "", txt)
        txt = re.sub(r"\s+", " ", txt)
        return txt.strip()

    def _categorize_address_length(self, addr: str) -> str:
        l = len(addr)
        if l <= 50:
            return "short"
        if l <= 100:
            return "medium"
        if l <= 150:
            return "long"
        return "very_long"

    def geocode_address(
        self, address: str, state: str
    ) -> Optional[Tuple[float, float]]:
        try:
            proc = self._preprocess_address(address)
            cat = self._categorize_address_length(proc)
            self.geocoding_metrics["address_length_distribution"][cat] += 1
            self.geocoding_metrics["state_distribution"][state] = (
                self.geocoding_metrics["state_distribution"].get(state, 0) + 1
            )

            query = requests.utils.quote(f"{proc}, {state}, Brasil")
            url = f"{self.base_url}/{query}.json"
            params = {"access_token": self.mapbox_token, "country": "br", "limit": 1}

            self.analytics.increment_requests()
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("features"):
                coords = data["features"][0]["center"]
                self.analytics.increment_success()
                self.geocoding_metrics["geocoded_by_state"][state] = (
                    self.geocoding_metrics["geocoded_by_state"].get(state, 0) + 1
                )
                return coords[0], coords[1]

            logger.warning(f"No coords for {proc}")
            self.analytics.increment_failure()
            self.geocoding_metrics["failed_by_state"][state] = (
                self.geocoding_metrics["failed_by_state"].get(state, 0) + 1
            )
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error geocoding {proc}: {e}")
            self.analytics.increment_failure()
            self.geocoding_metrics["error_types"][type(e).__name__] = (
                self.geocoding_metrics["error_types"].get(type(e).__name__, 0) + 1
            )
            self.analytics.add_error("network_error", str(e))
            return None

        except Exception as e:
            logger.error(f"Error geocoding {proc}: {e}")
            self.analytics.increment_failure()
            self.geocoding_metrics["error_types"][type(e).__name__] = (
                self.geocoding_metrics["error_types"].get(type(e).__name__, 0) + 1
            )
            self.analytics.add_error("geocoding_error", str(e))
            return None
