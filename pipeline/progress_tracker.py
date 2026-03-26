import time
import logging
from typing import Dict


class ProgressTracker:
    """
    Tracks live progress of dataset collection
    - Bucket-wise tracking
    - ETA calculation
    - Source tracking
    """

    def __init__(self):
        self.start_time = None
        self.last_log_time = 0

        self.bucket = ""
        self.target = 0
        self.collected = 0

        self.source = ""

    # =========================
    # INITIALIZE TRACKING
    # =========================

    def start(self, bucket: str, target: int):
        self.start_time = time.time()
        self.bucket = bucket
        self.target = target
        self.collected = 0

        logging.info(f"🚀 Starting bucket: {bucket} | Target: {target}")

    # =========================
    # UPDATE PROGRESS
    # =========================

    def update(self, collected: int, source: str):
        self.collected = collected
        self.source = source

        self._log_progress()

    # =========================
    # ETA CALCULATION
    # =========================

    def _calculate_eta(self) -> float:
        if not self.start_time or self.collected == 0:
            return 0.0

        elapsed = time.time() - self.start_time
        rate = self.collected / elapsed

        if rate == 0:
            return 0.0

        remaining = self.target - self.collected
        eta = remaining / rate

        return eta

    # =========================
    # LOG PROGRESS
    # =========================

    def _log_progress(self):
        now = time.time()

        # 🔥 avoid too frequent logs
        if now - self.last_log_time < 2:
            return

        eta = self._calculate_eta()

        logging.info(
            f"[Bucket: {self.bucket}] "
            f"[Source: {self.source}] "
            f"[Collected: {self.collected}/{self.target}] "
            f"[ETA: {eta:.1f}s]"
        )

        self.last_log_time = now

    # =========================
    # FINAL SUMMARY
    # =========================

    def finish(self):
        total_time = time.time() - self.start_time if self.start_time else 0

        logging.info(
            f"✅ Completed bucket: {self.bucket} | "
            f"Total: {self.collected}/{self.target} | "
            f"Time: {total_time:.1f}s"
        )