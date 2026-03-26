import csv
import os
from collections import defaultdict


class StatsManager:
    def __init__(self):
        self.file_path = "collection_stats.csv"

        self.stats = defaultdict(lambda: {
            "256": 0,
            "512": 0,
            "1024": 0,
            "2048": 0,
            "total": 0
        })

        # create file if not exists
        if not os.path.exists(self.file_path):
            self._init_file()

    # =========================
    # INIT CSV
    # =========================

    def _init_file(self):
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "bucket",
                "source",
                "count_256",
                "count_512",
                "count_1024",
                "count_2048",
                "total"
            ])

    # =========================
    # UPDATE STATS
    # =========================

    def update(self, bucket, source, resolution):
        key = (bucket, source)

        if key not in self.stats:
            self.stats[key] = {
                "256": 0,
                "512": 0,
                "1024": 0,
                "2048": 0,
                "total": 0
            }

        self.stats[key][resolution] += 1
        self.stats[key]["total"] += 1

    # =========================
    # SAVE TO CSV
    # =========================

    def save(self):
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow([
                "bucket",
                "source",
                "count_256",
                "count_512",
                "count_1024",
                "count_2048",
                "total"
            ])

            for (bucket, source), counts in self.stats.items():
                writer.writerow([
                    bucket,
                    source,
                    counts["256"],
                    counts["512"],
                    counts["1024"],
                    counts["2048"],
                    counts["total"]
                ])