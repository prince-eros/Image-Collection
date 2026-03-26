from PIL import Image


def load_image(path: str):
    """
    Safe image loading
    """
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


def get_image_size(path: str):
    try:
        img = Image.open(path)
        return img.size
    except Exception:
        return (0, 0)