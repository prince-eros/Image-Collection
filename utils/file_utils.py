import os


def ensure_dir(path: str):
    """
    Create directory if not exists
    """
    os.makedirs(path, exist_ok=True)


def safe_move(src: str, dst: str):
    """
    Move file safely
    """
    try:
        os.replace(src, dst)
    except Exception:
        pass


def get_filename(path: str) -> str:
    return os.path.basename(path)