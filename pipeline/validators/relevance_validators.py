import logging
from typing import Dict, List


class RelevanceValidator:
    """
    Relevance Validator:
    - Uses detailed query phrases (your source queries)
    - Supports phrase + partial matching
    """

    def __init__(self):
        self.bucket_keywords = self._build_keywords()

    # =========================
    # MAIN FUNCTION
    # =========================

    def is_relevant(self, bucket: str, metadata: Dict) -> (bool, str):
        text = self._extract_text(metadata)

        if not text:
            return True, "no_metadata"  # don't reject blindly

        keywords = self.bucket_keywords.get(bucket, [])

        score = 0

        for keyword in keywords:
            keyword = keyword.lower()

            # 🔥 full phrase match (strong)
            if keyword in text:
                score += 2
            else:
                # 🔥 partial word match
                words = keyword.split()
                if any(w in text for w in words):
                    score += 1

        # 🔥 decision threshold
        if score >= 2:
            return True, "relevant"

        return False, "irrelevant"

    # =========================
    # TEXT EXTRACTION
    # =========================

    def _extract_text(self, metadata: Dict) -> str:
        parts = []

        parts.append(metadata.get("alt_text", ""))
        parts.append(metadata.get("title", ""))

        tags = metadata.get("tags", [])
        if isinstance(tags, list):
            parts.extend(tags)

        return " ".join(parts).lower()

    # =========================
    # KEYWORDS (YOUR QUERIES)
    # =========================

    def _build_keywords(self) -> Dict[str, List[str]]:
        return {

            "people_portraits": [
                "indian woman portrait traditional saree",
                "indian elderly man face close-up wrinkles",
                "rajasthani people traditional attire portrait",
                "tamil woman face jasmine flowers portrait",
                "indian tribal people portrait cultural dress",
                "indian farmer face rural portrait",
                "indian classical dancer portrait bharatanatyam",
                "indian child portrait village life",
                "indian man turban portrait rajasthan",
                "person", "face", "portrait"
            ],

            "clothing_textiles": [
                "indian saree silk banarasi fabric",
                "phulkari embroidery punjab textile",
                "handloom weaving india traditional",
                "indian bridal lehenga embroidery close-up",
                "block print fabric rajasthan textile",
                "kanjeevaram silk saree detail",
                "indian textile pattern macro shot",
                "traditional shawl weaving kashmir",
                "indian jewelry textile combination",
                "saree", "fabric", "textile"
            ],

            "architecture": [
                "hindu temple architecture carvings india",
                "rajasthan fort sandstone architecture",
                "mughal monument taj mahal detail",
                "indian palace interior heritage",
                "mosque architecture india dome minaret",
                "ancient temple stone sculpture india",
                "stepwell architecture india",
                "south indian temple gopuram",
                "indian heritage building ruins",
                "temple", "monument", "building"
            ],

            "landscape_nature": [
                "himalaya mountains india snow landscape",
                "kerala backwaters boat scenic view",
                "thar desert dunes rajasthan",
                "indian forest jungle greenery",
                "tea plantation hills india",
                "river ganga sunrise landscape",
                "waterfall india nature scenic",
                "coastal beach india sunset",
                "monsoon rain landscape india",
                "nature", "landscape"
            ],

            "urban_street": [
                "mumbai street market crowd",
                "delhi bazaar shops busy street",
                "indian rickshaw traffic road",
                "street vendors india market",
                "night street india lights",
                "urban india metro station",
                "street food stall india",
                "crowded railway station india",
                "old city narrow streets india",
                "street", "market", "city"
            ],

            "rural_village": [
                "indian village mud house rural life",
                "paddy field farmer working india",
                "rural women carrying water pots",
                "bullock cart village india",
                "village children playing india",
                "traditional farming india agriculture",
                "sunset village landscape india",
                "hut house countryside india",
                "rural market village india",
                "village", "rural", "farmer"
            ],

            "food_drink": [
                "indian thali traditional meal",
                "masala dosa south indian food",
                "street food chaat india",
                "biryani rice indian cuisine",
                "chai tea cup india",
                "indian sweets laddu jalebi",
                "spices market india colorful",
                "tandoori food indian grill",
                "home cooked indian meal",
                "food", "dish", "meal"
            ],

            "festivals_rituals": [
                "holi festival colors celebration india",
                "diwali diya lights night",
                "indian wedding ceremony bride groom",
                "durga puja idol festival",
                "ganesh chaturthi celebration",
                "classical dance performance india",
                "temple puja ritual india",
                "fireworks festival india night",
                "traditional festival procession india",
                "festival", "celebration", "ritual"
            ],

            "objects_artifacts": [
                "indian brass handicraft artifact",
                "sitar instrument classical music",
                "indian pottery clay handmade",
                "wood carving craft india",
                "traditional mask indian art",
                "metal sculpture india artifact",
                "handmade basket weaving india",
                "antique artifact india museum",
                "decorative item indian culture",
                "artifact", "object", "craft"
            ],

            "animals_wildlife": [
                "bengal tiger jungle india",
                "indian elephant forest wildlife",
                "peacock feathers india national bird",
                "cow rural india animal",
                "monkey temple india wildlife",
                "camel desert rajasthan",
                "bird wildlife india forest",
                "leopard india jungle",
                "animal sanctuary india wildlife",
                "animal", "wildlife"
            ],

            "art_design": [
                "madhubani painting traditional art",
                "warli art tribal painting",
                "rangoli design floor pattern",
                "indian mural wall painting",
                "folk art india colorful design",
                "canvas painting indian theme",
                "temple art sculpture design",
                "miniature painting india",
                "traditional art workshop india",
                "art", "design", "painting"
            ],

            "abstract_texture": [
                "indian textile pattern block print",
                "kolam design geometric floor",
                "jali stone lattice pattern",
                "fabric texture macro india",
                "tile pattern indian design",
                "henna mehndi pattern close-up",
                "woven fabric texture india",
                "carpet pattern indian textile",
                "traditional motif indian design",
                "pattern", "texture"
            ],
        }