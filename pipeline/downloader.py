import os
import uuid
import logging
import shutil
import requests
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.request_handler import safe_request
from utils.rate_limiter import RateLimiter


class Downloader:
    """
    Concurrent downloader:
    - Handles URL + local files
    - Uses ThreadPool for speed
    """

    def __init__(self, workers: int = 4, delay: float = 1.0):
        self.delay = delay
        self.rate_limiter = RateLimiter(delay=delay)
        self.workers = workers

        self.raw_dir = "data/raw"
        os.makedirs(self.raw_dir, exist_ok=True)

        self.headers = {
            "User-Agent": "IndianCulturalDatasetBot/1.0"
        }

    # =========================
    # PUBLIC BATCH DOWNLOAD
    # =========================

    # def download_batch(self, batch: List[Dict]) -> List[str]:
    #     results = []

    #     with ThreadPoolExecutor(max_workers=self.workers) as executor:
    #         futures = [executor.submit(self.download, item) for item in batch]

    #         for future in as_completed(futures):
    #             result = future.result()
    #             if result:
    #                 results.append(result)

    #     return results

    # =========================
    # SINGLE DOWNLOAD
    # =========================

    def download(self, image_data: Dict) -> Optional[str]:
        url = image_data.get("url")

        if not url:
            return None

        if self._is_local_file(url):
            return self._handle_local_file(url)

        return self._download_from_url(url)

    # =========================
    # LOCAL FILE
    # =========================

    def _handle_local_file(self, file_path: str) -> Optional[str]:
        try:
            if not os.path.exists(file_path):
                return None

            file_name = self._generate_filename(file_path)
            destination = os.path.join(self.raw_dir, file_name)

            shutil.move(file_path, destination)

            return destination

        except Exception:
            return None

    # =========================
    # URL DOWNLOAD
    # =========================

    def _download_from_url(self, url: str) -> Optional[str]:
        self.rate_limiter.wait()

        try:
            content = safe_request(url, headers=self.headers)

            if not content:
               return None

            file_name = self._generate_filename(url)
            file_path = os.path.join(self.raw_dir, file_name)

            with open(file_path, "wb") as f:
                 f.write(content)

            return file_path 

        except Exception:
            return None

    # =========================
    # HELPERS
    # =========================

    def _is_local_file(self, path: str) -> bool:
        return not path.startswith("http")

    def _generate_filename(self, source: str) -> str:
        ext = self._get_extension(source)
        return f"{uuid.uuid4().hex}.{ext}"

    def _get_extension(self, source: str) -> str:
        if "." in source:
            ext = source.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "webp"]:
                return ext
        return "jpg"