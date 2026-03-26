from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any


class ConcurrencyManager:
    """
    Handles parallel execution of tasks
    - ThreadPool based
    - Safe result collection
    """

    def __init__(self, workers: int = 4):
        self.workers = workers

    # =========================
    # RUN TASKS IN PARALLEL
    # =========================

    def run(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        Runs function in parallel on given items
        Returns successful results only
        """

        results = []

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(func, item): item
                for item in items
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        results.append((result, futures[future]))
                except Exception:
                    continue

        return results