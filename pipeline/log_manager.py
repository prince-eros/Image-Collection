import json
import os
from datetime import datetime


class LogManager:
    def __init__(self):
        self.file_path = "download_log.json"

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    # =========================
    # ADD ENTRY
    # =========================

    def log(self, data: dict):
        try:
            with open(self.file_path, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []

        logs.append(data)

        with open(self.file_path, "w") as f:
            json.dump(logs, f, indent=2)

    # =========================
    # BUILD ENTRY
    # =========================

    def build_entry(
        self,
        image_id,
        bucket,
        source,
        query,
        image_url,
        download_path,
        width,
        height,
        tier,
        license_type,
        status
    ):
        return {
            "image_id": image_id,
            "bucket": bucket,
            "source": source,
            "query": query,
            "image_url": image_url,
            "download_path": download_path,
            "resolution": {
                "width": width,
                "height": height
            },
            "assigned_tier": tier,
            "license": license_type,
            "downloaded_at": datetime.now().strftime("%Y-%m-%d"),
            "status": status
        }