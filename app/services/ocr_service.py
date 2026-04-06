from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract
from pytesseract import Output

from app.config.settings import ENABLE_HANDWRITING_FALLBACK, OCR_DEFAULT_LANG, OCR_MIN_ACCEPTABLE_CONFIDENCE
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

    def run(self, file_path: str) -> tuple[str, dict[str, float | str]]:
        images = self.load_images(file_path)
        if not images:
            raise ValueError('No readable pages/images were found in the selected file.')

        texts: list[str] = []
        confidence: dict[str, float | str] = {}
        for idx, image in enumerate(images, start=1):
            best = self._run_best_profile_ocr(image)
            texts.append(best['text'])
            confidence[f'page_{idx}'] = float(best['confidence'])
            confidence[f'page_{idx}_profile'] = str(best['profile'])
        return '\n\n'.join(texts), confidence

    def _run_best_profile_ocr(self, image) -> dict[str, str | float]:
        candidates: list[dict[str, str | float]] = []
        for profile in self.preprocessing.pick_profiles(image):
            preprocessed = self.preprocessing.preprocess_with_profile(image, profile)
            text, conf = self._extract_text_with_confidence(preprocessed, config='--oem 3 --psm 6')
            candidates.append({'text': text, 'confidence': conf, 'profile': profile})

        best = max(candidates, key=lambda item: float(item['confidence']), default={'text': '', 'confidence': 0.0, 'profile': 'clean_scan'})
        if ENABLE_HANDWRITING_FALLBACK and float(best['confidence']) < OCR_MIN_ACCEPTABLE_CONFIDENCE:
            handwriting = self._run_handwriting_fallback(image)
            if float(handwriting['confidence']) > float(best['confidence']):
                best = handwriting
        return best

    def _run_handwriting_fallback(self, image) -> dict[str, str | float]:
        preprocessed = self.preprocessing.preprocess_with_profile(image, 'mobile_photo')
        text, conf = self._extract_text_with_confidence(preprocessed, config='--oem 1 --psm 11')
        return {'text': text, 'confidence': conf, 'profile': 'handwriting_fallback'}

    def _extract_text_with_confidence(self, image, config: str) -> tuple[str, float]:
        data = pytesseract.image_to_data(image, output_type=Output.DICT, lang=OCR_DEFAULT_LANG, config=config)
        words: list[str] = []
        confs: list[float] = []
        for raw_text, raw_conf in zip(data.get('text', []), data.get('conf', [])):
            token = (raw_text or '').strip()
            if not token:
                continue
            words.append(token)
            try:
                conf_value = float(raw_conf)
            except (TypeError, ValueError):
                continue
            if conf_value >= 0:
                confs.append(conf_value)
        text = ' '.join(words)
        avg_conf = float(sum(confs) / len(confs)) if confs else 0.0
        return text, avg_conf
