import importlib
import logging
import sys
from pathlib import Path
from typing import Optional

from PIL import Image

LOGGER = logging.getLogger(__name__)

# =========================
# 🔥 PATH SETUP
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]

# vendor repo (code)
VENDOR_PATH = BASE_DIR / ".vendor" / "watermark-detection"

# 🔥 your pre-downloaded model cache
MODEL_CACHE_PATH = BASE_DIR / ".model_cache" / "watermark-detection"

# add vendor path
if str(VENDOR_PATH) not in sys.path:
    sys.path.insert(0, str(VENDOR_PATH))


class WatermarkValidator:
    def __init__(
        self,
        model_name: str = "convnext-tiny",
        device: str = "auto",
        threshold: float = 0.5,
    ):
        self.threshold = threshold  # mentor requirement

        import torch

        # =========================
        # LOAD MODULE (NO CLONE)
        # =========================
        try:
            wmdetection_models = importlib.import_module("wmdetection.models")
        except ModuleNotFoundError as e:
            raise RuntimeError(
                "wmdetection not found. Ensure .vendor/watermark-detection exists"
            ) from e

        get_model = getattr(wmdetection_models, "get_watermarks_detection_model")

        # =========================
        # DEVICE
        # =========================
        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        if model_name != "convnext-tiny":
            raise ValueError(
                f"Unsupported model_name='{model_name}'. Expected 'convnext-tiny'."
            )

        LOGGER.info(f"[Watermark] Loading model on {device}")

        # Ensure cache dir exists and prefer local weights first.
        MODEL_CACHE_PATH.mkdir(parents=True, exist_ok=True)

        model = None
        transforms = None
        local_weights = self._find_local_weights()

        if local_weights is not None:
            LOGGER.info(f"[Watermark] Using local weights: {local_weights}")
            model, transforms = get_model(
                model_name,
                device=device,
                fp16=False,
                pretrained=False,
                cache_dir=str(MODEL_CACHE_PATH),
            )
            state_dict = torch.load(str(local_weights), map_location=device)
            model.load_state_dict(state_dict)
            model.eval()
            model = model.to(device)
        else:
            LOGGER.info("[Watermark] Local weights not found, trying cache_dir download path")
            model, transforms = get_model(
                model_name,
                device=device,
                fp16=False,
                pretrained=True,
                cache_dir=str(MODEL_CACHE_PATH),
            )

        self._torch = torch
        self._model = model
        self._transforms = transforms
        self._device = device

    def _find_local_weights(self) -> Optional[Path]:
        direct = MODEL_CACHE_PATH / "convnext-tiny_watermarks_detector.pth"
        if direct.exists():
            return direct

        # HuggingFace cached snapshots may nest files under snapshots/*/
        snapshot_candidates = list(
            MODEL_CACHE_PATH.glob(
                "models--boomb0om--watermark-detectors/snapshots/*/convnext-tiny_watermarks_detector.pth"
            )
        )
        if snapshot_candidates:
            return snapshot_candidates[0]

        return None

    # =========================
    # SCORE
    # =========================
    def score(self, image: Image.Image) -> float:
        with self._torch.no_grad():
            tensor = self._transforms(image).float().unsqueeze(0).to(self._device)
            logits = self._model(tensor)
            probs = self._torch.softmax(logits, dim=1)
            return float(probs[0, 1].item())

    # =========================
    # CHECK
    # =========================
    def is_watermarked(self, image: Image.Image):
        try:
            score = self.score(image)
            return score >= self.threshold, score
        except Exception as e:
            LOGGER.warning(f"Watermark failed: {e}")
            return False, 0.0