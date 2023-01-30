import base64
import cv2
from io import BytesIO
import numpy as np
from pathlib import Path


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


def b64_encode_img(img):
    """Decodes a b64 encoded image

    Args:
        img (Mat): cv2 image

    Returns:
        [str]: base64 encoded image
    """
    return str(base64.b64encode(cv2.imencode(".jpg", img)[1]))[2:-1]


def b64_decode_audio(audio):
    """Decodes a b64 encoded audio

    Args:
        audio (bytes): base64 encoded audio

    Returns:
        Mat: audio
    """
    return "something"


def b64_encode_audio(audio):
    """Decodes a b64 encoded audio

    Args:
        audio (Mat): cv2 audio

    Returns:
        [str]: base64 encoded audio
    """
    return "something"
