from pathlib import Path

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}


def is_supported_file(path: str) -> bool:
    return Path(path).suffix.lower() in ALLOWED_EXTENSIONS
