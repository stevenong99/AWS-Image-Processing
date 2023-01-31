import base64
import cv2
import numpy as np


def b64_decode_img(img):
    """Decodes a b64 encoded image

    Args:
        img (bytes): base64 encoded image

    Returns:
        Mat: cv2 image
    """
    return cv2.imdecode(
        np.frombuffer(base64.b64decode(img), np.uint8), cv2.IMREAD_COLOR
    )
