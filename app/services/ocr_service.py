from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract

from app.services.preprocessing_service import PreprocessingService


class OCRService:
    def __init__(self):
        self.preprocessing = PreprocessingService()

    def load_images(self, file_path: str) -> list:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')

        if path.suffix.lower() == '.pdf':
            images = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    pix = page.get_pixmap()
                    img = cv2.imdecode(np.frombuffer(pix.tobytes('png'), dtype=np.uint8), cv2.IMREAD_COLOR)
                    if img is not None:
                        images.append(img)
            return images

        img = cv2.imread(file_path)
        return [img] if img is not None else []

    def run(self, file_path: str) -> tuple[str, dict[str, float]]:
        images = self.load_images(file_path)
        if not images:
            raise ValueError('No readable pages/images were found in the selected file.')

        texts: list[str] = []
        confidence: dict[str, float] = {}
        for idx, image in enumerate(images, start=1):
            preprocessed = self.preprocessing.preprocess(image)
            text = pytesseract.image_to_string(preprocessed)
            texts.append(text)
            confidence[f'page_{idx}'] = 0.0
        return '\n\n'.join(texts), confidence
