import os
import logging
from datetime import datetime
from typing import Dict


class MetadataWriter:
    """
    Creates .txt metadata file for each image.

    Required fields:
    1. Description (2–3 sentences)
    2. Source
    3. License
    4. Original URL
    5. Download date
    """

    def __init__(self):
        pass

    # =========================
    # MAIN FUNCTION
    # =========================

    def write(self, image_path: str, metadata: Dict):
        """
        Creates a .txt file alongside the image
        """

        try:
            txt_path = self._get_txt_path(image_path)

            description = self._build_description(metadata)
            source = metadata.get("source", "unknown")
            license_type = metadata.get("license", "unknown")
            url = metadata.get("url", "unknown")
            download_date = self._get_today_date()

            content = self._format_content(
                description,
                source,
                license_type,
                url,
                download_date
            )

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            logging.error(f"Metadata writing failed: {e}")

    # =========================
    # HELPERS
    # =========================

    def _get_txt_path(self, image_path: str) -> str:
        base, _ = os.path.splitext(image_path)
        return base + ".txt"

    def _get_today_date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    # =========================
    # DESCRIPTION BUILDER
    # =========================

    def _build_description(self, metadata: Dict) -> str:
        """
        Build 2–3 sentence description.
        Uses available metadata like alt_text, tags, title.
        """

        alt_text = metadata.get("alt_text", "")
        tags = metadata.get("tags", [])
        title = metadata.get("title", "")

        # Clean fallback logic
        if alt_text:
            return self._clean_text(alt_text)

        if title:
            return self._expand_to_sentences(title)

        if tags:
            tag_sentence = ", ".join(tags[:5])
            return f"This image shows {tag_sentence}. It represents elements of Indian culture and environment."

        return "This image represents an aspect of Indian culture, including people, environment, or traditional elements. It is suitable for training AI models."

    # =========================
    # TEXT FORMATTING
    # =========================

    def _format_content(
        self,
        description: str,
        source: str,
        license_type: str,
        url: str,
        download_date: str
    ) -> str:
        """
        Format metadata into required structure
        """

        return (
            f"{description.strip()}\n\n"
            f"[Source: {source}]\n"
            f"[License: {license_type}]\n"
            f"[Original URL: {url}]\n"
            f"[Downloaded: {download_date}]"
        )

    def _clean_text(self, text: str) -> str:
        """
        Clean raw alt-text into proper sentences
        """
        text = text.strip()

        # Ensure sentence ends properly
        if not text.endswith("."):
            text += "."

        # Expand if too short
        if len(text.split()) < 8:
            text += " This image captures elements of Indian culture, traditions, or environment."

        return text

    def _expand_to_sentences(self, title: str) -> str:
        """
        Convert title into 2-sentence description
        """
        title = title.strip()

        return (
            f"This image shows {title.lower()}. "
            f"It represents aspects of Indian culture, lifestyle, or environment."
        )