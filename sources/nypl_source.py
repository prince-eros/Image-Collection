import requests
import logging
from typing import Generator, Dict, Any, List
from utils.request_handler import DEFAULT_HEADERS
from sources.base_source import BaseSource
from pipeline.config import Config


class NYPLSource(BaseSource):
    """
    NYPL Digital Collections API
    - Public domain rich dataset
    """

    name = "nypl"
    required_api_key = "NYPL_API_KEY"
    source_type = "api" 
    BASE_URL = "https://api.repo.nypl.org/api/v1/items/search"

    def __init__(self):
        self.api_key = Config.get_api_key("nypl")

        self.headers = {
            "Authorization": f"Token {self.api_key}"
        }

    # =========================
    # MAIN FETCH
    # =========================

    def fetch_images(self, bucket: str, limit: int) -> Generator[Dict[str, Any], None, None]:
        collected = 0
        queries = self.get_queries(bucket)

        for query in queries:
            if collected >= limit:
                break

            params = {
                "q": query,
                "publicDomainOnly": "true"
            }

            try:
                headers = DEFAULT_HEADERS.copy()
                headers.update(self.headers)
                
                response = requests.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                if response.status_code != 200:
                    logging.warning(f"NYPL API error: {response.status_code}")
                    continue

                data = response.json()
                items = data.get("nyplAPI", {}).get("response", {}).get("docs", [])

                for item in items:
                    if collected >= limit:
                        break

                    image_data = self._parse_item(item)
                    if image_data:
                        yield image_data
                        collected += 1

            except Exception as e:
                logging.error(f"NYPL fetch error: {e}")
                continue

    # =========================
    # PARSE
    # =========================

    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        try:
            image_id = item.get("uuid")

            if not image_id:
                return None

            # Construct image URL
            image_url = f"https://images.nypl.org/index.php?id={image_id}&t=w"

            title = item.get("title", "")

            return self.build_metadata(
                url=image_url,
                source=self.name,
                license_type="public-domain",
                alt_text=title,
                tags=[],
                title=title
            )

        except Exception as e:
            logging.warning(f"NYPL parse error: {e}")
            return None

    # =========================
    # QUERIES
    # =========================

    def get_queries(self, bucket: str) -> List[str]:
        return {
            "people_portraits": [
                "Indian woman portrait traditional saree",
                "Indian elderly man face close-up wrinkles",
                "Rajasthani people traditional attire portrait",
                "Tamil woman face jasmine flowers portrait",
                "Indian tribal people portrait cultural dress",
                "Indian farmer face rural portrait",
                "Indian classical dancer portrait Bharatanatyam",
                "Indian child portrait village life",
                "Indian man turban portrait Rajasthan"
            ],

            "clothing_textiles": [
                "Indian saree silk Banarasi fabric",
                "phulkari embroidery Punjab textile",
                "handloom weaving India traditional",
                "Indian bridal lehenga embroidery close-up",
                "block print fabric Rajasthan textile",
                "kanjeevaram silk saree detail",
                "Indian textile pattern macro shot",
                "traditional shawl weaving Kashmir",
                "Indian jewelry textile combination"
            ],

            "architecture": [
                "Hindu temple architecture carvings India",
                "Rajasthan fort sandstone architecture",
                "Mughal monument Taj Mahal detail",
                "Indian palace interior heritage",
                "mosque architecture India dome minaret",
                "ancient temple stone sculpture India",
                "stepwell architecture India",
                "South Indian temple gopuram",
                "Indian heritage building ruins"
            ],

            "landscape_nature": [
                "Himalaya mountains India snow landscape",
                "Kerala backwaters boat scenic view",
                "Thar desert dunes Rajasthan",
                "Indian forest jungle greenery",
                "tea plantation hills India",
                "river Ganga sunrise landscape",
                "waterfall India nature scenic",
                "coastal beach India sunset",
                "monsoon rain landscape India"
            ],

            "urban_street": [
                "Mumbai street market crowd",
                "Delhi bazaar shops busy street",
                "Indian rickshaw traffic road",
                "street vendors India market",
                "night street India lights",
                "urban India metro station",
                "street food stall India",
                "crowded railway station India",
                "old city narrow streets India"
            ],

            "rural_village": [
                "Indian village mud house rural life",
                "paddy field farmer working India",
                "rural women carrying water pots",
                "bullock cart village India",
                "village children playing India",
                "traditional farming India agriculture",
                "sunset village landscape India",
                "hut house countryside India",
                "rural market village India"
            ],

            "food_drink": [
                "Indian thali traditional meal",
                "masala dosa south Indian food",
                "street food chaat India",
                "biryani rice Indian cuisine",
                "chai tea cup India",
                "Indian sweets laddu jalebi",
                "spices market India colorful",
                "tandoori food Indian grill",
                "home cooked Indian meal"
            ],

            "festivals_rituals": [
                "Holi festival colors celebration India",
                "Diwali diya lights night",
                "Indian wedding ceremony bride groom",
                "Durga Puja idol festival",
                "Ganesh Chaturthi celebration",
                "classical dance performance India",
                "temple puja ritual India",
                "fireworks festival India night",
                "traditional festival procession India"
            ],

            "objects_artifacts": [
                "Indian brass handicraft artifact",
                "sitar instrument classical music",
                "Indian pottery clay handmade",
                "wood carving craft India",
                "traditional mask Indian art",
                "metal sculpture India artifact",
                "handmade basket weaving India",
                "antique artifact India museum",
                "decorative item Indian culture"
            ],

            "animals_wildlife": [
                "Bengal tiger jungle India",
                "Indian elephant forest wildlife",
                "peacock feathers India national bird",
                "cow rural India animal",
                "monkey temple India wildlife",
                "camel desert Rajasthan",
                "bird wildlife India forest",
                "leopard India jungle",
                "animal sanctuary India wildlife"
            ],

            "art_design": [
                "Madhubani painting traditional art",
                "Warli art tribal painting",
                "rangoli design floor pattern",
                "Indian mural wall painting",
                "folk art India colorful design",
                "canvas painting Indian theme",
                "temple art sculpture design",
                "miniature painting India",
                "traditional art workshop India"
            ],

            "abstract_texture": [
                "Indian textile pattern block print",
                "kolam design geometric floor",
                "jali stone lattice pattern",
                "fabric texture macro India",
                "tile pattern Indian design",
                "henna mehndi pattern close-up",
                "woven fabric texture India",
                "carpet pattern Indian textile",
                "traditional motif Indian design"
            ],
        }.get(bucket, [bucket])