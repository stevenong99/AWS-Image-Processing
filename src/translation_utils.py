import whisper
import torch

from configs import RESOURCES

device = "cuda" if torch.cuda.is_available() else "cpu"

# Model names: tiny base small medium large-v1 large-v2
WHISPER_MODEL = whisper.load_model(
    "base", device="cpu", download_root=RESOURCES / "models"
)


def translate(audioPath, lang="en"):
    transcription = WHISPER_MODEL.transcribe(
        audioPath, language=lang, condition_on_previous_text=False, task="translate"
    )
    return transcription
