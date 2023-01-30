from fastapi import FastAPI, Request, status, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from io import BytesIO
from pydantic import Field, validator, BaseModel
import PIL
from PIL import Image
from typing import Union

from logging_utils import api_logger
from utilities import b64_decode_img, b64_decode_audio
from translation_utils import translate
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
    {
        "name": "translate_audio",
        "description": "Takes a base64 encoded audio file in any language, transcribes it, then translates it into English, and returns the translation",
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


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


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


def valid_b64_audio(b64_audio):
    try:
        audio = b64_decode_audio(b64_audio)
    except Exception as err:
        api_logger.logger.error("Invalid base64 string")
        api_logger.logger.exception(err)
        raise ValueError("Invalid base64 string")

    if audio is None:
        raise ValueError("No audio/invalid audio found")

    return b64_audio


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


@app.post(
    "/detect-objects", response_model=DetectionResponseOut, tags=["detect_objects"]
)
def object_detection(detection_request:DetectionRequestIn):
    api_logger.logger.info("Object detection called")
    b64_image = detection_request.b64_image

    try:
        image = Image.fromarray(b64_decode_img(b64_image))

        result = detect_objects(image, save=True)
        api_logger.logger.info(f"Object detection results: {result}")

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
        response = DetectionResponseOut(detection_result=[{"ERROR":"An error occurred"}], errors=result)
        return response


@app.post(
    "/detect-objects-upload", response_model=DetectionResponseOut, tags=["detect_objects_upload"]
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
        response = DetectionResponseOut(detection_result=[{"ERROR":"An error occurred"}], errors=result)
        return response
    except Exception as e:
        api_logger.logger.error("Object detection failed")
        api_logger.logger.exception(e)
        result = {
            "error": str(e),
        }
        response = DetectionResponseOut(detection_result=[{"ERROR":"An error occurred"}], errors=result)
        return response


"""============Audio Translation============"""

class AudioTranslationRequestIn(BaseModel):
    b64_audio: Union[str, None]
    _validb64_audio = validator("b64_audio", allow_reuse=True)(valid_b64_audio)

    class Config:
        schema_extra = {
            "example": {
                "b64_audio": "Audio to be processed of format wav/mp3 encoded into a base 64 string",
            }
        }

class AudioTranslationRequestOut(BaseModel):
    detected_language: str
    translation: str
    errors: dict


@app.post(
    "/translate-audio",
    response_model=AudioTranslationRequestOut,
    tags=["translate_audio"],
)
def translate_audio(translation_request:AudioTranslationRequestIn):
    api_logger.logger.info("Translate audio called")
    b64_audio = translation_request.b64_audio

    try:
        decoded_audio = b64_decode_audio(b64_audio)

        detected_language, translation = translate(decoded_audio)

        api_logger.logger.info(f"Detected language: {detected_language}")
        api_logger.logger.info(f"Translation: {translation}")
        response = AudioTranslationRequestOut(
            detected_language=detected_language,
            translation=translation,
            errors={"Errors": "None"},
        )
        return response
    except Exception as e:
        api_logger.logger.error("Audio translation failed")
        api_logger.logger.exception(e)
        error = {
            "error": str(e),
        }
        response = AudioTranslationRequestOut(
            detected_language="", translation="", errors=error
        )
        return response

@app.post(
    "/translate-audio-upload",
    response_model=AudioTranslationRequestOut,
    tags=["translate_audio"],
)
def translate_audio(file: bytes = File(...)):
    api_logger.logger.info("Translate audio called")

    try:
        

        detected_language, translation = translate(decoded_audio)

        api_logger.logger.info(f"Detected language: {detected_language}")
        api_logger.logger.info(f"Translation: {translation}")
        response = AudioTranslationRequestOut(
            detected_language=detected_language,
            translation=translation,
            errors={"Errors": "None"},
        )
        return response
    except Exception as e:
        api_logger.logger.error("Audio translation failed")
        api_logger.logger.exception(e)
        error = {
            "error": str(e),
        }
        response = AudioTranslationRequestOut(
            detected_language="", translation="", errors=error
        )
        return response
