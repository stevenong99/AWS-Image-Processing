import sys
import unittest
from pathlib import Path

from object_detection_utils import detect_objects

sys.path.append(str(Path(__file__).parent.parent))

class Test_Object_Detection(unittest.TestCase):
    def setUp(self):
        RESOUCES = Path(__file__).parent/"res"
        self.test_image_path = RESOUCES/"2dogs.jpg"

    def tearDown(self):
        pass

    def test_detect_objects(self):
        ground_truth = [{'xmin': 128.9379119873047, 'ymin': 41.66037368774414, 'xmax': 194.33349609375, 'ymax': 161.2702178955078, 'confidence': 0.8801981210708618, 'class': 16, 'name': 'dog'}, {'xmin': 68.428955078125, 'ymin': 48.27406692504883, 'xmax': 134.3076171875, 'ymax': 156.50592041015625, 'confidence': 0.7833684682846069, 'class': 16, 'name': 'dog'}]
        result = detect_objects(self.test_image_path, save=True)
        self.assertEqual(ground_truth, result)

