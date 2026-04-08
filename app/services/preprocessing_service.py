import cv2
import numpy as np


class PreprocessingService:
    PROFILES = {
        'mobile_photo': {'blur': (3, 3), 'block_size': 31, 'c': 8, 'scale': 1.5},
        'scan_document': {'blur': (1, 1), 'block_size': 21, 'c': 5, 'scale': 1.2},
    }

    def pick_profiles(self, image) -> list[str]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        std_dev = float(np.std(gray))
        # Heuristic ranking: low contrast photos usually benefit from stronger mobile profile.
        if std_dev < 40:
            return ['mobile_photo', 'scan_document']
        return ['scan_document', 'mobile_photo']

    def preprocess_with_profile(self, image, profile_name: str):
        profile = self.PROFILES.get(profile_name, self.PROFILES['mobile_photo'])
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.GaussianBlur(gray, profile['blur'], 0)
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            profile['block_size'],
            profile['c'],
        )
        scaled = cv2.resize(thresh, None, fx=profile['scale'], fy=profile['scale'], interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        return cv2.morphologyEx(scaled, cv2.MORPH_OPEN, kernel)

    def preprocess(self, image):
        ranked = self.pick_profiles(image)
        return self.preprocess_with_profile(image, ranked[0])
