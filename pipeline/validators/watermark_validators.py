import importlib
import logging
import subprocess
import sys
from pathlib import Path

from PIL import Image

LOGGER = logging.getLogger(__name__)


class WatermarkValidator:
    def __init__(
        self,
        model_name: str = "convnext-tiny",
        cache_dir: str = ".cache",
        device: str = "auto",
        threshold: float = 0.5,
    ):
        self.threshold = 0.5  # mentor enforced

        import torch

        try:
            wmdetection_models = importlib.import_module("wmdetection.models")
        except ModuleNotFoundError:
            wmdetection_models = self._clone_and_import()

        get_model = getattr(wmdetection_models, "get_watermarks_detection_model")

        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        LOGGER.info(f"[Watermark] Loading model on {device}")

        model, transforms = get_model(
            model_name,
            device=device,
            fp16=False,
            pretrained=True,
            cache_dir=cache_dir,
        )

        self._torch = torch
        self._model = model
        self._transforms = transforms
        self._device = device

    # =========================
    # MAIN
    # =========================

    def score(self, image: Image.Image) -> float:
        with self._torch.no_grad():
            tensor = self._transforms(image).float().unsqueeze(0).to(self._device)
            logits = self._model(tensor)
            probs = self._torch.softmax(logits, dim=1)
            return float(probs[0, 1].item())

    def is_watermarked(self, image: Image.Image) -> (bool, float):
        try:
            score = self.score(image)
            return score >= self.threshold, score
        except Exception as e:
            LOGGER.warning(f"Watermark failed: {e}")
            return False, 0.0

    # =========================
    # CLONE REPO
    # =========================

    def _clone_and_import(self):
        project_root = Path(__file__).resolve().parents[2]
        vendor_repo = project_root / ".vendor" / "watermark-detection"

        if not vendor_repo.exists():
            subprocess.run(
                ["git", "clone",
                 "https://github.com/boomb0om/watermark-detection.git",
                 str(vendor_repo)],
                check=True,
            )

        sys.path.insert(0, str(vendor_repo))
        return importlib.import_module("wmdetection.models")