import torch

from configs import RESOURCES

YOLO_MODEL = torch.hub.load("ultralytics/yolov5", "yolov5x", force_reload=True, verbose=False)


def detect_objects(image, save=False):
    """Given an image, find and detect all the objects in the image
    and return a dict containing each object's details

    Args:
        image (PIL.Image): image to be processed 

    Returns:
        dict: containing bbox coordinates and name of objects found in the image
        Example:
        [
            {'xmin': 128.9379119873047, 'ymin': 41.66037368774414, 'xmax': 194.33349609375, 'ymax': 161.2702178955078, 'confidence': 0.8801981210708618, 'class': 16, 'name': 'dog'}.
            {'xmin': 68.428955078125, 'ymin': 48.27406692504883, 'xmax': 134.3076171875, 'ymax': 156.50592041015625, 'confidence': 0.7833684682846069, 'class': 16, 'name': 'dog'}
        ]
    """

    results = YOLO_MODEL(image)

    # Saves the resulting image to "res/runs/exp#", for debugging purposes
    if save:
        results.save(save_dir=str(RESOURCES/"runs"/"exp"))

    results = results.pandas().xyxy[0].to_dict(orient="records")

    if not results: # If the model could not detect anything
        results = [{"detection_result": "Model could not detect any object in the image"}]

    return results
