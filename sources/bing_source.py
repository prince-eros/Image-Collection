import os
import logging
from typing import Generator, Dict, Any, List

from icrawler.builtin import BingImageCrawler

from sources.base_source import BaseSource


class BingSource(BaseSource):
    """
    Bing Image source (FALLBACK ONLY)

    Features:
    - Uses icrawler BingImageCrawler
    - Creative Commons filter enabled
    - No Google scraping
    """
    source_type = "scraper"
    name = "bing"
    required_api_key = None

    def __init__(self):
        self.temp_dir = "data/raw/bing_temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    # =========================
    # MAIN FETCH FUNCTION
    # =========================

    def fetch_images(self, bucket: str, limit: int) -> Generator[Dict[str, Any], None, None]:
        queries = self.get_queries(bucket)

        per_query_limit = max(1, limit // len(queries))
        collected = 0

        for query in queries:
            if collected >= limit:
                break

            logging.info(f"Bing scraping: {query}")

            try:
                crawler = BingImageCrawler(
                    storage={"root_dir": self.temp_dir}
                )

                crawler.crawl(
                    keyword=query,
                    max_num=per_query_limit,
                    filters={
                        "license": "commercial,modify"  # ✅ CC filter
                    }
                )

                # Read downloaded files
                files = os.listdir(self.temp_dir)

                for file_name in files:
                    if collected >= limit:
                        break

                    file_path = os.path.join(self.temp_dir, file_name)

                    if not os.path.isfile(file_path):
                        continue

                    yield self._build_metadata(file_path, query)

                    collected += 1

            except Exception as e:
                logging.error(f"Bing crawl error: {e}")
                continue

    # =========================
    # BUILD METADATA
    # =========================

    def _build_metadata(self, file_path: str, query: str) -> Dict[str, Any]:
        """
        Since Bing doesn't provide rich metadata,
        we generate basic metadata.
        """

        return self.build_metadata(
            url=file_path,  # local file path
            source=self.name,
            license_type="creative-commons",
            alt_text=query,
            tags=query.split(),
            title="bing_image"
        )

    # =========================
    # QUERY SYSTEM
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