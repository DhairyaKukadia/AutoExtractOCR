import cv2
import numpy as np


class PreprocessingService:
    PROFILES = ('clean_scan', 'noisy_scan', 'mobile_photo')

    def estimate_image_quality(self, image) -> dict[str, float]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = float(np.std(gray))
        noise = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        black_pixels = int(np.sum(gray < 40))
        white_pixels = int(np.sum(gray > 215))
        ratio = black_pixels / max(1, black_pixels + white_pixels)
        handwritten_likelihood = float(min(1.0, max(0.0, ratio * 4.0)))

        return {
            'contrast': contrast,
            'noise': noise,
            'handwritten_likelihood': handwritten_likelihood,
        }

    def pick_profiles(self, image) -> list[str]:
        metrics = self.estimate_image_quality(image)

        if metrics['contrast'] < 25:
            return ['mobile_photo', 'noisy_scan']
        if metrics['noise'] > 120:
            return ['noisy_scan', 'clean_scan']
        return ['clean_scan', 'mobile_photo']

    def preprocess(self, image):
        return self.preprocess_with_profile(image, 'clean_scan')

    def preprocess_with_profile(self, image, profile: str = 'clean_scan'):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if profile not in self.PROFILES:
            profile = 'clean_scan'

        if profile == 'noisy_scan':
            denoised = cv2.medianBlur(gray, 3)
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                35,
                5,
            )
            kernel = np.ones((1, 1), np.uint8)
            return cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        if profile == 'mobile_photo':
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            normalized = clahe.apply(gray)
            denoised = cv2.GaussianBlur(normalized, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                41,
                7,
            )
            return cv2.resize(thresh, None, fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)

        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            8,
        )
        scaled = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        return cv2.morphologyEx(scaled, cv2.MORPH_OPEN, kernel)
