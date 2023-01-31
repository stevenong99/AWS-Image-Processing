import sys
import json
import unittest
from fastapi.testclient import TestClient
from pathlib import Path
from PIL import UnidentifiedImageError
from unittest.mock import patch


sys.path.append(str(Path(__file__).parent.parent))

from main import app


class Test_Main(unittest.TestCase):
    def setUp(self):
        RESOURCES = Path(__file__).parent / "res"
        self.image_2_dogs = open(str(RESOURCES / "2dogs.jpg"), "rb")
        self.image_empty = open(str(RESOURCES / "empty.png"), "rb")
        with open(str(RESOURCES / "2cats.json"), "r") as file:
            self.request_2_cats_base64 = file.read()
        with open(str(RESOURCES / "error.json"), "r") as file:
            self.error = file.read()

    def tearDown(self):
        self.image_2_dogs.close()
        self.image_empty.close()

    def test_index(self):
        with TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)

    def test_object_detection(self):
        json_request = json.loads(self.request_2_cats_base64)
        with TestClient(app) as client:
            response = client.post("/detect-objects", json=json_request)
            detection_result = dict(response.json())["detection_result"]
            objects = [objects["name"] for objects in detection_result]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(objects.count("cat"), 2)

    @patch("main.detect_objects")
    def test_object_detection_exceptions(self, mock_detect_object):
        expected_response = {
            "detection_result": [{"ERROR": "An error occurred"}],
            "errors": {"error": "Mock exception"},
        }
        mock_detect_object.side_effect = Exception("Mock exception")
        with TestClient(app) as client:
            json_request = json.loads(self.request_2_cats_base64)
            response = client.post("/detect-objects", json=json_request)
            self.assertEqual(response.json(), expected_response)

    def test_object_detection_upload(self):
        with TestClient(app) as client:
            response = client.post(
                "/detect-objects-upload",
                files={"file": ("filename", self.image_2_dogs, "image/jpeg")},
            )
            detection_result = dict(response.json())["detection_result"]
            objects = [objects["name"] for objects in detection_result]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(objects.count("dog"), 2)

    @patch("main.detect_objects")
    def test_object_detection_exception(self, mock_detect_object):
        expected_response = {
            "detection_result": [{"ERROR": "An error occurred"}],
            "errors": {"error": "Mock exception"},
        }
        mock_detect_object.side_effect = Exception("Mock exception")
        with TestClient(app) as client:
            response = client.post(
                "/detect-objects-upload",
                files={"file": ("filename", self.image_2_dogs, "image/jpeg")},
            )
            self.assertEqual(response.json(), expected_response)

    @patch("PIL.Image.open")
    def test_object_detection_unsupported_format(self, mock_detect_object):
        expected_response = {
            "detection_result": [{"ERROR": "An error occurred"}],
            "errors": {"error": "File uploaded is not an image supported by PIL"},
        }
        mock_detect_object.side_effect = UnidentifiedImageError("Mock exception")
        with TestClient(app) as client:
            response = client.post(
                "/detect-objects-upload",
                files={"file": ("2dogs.jpg", self.image_2_dogs, "image/jpeg")},
            )
            self.assertEqual(response.json(), expected_response)

    def test_object_detection_empty(self):
        expected_response = [
            {"detection_result": "Model could not detect any object in the image"}
        ]
        with TestClient(app) as client:
            response = client.post(
                "/detect-objects-upload",
                files={"file": ("empty.png", self.image_empty, "image/jpeg")},
            )
            detection_result = dict(response.json())["detection_result"]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(detection_result, expected_response)

    def test_object_detection_error_b64(self):
        expected_response = {
            "detail": [
                {
                    "loc": ["body", "b64_image"],
                    "msg": "Invalid base64 string",
                    "type": "value_error",
                }
            ]
        }
        json_request = json.loads(self.error)
        with TestClient(app) as client:
            response = client.post("/detect-objects", json=json_request)
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json(), expected_response)
