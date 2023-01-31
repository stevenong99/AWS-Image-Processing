# AWS Object Detection
Simple FastAPI object detection service deployed in AWS EC2. As of this commit, the API can be accessed from here: http://54.251.190.86/

You can find sample images and their base64 counterparts here: [sample_images](sample_images/)

# POST Endpoint: http://54.251.190.86/detect-objects
Takes a base64 encoded image detects the objects within them, then returns the list of objects found in the image along with their bounding box coordinates.

## Supported image formats: jpeg/jpg/png

## Request Body
```
{
  "b64_image": "Image to be processed of format jpeg/jpg/png encoded into a base 64 string"
}
```

## Curl
```
curl -X 'POST' \
  'http://54.251.190.86/detect-objects' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "b64_image": "Image to be processed of format jpeg/jpg/png encoded into a base 64 string"
}'

  ```

## Expected Response
```
{
  "detection_result": [
                        {
                            "xmin": 128.9379119873047,
                            "ymin": 41.66037368774414,
                            "xmax": 194.33349609375,
                            "ymax": 161.2702178955078,
                            "confidence": 0.8801981210708618,
                            "class": 16,
                            "name": "dog",
                        },
                        {
                            "xmin": 68.428955078125,
                            "ymin": 48.27406692504883,
                            "xmax": 134.3076171875,
                            "ymax": 156.50592041015625,
                            "confidence": 0.7833684682846069,
                            "class": 16,
                            "name": "dog",
                        }
                    ],
  "errors": {}
}
```

## Validation Error Response
```
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```


# POST Endpoint: http://54.251.190.86/detect-objects-upload
Allows uploading of an image instead of base64. Takes a base64 encoded image detects the objects within them, then returns the list of objects found in the image along with their bounding box coordinates.

## Request Body
```
requires an uploaded image file
```

## Curl
```
curl -X 'POST' \
  'http://54.251.190.86/detect-objects-upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file='

  ```

## Expected Response
```
{
  "detection_result": [
                        {
                            "xmin": 128.9379119873047,
                            "ymin": 41.66037368774414,
                            "xmax": 194.33349609375,
                            "ymax": 161.2702178955078,
                            "confidence": 0.8801981210708618,
                            "class": 16,
                            "name": "dog",
                        },
                        {
                            "xmin": 68.428955078125,
                            "ymin": 48.27406692504883,
                            "xmax": 134.3076171875,
                            "ymax": 156.50592041015625,
                            "confidence": 0.7833684682846069,
                            "class": 16,
                            "name": "dog",
                        }
                    ],
  "errors": {}
}
```

## Validation Error Response
```
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

# Unit test coverage:
```
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
__init__.py                                0      0   100%
configs.py                                 5      0   100%
logging_utils.py                          38      3    92%   41, 43-44
main.py                                   97     10    90%   95, 101-111
object_detection_utils.py                 11      0   100%
startup.py                                 3      3     0%   1-4
tests/__init__.py                          0      0   100%
tests/test_main.py                        76      0   100%
tests/test_object_detection_utils.py      15      0   100%
utilities.py                               7      0   100%
--------------------------------------------------------------------
TOTAL                                    252     16    94%
```
