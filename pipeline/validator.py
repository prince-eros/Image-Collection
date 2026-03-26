import os
import shutil
import logging
import hashlib
from typing import Optional, Dict

import numpy as np
from PIL import Image

from utils.file_utils import ensure_dir

from pipeline.validators.watermark_validators import WatermarkValidator
from pipeline.validators.blur_validators import BlurValidator
from pipeline.validators.relevance_validators import RelevanceValidator


class Validator:
    """
    Validates downloaded images:
    - Duplicate detection (hash-based)
    - Watermark detection
    - Blur detection (center-focused)
    - Relevance filtering
    """

    def __init__(self):
        self.clean_dir = "data/clean"
        self.rejected_dir = "data/rejected"

        ensure_dir(self.clean_dir)
        ensure_dir(self.rejected_dir)

        # =========================
        # HASH (DEDUP)
        # =========================
        self.hash_file = "state/hashes.txt"
        self.hashes = self._load_hashes()

        # =========================
        # VALIDATORS
        # =========================
        self.watermark_validator = WatermarkValidator()

        self.blur_validator = BlurValidator(
            min_variance=100.0,     # you can tune later
            tolerance=20.0
        )

        self.relevance_validator = RelevanceValidator()

    # =========================
    # MAIN VALIDATION
    # =========================

    def validate(
        self,
        image_path: str,
        bucket_name: str,
        metadata: Dict
    ) -> Optional[str]:
        """
        Returns cleaned image path if valid, else None
        """

        try:
            # Step 1: file exists
            if not os.path.exists(image_path):
                return None

            # Step 2: load image
            image = Image.open(image_path).convert("RGB")

            # =========================
            # STEP 3: HASH (DEDUP)
            # =========================
            image_hash = self._compute_hash(image_path)

            if image_hash in self.hashes:
                logging.info("Duplicate image rejected")
                self._move_to_rejected(image_path)
                return None

            # =========================
            # STEP 4: WATERMARK
            # =========================
            is_watermarked, wm_score = self.watermark_validator.is_watermarked(image)

            if is_watermarked:
                logging.info(f"🚫 Watermark detected ({wm_score:.2f})")
                self._move_to_rejected(image_path)
                return None

            # =========================
            # STEP 5: RELEVANCE
            # =========================
            is_relevant, reason_rel = self.relevance_validator.is_relevant(
                bucket_name,
                metadata
            )

            if not is_relevant:
                logging.info("🚫 Irrelevant image rejected")
                self._move_to_rejected(image_path)
                return None

            # =========================
            # STEP 6: BLUR (CENTER FOCUSED)
            # =========================
            rgb = np.asarray(image, dtype=np.float32)

            blur_variance = self.blur_validator.variance(rgb)
            is_blurry, blur_reason = self.blur_validator.is_blurry(blur_variance)

            if is_blurry:
                logging.info("🚫 Blurry image rejected")
                self._move_to_rejected(image_path)
                return None

            # =========================
            # STEP 7: MOVE TO CLEAN
            # =========================
            clean_path = self._move_to_clean(image_path)

            # =========================
            # STEP 8: SAVE HASH
            # =========================
            self.hashes.add(image_hash)
            self._save_hash(image_hash)

            return clean_path

        except Exception as e:
            logging.error(f"Validation failed: {e}")
            self._move_to_rejected(image_path)
            return None

    # =========================
    # HASH FUNCTIONS
    # =========================

    def _compute_hash(self, image_path: str) -> str:
        hasher = hashlib.md5()

        with open(image_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _load_hashes(self):
        if not os.path.exists(self.hash_file):
            return set()

        with open(self.hash_file, "r") as f:
            return set(line.strip() for line in f.readlines())

    def _save_hash(self, image_hash: str):
        with open(self.hash_file, "a") as f:
            f.write(image_hash + "\n")

    # =========================
    # FILE MOVEMENT
    # =========================

    def _move_to_clean(self, image_path: str) -> str:
        file_name = os.path.basename(image_path)
        destination = os.path.join(self.clean_dir, file_name)

        shutil.move(image_path, destination)
        return destination

    def _move_to_rejected(self, image_path: str):
        file_name = os.path.basename(image_path)
        destination = os.path.join(self.rejected_dir, file_name)

        try:
            shutil.move(image_path, destination)
        except Exception:
            pass