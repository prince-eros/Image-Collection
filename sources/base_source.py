from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, List


class BaseSource(ABC):
    """
    Abstract base class for all image sources.

    Every source MUST:
    - Implement fetch_images()
    - Return standardized metadata format
    """

    # =========================
    # REQUIRED CONFIG
    # =========================

    name: str = "base"
    required_api_key: str = None  # e.g. "PEXELS_API_KEY"

    # =========================
    # MAIN FETCH METHOD
    # =========================

    @abstractmethod
    def fetch_images(self, query: str, limit: int) -> Generator[Dict[str, Any], None, None]:
        """
        Must yield image metadata dictionaries.

        Args:
            query: search keyword (bucket name)
            limit: number of images required

        Returns:
            Generator of standardized image metadata
        """
        pass

    # =========================
    # STANDARD METADATA FORMAT
    # =========================

    def build_metadata(
        self,
        url: str,
        source: str,
        license_type: str,
        alt_text: str = "",
        tags: List[str] = None,
        title: str = ""
    ) -> Dict[str, Any]:
        """
        Standard metadata structure for all sources
        """

        return {
            "url": url,
            "source": source,
            "license": license_type,
            "alt_text": alt_text or "",
            "tags": tags or [],
            "title": title or "",
        }

    # =========================
    # OPTIONAL: AVAILABILITY CHECK
    # =========================

    def is_available(self) -> bool:
        """
        Override if needed (e.g., check API key exists)
        """
        return True