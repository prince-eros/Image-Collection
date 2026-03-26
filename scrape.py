#!/usr/bin/env python3
"""
scrape.py

Main CLI entry point for the Indian Cultural Image Collection Pipeline.

Responsibilities:
- Parse CLI arguments
- Validate inputs
- Initialize orchestrator
- Trigger scraping workflow

Usage Examples:
----------------
python scrape.py --bucket people_portraits --count 5000

python scrape.py --all --count-per-bucket 10000

python scrape.py --all --count-per-bucket 1000000 --workers 8
"""

import argparse
import sys
import time
import logging
from typing import List, Optional

# Import orchestrator (you will implement this next)
from pipeline.orchestrator import Orchestrator
from pipeline.config import Config
from pipeline.consistency_checker import ConsistencyChecker


Config.validate()

# =========================
# CONSTANTS
# =========================

VALID_BUCKETS = [
    "people_portraits",
    "clothing_textiles",
    "architecture",
    "landscape_nature",
    "urban_street",
    "rural_village",
    "food_drink",
    "festivals_rituals",
    "objects_artifacts",
    "animals_wildlife",
    "art_design",
    "abstract_texture",
]


# =========================
# LOGGING SETUP
# =========================

def setup_logging(log_level: str):
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# =========================
# ARGUMENT PARSER
# =========================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Indian Cultural Image Scraper (Scalable Pipeline)"
    )

    # Mode selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--bucket",
        type=str,
        help="Scrape a single bucket (e.g., people_portraits)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Scrape all buckets",
    )

    # Count parameters
    parser.add_argument(
        "--count",
        type=int,
        help="Number of images (required if using --bucket)",
    )

    parser.add_argument(
        "--count-per-bucket",
        type=int,
        help="Images per bucket (required if using --all)",
    )

    # Performance options
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent download workers (default: 4)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    # Resume support
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint",
    )

    return parser.parse_args()


# =========================
# VALIDATION
# =========================

def validate_args(args):
    # Validate bucket
    if args.bucket:
        if args.bucket not in VALID_BUCKETS:
            raise ValueError(f"Invalid bucket: {args.bucket}")

        if not args.count:
            raise ValueError("--count is required when using --bucket")

    # Validate all mode
    if args.all:
        if not args.count_per_bucket:
            raise ValueError("--count-per-bucket is required when using --all")

    # Validate numbers
    if args.count is not None and args.count <= 0:
        raise ValueError("--count must be positive")

    if args.count_per_bucket is not None and args.count_per_bucket <= 0:
        raise ValueError("--count-per-bucket must be positive")

    if args.workers <= 0:
        raise ValueError("--workers must be positive")

    if args.delay < 0:
        raise ValueError("--delay must be >= 0")


# =========================
# MAIN EXECUTION
# =========================

def main():
    args = parse_arguments()

    try:
        validate_args(args)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    setup_logging(args.log_level)

    logging.info(" Starting Image Scraping Pipeline")
    logging.info(f"Arguments: {args}")

    start_time = time.time()

    try:
        # Initialize orchestrator
        orchestrator = Orchestrator(
            workers=args.workers,
            delay=args.delay,
            resume=args.resume,
        )

        # SINGLE BUCKET MODE
        if args.bucket:
            logging.info(f"Processing bucket: {args.bucket}")
            orchestrator.run_bucket(
                bucket_name=args.bucket,
                target_count=args.count,
            )

        # ALL BUCKETS MODE
        elif args.all:
            logging.info("Processing ALL buckets")

            for bucket in VALID_BUCKETS:
                logging.info(f"\n--- Bucket: {bucket} ---")
                orchestrator.run_bucket(
                    bucket_name=bucket,
                    target_count=args.count_per_bucket,
                )

    except KeyboardInterrupt:
        logging.warning("Interrupted by user. Saving progress...")
        orchestrator.save_state()

    except Exception as e:
        logging.exception(f"Fatal error: {e}")
        if 'orchestrator' in locals():
            orchestrator.save_state()
        sys.exit(1)

    finally:
        elapsed = time.time() - start_time
        logging.info(f"Total time: {elapsed:.2f} seconds")
        logging.info("Pipeline finished")

checker = ConsistencyChecker()
checker.run()
# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    main()