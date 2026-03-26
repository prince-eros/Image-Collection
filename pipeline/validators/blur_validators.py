import numpy as np


class BlurValidator:
    def __init__(self, min_variance: float, tolerance: float):
        self.min_variance = min_variance
        self.tolerance = max(0.0, tolerance)

    def variance(self, rgb: np.ndarray) -> float:
        h, w, _ = rgb.shape

        # 🔥 take center crop (important region)
        cx, cy = w // 2, h // 2
        crop_w, crop_h = int(w * 0.5), int(h * 0.5)

        x1 = max(cx - crop_w // 2, 0)
        x2 = min(cx + crop_w // 2, w)
        y1 = max(cy - crop_h // 2, 0)
        y2 = min(cy + crop_h // 2, h)

        center = rgb[y1:y2, x1:x2]

        # convert to grayscale
        gray = (
           center[:, :, 0] * 0.299 +
           center[:, :, 1] * 0.587 +
           center[:, :, 2] * 0.114
           )

        dx = np.diff(gray, axis=1)
        dy = np.diff(gray, axis=0)
        grad = np.concatenate([dx.ravel(), dy.ravel()])

        return float(np.var(grad))

    def is_blurry(self, variance: float) -> (bool, str):
        relaxed = self.min_variance - self.tolerance

        if variance < self.min_variance:
            if variance >= relaxed:
                return False, "ok_blur_tolerated"
            return True, "blurry"

        return False, "ok"