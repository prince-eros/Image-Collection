import os
import logging
from PIL import Image
from typing import Dict

from utils.file_utils import ensure_dir


class ResolutionSorter:
    """
    Intelligent sorter with:
    - Fixed resolution ranges
    - Target distribution balancing
    - Controlled dataset creation
    """

    def __init__(self):
        self.base_dir = "data/sorted"

        # Counters per bucket
        self.counters: Dict[str, Dict[str, int]] = {}

        # Current counts per bucket/resolution
        self.current_counts: Dict[str, Dict[str, int]] = {}

        # Target counts per bucket/resolution
        self.target_counts: Dict[str, Dict[str, int]] = {}

    # =========================
    # INITIALIZE DISTRIBUTION
    # =========================

    def set_target(self, bucket: str, total_images: int):
        """
        Set 25% distribution per resolution
        """

        per_bucket = total_images // 4

        self.target_counts[bucket] = {
            "256": per_bucket,
            "512": per_bucket,
            "1024": per_bucket,
            "2048": per_bucket,
        }

        self.current_counts[bucket] = {
            "256": 0,
            "512": 0,
            "1024": 0,
            "2048": 0,
        }

    # =========================
    # MAIN SORT FUNCTION
    # =========================

    def sort(self, image_path: str, bucket_name: str) -> str:
        img = Image.open(image_path)
        width, height = img.size
        min_side = min(width, height)

        # Reject small images
        if min_side < 220:
            os.remove(image_path)
            return None

        # 🔥 Determine fixed resolution bucket
        resolution = self._get_fixed_bucket(min_side)

        # 🔥 Check if bucket is already full
        if self._is_bucket_full(bucket_name, resolution):
            os.remove(image_path)
            return None

        # Prepare folder
        bucket_folder = self._format_bucket_name(bucket_name)
        target_dir = os.path.join(self.base_dir, bucket_folder, resolution)

        ensure_dir(target_dir)

        # Generate filename
        file_index = self._get_next_index(bucket_folder, resolution)
        file_name = f"image_{file_index:04d}.jpg"
        target_path = os.path.join(target_dir, file_name)

        # Resize to exact resolution
        img = self._resize_image(img, resolution)

        img.save(target_path, "JPEG", quality=95)

        # Update counts
        self.current_counts[bucket_name][resolution] += 1

        # Remove original
        os.remove(image_path)

        return target_path

    # =========================
    # FIXED RANGE LOGIC (YOUR RULE)
    # =========================

    def _get_fixed_bucket(self, min_side: int) -> str:
        if min_side >= 2048:
           return "2048"
        if min_side >= 1024 and min_side < 2048:
           return "1024"
        if min_side >= 512 and min_side < 1024:
           return "512"
        if min_side >= 220 and min_side < 512:
           return "256"

    # =========================
    # CHECK IF FULL
    # =========================

    def _is_bucket_full(self, bucket: str, resolution: str) -> bool:
        if bucket not in self.target_counts:
            return False

        return self.current_counts[bucket][resolution] >= self.target_counts[bucket][resolution]

    # =========================
    # RESIZE
    # =========================

    def _resize_image(self, img, resolution: str):
        size_map = {
            "256": 256,
            "512": 512,
            "1024": 1024,
            "2048": 2048,
        }

        target = size_map[resolution]
        return img.resize((target, target))

    # =========================
    # NAMING
    # =========================

    def _get_next_index(self, bucket: str, resolution: str) -> int:
        if bucket not in self.counters:
            self.counters[bucket] = {}

        if resolution not in self.counters[bucket]:
            self.counters[bucket][resolution] = 1
        else:
            self.counters[bucket][resolution] += 1

        return self.counters[bucket][resolution]

    def _format_bucket_name(self, bucket_name: str) -> str:
        bucket_map = {
            "people_portraits": "01_people_portraits",
            "clothing_textiles": "02_clothing_textiles",
            "architecture": "03_architecture",
            "landscape_nature": "04_landscape_nature",
            "urban_street": "05_urban_street",
            "rural_village": "06_rural_village",
            "food_drink": "07_food_drink",
            "festivals_rituals": "08_festivals_rituals",
            "objects_artifacts": "09_objects_artifacts",
            "animals_wildlife": "10_animals_wildlife",
            "art_design": "11_art_design",
            "abstract_texture": "12_abstract_texture",
        }

        return bucket_map.get(bucket_name, bucket_name)