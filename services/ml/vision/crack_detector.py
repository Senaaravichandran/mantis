"""Crack detection in pavement and concrete imagery.

Integration point for fine-tuned vision models.
"""

from dataclasses import dataclass


@dataclass
class CrackDetectionResult:
    cracks_detected: bool
    crack_count: int
    max_crack_width_mm: float | None
    severity: str  # none, minor, moderate, severe
    confidence: float
    regions: list[dict]  # [{x, y, width, height, severity}]


class CrackDetector:
    """Detects cracks in infrastructure images.

    MVP stub — full implementation will use a fine-tuned ViT model
    trained on pavement and concrete crack datasets.
    """

    def detect(self, image_path: str) -> CrackDetectionResult:
        """Detect cracks in an infrastructure image.

        In the full implementation, this will:
        1. Preprocess the image (resize, normalize)
        2. Run through fine-tuned ViT model
        3. Post-process detections with NMS
        4. Measure crack widths using pixel calibration
        """
        return CrackDetectionResult(
            cracks_detected=False,
            crack_count=0,
            max_crack_width_mm=None,
            severity="none",
            confidence=0.0,
            regions=[],
        )
