import numpy as np

from app.services.preprocessing_service import PreprocessingService


def test_pick_profiles_returns_ranked_candidates():
    service = PreprocessingService()
    image = np.full((120, 120, 3), 200, dtype=np.uint8)
    image[20:40, 20:100] = 20

    profiles = service.pick_profiles(image)

    assert len(profiles) == 2
    assert profiles[0] in service.PROFILES
    assert profiles[1] in service.PROFILES


def test_preprocess_with_profile_produces_binary_like_image():
    service = PreprocessingService()
    image = np.full((100, 140, 3), 255, dtype=np.uint8)
    image[20:80, 20:120] = 0

    processed = service.preprocess_with_profile(image, 'mobile_photo')

    assert processed.ndim == 2
    assert processed.shape[0] > 0 and processed.shape[1] > 0
