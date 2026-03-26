# TaskA V2 - Indian Cultural Image Collection Pipeline

Scalable Python pipeline to collect, validate, normalize, and organize image datasets across multiple cultural buckets.

This project is designed to:
- Fetch images from multiple sources.
- Download in parallel with throttling.
- Reject low-quality or irrelevant samples.
- Sort accepted images into fixed resolution tiers.
- Save metadata, logs, and checkpoint state for resumable runs.

## What This Repository Contains

- CLI entrypoint: `scrape.py`
- Core pipeline modules: `pipeline/`
- Source adapters: `sources/`
- Utility modules: `utils/`
- Dataset storage:
	- `data/raw/` - freshly downloaded files
	- `data/clean/` - validated (pre-sort) files
	- `data/rejected/` - failed validation
	- `data/sorted/` - final bucketed dataset by category and resolution
- Runtime state: `state/`
- Logs: `logs/`

## High-Level Pipeline Flow

1. CLI receives run mode and target counts.
2. `Orchestrator` starts bucket processing.
3. `SourceManager` provides source adapters.
4. Images are fetched from each source until target is reached.
5. `ConcurrencyManager` processes batches in parallel.
6. `Downloader` saves files to `data/raw/`.
7. `Validator` performs:
	 - duplicate hash check
	 - watermark detection
	 - relevance filtering
	 - blur check
8. Valid files move to `data/clean/`.
9. `ResolutionSorter` resizes and places files into fixed tiers under `data/sorted/`.
10. `MetadataWriter` creates `.txt` sidecar metadata files.
11. `StateManager`, `StatsManager`, and `LogManager` update run artifacts.

## Buckets

The configured semantic buckets are:

- `people_portraits`
- `clothing_textiles`
- `architecture`
- `landscape_nature`
- `urban_street`
- `rural_village`
- `food_drink`
- `festivals_rituals`
- `objects_artifacts`
- `animals_wildlife`
- `art_design`
- `abstract_texture`

Sorted output folder naming uses ordered prefixes, e.g.:
- `01_people_portraits`
- `02_clothing_textiles`
- ...
- `12_abstract_texture`

## Resolution Policy

Images are assigned by minimum side length to fixed tiers:

- `2048`: min side >= 2048
- `1024`: 1024 <= min side < 2048
- `512`: 512 <= min side < 1024
- `256`: 220 <= min side < 512
- `< 220`: rejected

Within a bucket run, target distribution is currently split evenly across the 4 tiers.

## Requirements

## 1) Python

- Python 3.10+

## 2) Install dependencies

Because `pyproject.toml` currently has no dependencies listed, install from `requirements.txt` (or install packages manually if this file is incomplete):

```bash
pip install -r requirements.txt
```

Common packages used by current code include:
- `requests`
- `Pillow`
- `numpy`
- `python-dotenv`

## 3) Environment variables

Create a `.env` file in project root for API-backed sources. `Config.get_api_key("<source>")` expects keys in this format:

```env
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
UNSPLASH_API_KEY=your_key
...etc
```

Only sources that require keys need them.

## Usage

Run from project root.

### Single bucket mode

```bash
python scrape.py --bucket people_portraits --count 5000
```

### All buckets mode

```bash
python scrape.py --all --count-per-bucket 10000
```

### With custom concurrency, delay, resume, logging

```bash
python scrape.py --all --count-per-bucket 10000 --workers 8 --delay 0.8 --resume --log-level INFO
```

## CLI Options

- `--bucket <name>`: run one bucket
- `--all`: run all configured buckets
- `--count <n>`: required with `--bucket`
- `--count-per-bucket <n>`: required with `--all`
- `--workers <n>`: concurrent workers (default `4`)
- `--delay <seconds>`: delay between HTTP requests (default `1.0`)
- `--resume`: continue from checkpoint state
- `--log-level`: `DEBUG | INFO | WARNING | ERROR`

## Runtime Artifacts

During runs, these files are produced/updated:

- `logs/pipeline.log` - runtime log stream
- `state/checkpoint.json` - per-bucket progress and seen URLs
- `state/hashes.txt` - dedup hashes
- `download_log.json` - accepted image event log
- `collection_stats.csv` - per bucket/source/tier counters

## Data Layout Example

```text
data/
	sorted/
		01_people_portraits/
			256/
				image_0001.jpg
				image_0001.txt
			512/
			1024/
			2048/
```

Each `.jpg` should have a matching `.txt` metadata sidecar.

## Consistency Check

`pipeline/consistency_checker.py` validates:
- expected resolution folders exist
- `.jpg` and `.txt` pair presence
- image readability (corruption check)

The checker is invoked in `scrape.py` after main flow.

## Known Issues In Current Codebase

This repository appears to be mid-refactor. A few modules contain inconsistencies that may affect execution:

- `pipeline/orchestrator.py` references `self.concurrency.run(...)` but initializes `self.concurrency_manager`.
- `pipeline/source_manager.py` currently contains downloader code content, suggesting accidental overwrite.
- `pipeline/downloader.py` has duplicated class definitions in one file.
- `main.py` and packaging metadata are still default scaffolding.

If you want, the next step can be a stabilization pass to fix these issues and make the pipeline executable end-to-end.

## Development Notes

- Keep source adapters in `sources/` returning the standardized metadata schema from `BaseSource`.
- Preserve side effects in order: download -> validate -> sort -> metadata/log/state updates.
- For large runs, monitor disk growth in `data/` and rotate/backup logs.

## License and Attribution

When using external image APIs, follow each provider's license and attribution requirements.
Metadata sidecars and `download_log.json` help retain provenance.

