import os
import time
import uuid
import logging
import shutil
import requests
from typing import Dict, Optional

from utils.rate_limiter import RateLimiter


class Downloader:
    """
    Handles:
    - API downloads (URL-based)
    - Local file handling (Bing fallback)
    """

    def __init__(self, workers: int = 4, delay: float = 1.0):
        self.delay = delay
        self.rate_limiter = RateLimiter(delay=delay)

        self.raw_dir = "data/raw"
        os.makedirs(self.raw_dir, exist_ok=True)

        self.headers = {
            "User-Agent": "IndianCulturalDatasetBot/1.0"
        }

    # =========================
    # MAIN FUNCTION
    # =========================

    def download(self, image_data: Dict) -> Optional[str]:
        url = image_data.get("url")

        if not url:
            logging.warning("No URL provided")
            return None

        # 🔥 CASE 1: LOCAL FILE (Bing)
        if self._is_local_file(url):
            return self._handle_local_file(url)

        # 🔥 CASE 2: REMOTE URL (API sources)
        return self._download_from_url(url)

    # =========================
    # LOCAL FILE HANDLER
    # =========================

    def _handle_local_file(self, file_path: str) -> Optional[str]:
        try:
            if not os.path.exists(file_path):
                logging.warning(f"Local file not found: {file_path}")
                return None

            file_name = self._generate_filename(file_path)
            destination = os.path.join(self.raw_dir, file_name)

            shutil.move(file_path, destination)

            return destination

        except Exception as e:
            logging.error(f"Local file handling error: {e}")
            return None

    # =========================
    # REMOTE DOWNLOAD
    # =========================

    def _download_from_url(self, url: str) -> Optional[str]:
        self.rate_limiter.wait()

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logging.warning(f"Failed to download: {url}")
                return None

            file_name = self._generate_filename(url)
            file_path = os.path.join(self.raw_dir, file_name)

            with open(file_path, "wb") as f:
                f.write(response.content)

            return file_path

        except Exception as e:
            logging.error(f"Download error: {e}")
            return None

    # =========================
    # HELPERS
    # =========================

    def _is_local_file(self, path: str) -> bool:
        """
        Detect if path is local file (not URL)
        """
        return not path.startswith("http")

    def _generate_filename(self, source: str) -> str:
        ext = self._get_extension(source)
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{ext}"

    def _get_extension(self, source: str) -> str:
        if "." in source:
            ext = source.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "webp"]:
                return ext
        return "jpg"