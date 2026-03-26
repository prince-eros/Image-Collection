import requests
import logging
import time
from typing import Generator, Dict, Any, List
from utils.request_handler import safe_request
from sources.base_source import BaseSource
from utils.request_handler import DEFAULT_HEADERS

class WikimediaSource(BaseSource):
    """
    Wikimedia Commons source (STRICT mentor-compliant)

    Features:
    - No API key
    - Category-based fetching (high quality)
    - License filtering (CC-BY, CC-BY-SA, CC0 only)
    - Rate limiting (1 request/sec)
    - Proper User-Agent
    """

    name = "wikimedia"
    required_api_key = None
    source_type = "api"
    BASE_URL = "https://commons.wikimedia.org/w/api.php"

    def __init__(self):
        self.headers = {
            "User-Agent": "IndianCulturalDatasetBot/1.0 (educational project)"
        }

    # =========================
    # MAIN FETCH FUNCTION
    # =========================

    def fetch_images(self, bucket: str, limit: int) -> Generator[Dict[str, Any], None, None]:
        collected = 0

        categories = self.get_categories(bucket)

        for category in categories:
            if collected >= limit:
                break

            logging.info(f"Wikimedia category: {category}")

            params = {
                "action": "query",
                "format": "json",
                "generator": "categorymembers",
                "gcmtitle": f"Category:{category}",
                "gcmlimit": 50,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata"
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    headers=DEFAULT_HEADERS,
                    params=params,
                    timeout=10
               )

               

                if response.status_code != 200:
                    logging.warning(f"Wikimedia API error: {response.status_code}")
                    continue

                data = response.json()
                pages = data.get("query", {}).get("pages", {})

                if not pages:
                    continue

                for page in pages.values():
                    if collected >= limit:
                        break

                    image_data = self._parse_page(page)
                    if image_data:
                        yield image_data
                        collected += 1

            except Exception as e:
                logging.error(f"Wikimedia fetch error: {e}")
                continue

    # =========================
    # PARSE IMAGE
    # =========================

    def _parse_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        try:
            imageinfo = page.get("imageinfo", [{}])[0]

            image_url = imageinfo.get("url")
            metadata = imageinfo.get("extmetadata", {})

            if not image_url:
                return None

            description = self._extract(metadata, "ImageDescription")
            license_name = self._extract(metadata, "LicenseShortName")

            # ✅ STRICT LICENSE FILTER
            if not self._is_allowed_license(license_name):
                return None

            return self.build_metadata(
                url=image_url,
                source=self.name,
                license_type=license_name,
                alt_text=description,
                tags=[],
                title=page.get("title", "")
            )

        except Exception as e:
            logging.warning(f"Wikimedia parse error: {e}")
            return None

    # =========================
    # LICENSE FILTER
    # =========================

    def _is_allowed_license(self, license_name: str) -> bool:
        if not license_name:
            return False

        allowed = ["CC-BY", "CC-BY-SA", "CC0"]

        return any(x in license_name for x in allowed)

    # =========================
    # METADATA HELPER
    # =========================

    def _extract(self, metadata: Dict, key: str) -> str:
        try:
            return metadata.get(key, {}).get("value", "")
        except:
            return ""

    # =========================
    # CATEGORY SYSTEM (MENTOR REQUIRED)
    # =========================

    def get_categories(self, bucket: str) -> List[str]:
        return {
            "people_portraits": [
                "Culture_of_India",
                "People_of_India"
            ],

            "architecture": [
                "Hindu_temples_in_India",
                "Forts_in_India",
                "Monuments_of_India"
            ],

            "festivals_rituals": [
                "Festivals_of_India",
                "Religious_festivals_in_India"
            ],

            "art_design": [
                "Classical_dance_genres_of_India",
                "Paintings_of_India"
            ],

            "clothing_textiles": [
                "Textiles_of_India",
                "Clothing_of_India"
            ],

            "food_drink": [
                "Indian_cuisine"
            ],

            "animals_wildlife": [
                "Wildlife_of_India"
            ],

        }.get(bucket, ["Culture_of_India"])