import cv2
from fastapi import FastAPI, Request, status, File
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from io import BytesIO
from pydantic import validator, BaseModel
import PIL
from PIL import Image
from typing import Union

from logging_utils import api_logger
from utilities import b64_decode_img
from object_detection_utils import detect_objects

tags_metadata = [
    {
        "name": "index",
        "description": "redirects the user back to the docs",
    },
    {
        "name": "detect_objects",
        "description": "Takes a base64 encoded image detects the objects within them, then returns the list of objects found in the image along with their bounding box coordinates",
    },
    {
        "name": "detect_objects_upload",
        "description": "Allows uploading of an image instead of base64. Takes a base64 encoded image detects the objects within them, then returns the list of objects found in the image along with their bounding box coordinates",
    },
]


class ErrorList(BaseModel):
    msgText: str = ""
    msgCode: str = ""


app = FastAPI(
    title="AWS Test",
    version="0.0.1",
    description="APIs for deep learning functions",
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


"""============Setting Up the Documentation============"""

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    api_logger.logger.error(f"{request.body()}: {exc_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


"""============Image Validation Function============"""

def valid_b64_image(b64_image):
    try:
        img = b64_decode_img(b64_image)
    except Exception as e:
        api_logger.logger.error("Invalid base64 string")
        api_logger.logger.exception(e)
        raise ValueError("Invalid base64 string")

    if img is None:
        raise ValueError("No image/invalid image found")

    return b64_image


"""============Redirect to Docs============"""

@app.get("/", tags=["index"])
def index():
    api_logger.logger.info("Index page called")
    return RedirectResponse(url="/docs")


"""============Object Detection============"""

class DetectionRequestIn(BaseModel):
    b64_image: Union[str, None]
    _validb64_image = validator("b64_image", allow_reuse=True)(valid_b64_image)

    class Config:
        schema_extra = {
            "example": {
                "b64_image": "Image to be processed of format jpeg/jpg/png encoded into a base 64 string",
            }
        }


class DetectionResponseOut(BaseModel):
    detection_result: list[dict]
    errors: dict

# This endpoint takes images in the form of base64 strings
@app.post(
    "/detect-objects", response_model=DetectionResponseOut, tags=["detect_objects"]
)
def object_detection(detection_request: DetectionRequestIn):
    api_logger.logger.info("Object detection called")
    b64_image = detection_request.b64_image

    try:
        # Converting from base64 to PIL.Image
        image = Image.fromarray(cv2.cvtColor(b64_decode_img(b64_image), cv2.COLOR_BGR2RGB))

        # Object detection occurs here
        result = detect_objects(image, save=True)
        api_logger.logger.info(f"Object detection results: {result}")

        # The result is put into the response and sent back to the user
        response = DetectionResponseOut(
            detection_result=result, errors={"Errors": "None"}
        )
        return response
    except Exception as e:
        api_logger.logger.error("Object detection failed")
        api_logger.logger.exception(e)
        result = {
            "error": str(e),
        }
        # The error is returned if any kind of exception occurs
        response = DetectionResponseOut(
            detection_result=[{"ERROR": "An error occurred"}], errors=result
        )
        return response

# This endpoint takes images in the form of uploaded images in a multipart request
@app.post(
    "/detect-objects-upload",
    response_model=DetectionResponseOut,
    tags=["detect_objects_upload"],
)
def object_detection_upload(file: Union[bytes, None] = File(default=None)):
    api_logger.logger.info("Object detection called")

    try:
        image = Image.open(BytesIO(file)).convert("RGB")

        result = detect_objects(image, save=True)
        api_logger.logger.info(f"Object detection results: {result}")

        response = DetectionResponseOut(
            detection_result=result, errors={"Errors": "None"}
        )
        return response
    except PIL.UnidentifiedImageError as e:
        api_logger.logger.error("Object detection failed")
        api_logger.logger.exception(e)
        result = {
            "error": "File uploaded is not an image supported by PIL",
        }
        response = DetectionResponseOut(
            detection_result=[{"ERROR": "An error occurred"}], errors=result
        )
        return response
    except Exception as e:
        api_logger.logger.error("Object detection failed")
        api_logger.logger.exception(e)
        result = {
            "error": str(e),
        }
        response = DetectionResponseOut(
            detection_result=[{"ERROR": "An error occurred"}], errors=result
        )
        return response
