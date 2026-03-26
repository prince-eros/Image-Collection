import logging
from typing import Dict, Any
import time
from pipeline.source_manager import SourceManager
from pipeline.downloader import Downloader
from pipeline.validator import Validator
from pipeline.resolution_sorter import ResolutionSorter
from pipeline.metadata_writer import MetadataWriter
from pipeline.state_manager import StateManager
from pipeline.progress_tracker import ProgressTracker
from pipeline.concurrency import ConcurrencyManager
from pipeline.stats_manager import StatsManager
from pipeline.log_manager import LogManager

class Orchestrator:
    """
    Advanced pipeline controller:
    - Handles multiple source types
    - Manages fallback
    - Controls full image lifecycle
    """

    def __init__(self, workers: int = 4, delay: float = 1.0, resume: bool = False):
        self.workers = workers
        self.delay = delay
        self.resume = resume

        self.source_manager = SourceManager()
        self.downloader = Downloader(workers=workers, delay=delay)
        self.validator = Validator()
        self.sorter = ResolutionSorter()
        self.metadata_writer = MetadataWriter()
        self.state_manager = StateManager()
        self.progress_tracker = ProgressTracker()
        self.concurrency_manager = ConcurrencyManager(workers=workers)
        self.stats_manager = StatsManager()
        self.log_manager = LogManager()
        self.collected = 0
        self.target = 0
        self.bucket = ""

    # =========================
    # MAIN ENTRY
    # =========================

    def run_bucket(self, bucket_name: str, target_count: int):
        self.bucket = bucket_name
        self.target = target_count
        self.sorter.set_target(bucket_name, target_count)
        self.progress_tracker.start(bucket_name, target_count)
        previous = self.state_manager.get_progress(bucket_name)

        if self.resume:
           self.collected = previous
           logging.info(f"♻️ Resuming from {previous}")
        else:
            self.collected = 0

        logging.info(f"🎯 Target: {target_count} images")

        sources = self.source_manager.get_sources()

        for source in sources:
            if self.collected >= self.target:
                break

            logging.info(
                f"\n🔄 Source: {source.name} | Type: {source.source_type}"
            )

            try:
                self._run_source(source)
            except Exception as e:
                logging.error(f"Source failed: {source.name} | {e}")
                continue

        logging.info(f"✅ Completed bucket: {bucket_name} ({self.collected}/{self.target})")
        self.progress_tracker.finish()
        self.stats_manager.save()
    # =========================
    # SOURCE HANDLER
    # =========================

    def _run_source(self, source):
        remaining = self.target - self.collected
        batch = []

        for image_data in source.fetch_images(self.bucket, remaining):
            if self.collected >= self.target:
               break

            batch.append(image_data)

             # 🔥 Process batch in parallel
            if len(batch) >= self.workers:
                self._process_batch(batch, source)
                batch = []

        # Process leftover
        if batch:
           self._process_batch(batch, source)

    def _process_batch(self, batch, source):
        results = self.concurrency.run(
            self.downloader.download,
            batch
        )

        for image_path, image_data in results:
            try:
                self._process_pipeline(image_path, image_data, source)
            except Exception:
                 continue

    # =========================
    # CORE PIPELINE
    # =========================


    def _process_pipeline(self, image_path, image_data, source):
        
        if not image_path:
           return

        clean_path = self.validator.validate(
            image_path,
            self.bucket,
            image_data
            )
        
        if not clean_path:
           return

        sorted_path = self.sorter.sort(clean_path, self.bucket)

        # get resolution
        width, height = image_data.get("width", 0), image_data.get("height", 0)

        tier = self.sorter._get_fixed_bucket(min(width, height))

        # update stats
        self.stats_manager.update(
            self.bucket,
            source.name,
            tier
        )

        # log entry
        entry = self.log_manager.build_entry(
            image_id=image_data.get("id", ""),
            bucket=self.bucket,
            source=source.name,
            query=image_data.get("query", ""),
            image_url=image_data.get("url", ""),
            download_path=sorted_path,
            width=width,
            height=height,
            tier=tier,
            license_type=image_data.get("license", ""),
            status="accepted"
        )

        self.log_manager.log(entry)

        if not sorted_path:
           return

        self.metadata_writer.write(sorted_path, image_data)
        self.state_manager.add_seen_url(self.bucket, image_data.get("url", ""))
        self.collected += 1
        self.state_manager.update_progress(self.bucket, self.collected)

        self.progress_tracker.update(
            self.collected,
            source.name
        )

        if not image_data:
              return
        

    def _log_progress(self, source):
        if not hasattr(self, "start_time"):
           self.start_time = time.time()

        elapsed = time.time() - self.start_time

        if self.collected == 0:
           return

        rate = self.collected / elapsed
        remaining = self.target - self.collected

        eta = remaining / rate if rate > 0 else 0

        if self.collected % 5 == 0:
            logging.info(
                   f"[Bucket: {self.bucket}] "
                   f"[Source: {source.name}] "
                   f"[Collected: {self.collected}/{self.target}] "
                   f"[ETA: {eta:.1f}s]"
                )
    # =========================
    # OPTIONAL: FUTURE HOOKS
    # =========================

    def shutdown(self):
        logging.info("🛑 Shutting down pipeline")