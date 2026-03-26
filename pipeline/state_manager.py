import json
import os
import logging
from typing import Dict, Set


class StateManager:
    """
    Handles checkpointing + resume system
    - Tracks collected count
    - Tracks seen image URLs (avoid duplicates on resume)
    """

    def __init__(self):
        self.state_file = "state/checkpoint.json"
        self.state: Dict = {}

        os.makedirs("state", exist_ok=True)
        self._load()

    # =========================
    # LOAD STATE
    # =========================

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {}
        else:
            self.state = {}

    # =========================
    # SAVE STATE
    # =========================

    def _save(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logging.error(f"State save error: {e}")

    # =========================
    # PROGRESS
    # =========================

    def get_progress(self, bucket: str) -> int:
        return self.state.get(bucket, {}).get("collected", 0)

    def update_progress(self, bucket: str, count: int):
        if bucket not in self.state:
            self.state[bucket] = {}

        self.state[bucket]["collected"] = count
        self._save()

    # =========================
    # URL TRACKING (NEW 🔥)
    # =========================

    def get_seen_urls(self, bucket: str) -> Set[str]:
        urls = self.state.get(bucket, {}).get("seen_urls", [])
        return set(urls)

    def add_seen_url(self, bucket: str, url: str):
        if bucket not in self.state:
            self.state[bucket] = {}

        if "seen_urls" not in self.state[bucket]:
            self.state[bucket]["seen_urls"] = []

        # avoid duplicates
        if url not in self.state[bucket]["seen_urls"]:
            self.state[bucket]["seen_urls"].append(url)

        self._save()

    # =========================
    # RESET
    # =========================

    def reset_bucket(self, bucket: str):
        if bucket in self.state:
            del self.state[bucket]
            self._save()