from PIL import Image


def load_preview(path: str):
    return Image.open(path)
