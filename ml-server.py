
import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from classify import CLASS_LABELS, classify_image


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


DEFAULT_MODEL_PATH = "saved_model/blood_cell_model_full.keras"

SUPPORTED_CONTENT_TYPES = {"image/jpeg", "image/png"}


CONTENT_TYPE_SUFFIX = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}



class PredictionResponse(BaseModel):
    """Successful prediction result."""

    predicted_class: str  # one of CLASS_LABELS
    confidence: float     # rounded to 4 decimal places, range [0.0, 1.0]


class HealthResponse(BaseModel):
    """Liveness check response."""

    status: str  # always "ok"


class ErrorResponse(BaseModel):
    """Structured error body returned on 4xx / 5xx responses."""

    error: str  # human-readable description


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.

    On startup:
      - Stores the default model path in app.state.model_path so that
        /predict can pass it to classify_image().
      - classify_image() handles its own model loading internally, so we
        only need to verify the file exists and record the path.
      - If the file is missing, logs a warning and sets model_path to None;
        classify_image() will fall back to its own DEFAULT_MODEL constant.

    On shutdown:
      - Nothing to clean up (no persistent resources held here).
    """
    model_path = DEFAULT_MODEL_PATH
    if Path(model_path).exists():
        logger.info("Default model found at '%s'. Ready for inference.", model_path)
        app.state.model = True          # sentinel: model file is present
        app.state.model_path = model_path
    else:
        logger.warning(
            "WARNING: Default model not found at %s. "
            "Model will be loaded on first request.",
            model_path,
        )
        app.state.model = None
        app.state.model_path = None

    yield  # application runs here

    # Shutdown — nothing to release
    logger.info("Shutting down Blood Cell Classifier API.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Blood Cell Classifier API",
    description=(
        "REST API for blood cell image classification. "
        "POST a JPEG or PNG microscopy image to /predict and receive the "
        "predicted cell type (Eosinophil, Lymphocyte, Monocyte, or Neutrophil) "
        "together with the model's confidence score. "
        "Use the optional `model` query parameter to select an alternative "
        "Keras model from the saved_model/ directory."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns HTTP 200 with `{\"status\": \"ok\"}` when the server is running.",
)
async def health() -> HealthResponse:
    """Return a simple liveness response."""
    return HealthResponse(status="ok")


# ---------------------------------------------------------------------------
# Predict endpoint
# ---------------------------------------------------------------------------


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type or corrupt image"},
        404: {"model": ErrorResponse, "description": "Requested model file not found"},
        500: {"model": ErrorResponse, "description": "Unexpected server error during inference"},
    },
    summary="Classify a blood cell image",
    description=(
        "Upload a JPEG or PNG blood cell image and receive the predicted class "
        "label and confidence score. Optionally specify a `model` filename "
        "(relative to `saved_model/`) to use a non-default Keras model."
    ),
)
async def predict(
    file: UploadFile = File(..., description="Blood cell image (JPEG or PNG)"),
    model: Optional[str] = Query(
        default=None,
        description="Filename of an alternative model inside saved_model/ (e.g. blood_cell_model_4000.keras)",
    ),
) -> JSONResponse:
    """
    Classify an uploaded blood cell image.

    Steps:
      1. Validate MIME type (JPEG or PNG only).
      2. If `model` query param is given, resolve and validate the path.
      3. Write uploaded bytes to a NamedTemporaryFile (delete=False for Windows).
      4. Call classify_image(tmp_path, model_path).
      5. Round confidence to 4 decimal places and return PredictionResponse.
      6. Always delete the temp file in a finally block.
    """
    # ------------------------------------------------------------------
    # 4.2 — Validate content type
    # ------------------------------------------------------------------
    content_type = file.content_type
    if content_type not in SUPPORTED_CONTENT_TYPES:
        return JSONResponse(
            status_code=400,
            content={"error": "Unsupported file type. Please upload a JPEG or PNG image."},
        )

    # ------------------------------------------------------------------
    # 4.3 — Resolve custom model path (if provided)
    # ------------------------------------------------------------------
    if model is not None:
        custom_model_path = os.path.join("saved_model", model)
        if not os.path.exists(custom_model_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"Model file not found: {model}"},
            )
        model_path = custom_model_path
    else:
        # Use the default model path recorded at startup (may be None if
        # the file was missing; classify_image() will use its own default).
        model_path = app.state.model_path

    # ------------------------------------------------------------------
    # 4.4 — Write uploaded bytes to a NamedTemporaryFile
    # ------------------------------------------------------------------
    suffix = CONTENT_TYPE_SUFFIX[content_type]
    tmp_path: Optional[str] = None

    try:
        # Read all bytes from the upload
        image_bytes = await file.read()

        # Create temp file with delete=False for Windows compatibility
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        # ------------------------------------------------------------------
        # 5.1 — Catch PIL.UnidentifiedImageError specifically (before generic
        #        Exception) and return HTTP 400 with a descriptive message.
        # ------------------------------------------------------------------
        try:
            from PIL import UnidentifiedImageError  # noqa: PLC0415

            pil_error = UnidentifiedImageError
        except ImportError:
            pil_error = None  # type: ignore[assignment]

        try:
            # ------------------------------------------------------------------
            # 4.5 — Call classify_image with the resolved model path
            # ------------------------------------------------------------------
            predicted_label, confidence = classify_image(tmp_path, model_path)

            # ------------------------------------------------------------------
            # 4.6 — Round confidence and return PredictionResponse
            # ------------------------------------------------------------------
            rounded_confidence = round(confidence, 4)
            return JSONResponse(
                status_code=200,
                content={
                    "predicted_class": predicted_label,
                    "confidence": rounded_confidence,
                },
            )

        except Exception as exc:  # noqa: BLE001
            # ------------------------------------------------------------------
            # 5.1 — PIL.UnidentifiedImageError → HTTP 400
            # ------------------------------------------------------------------
            if pil_error is not None and isinstance(exc, pil_error):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": (
                            "Could not decode image. "
                            "Please upload a valid JPEG or PNG file."
                        )
                    },
                )

            # ------------------------------------------------------------------
            # 4.7 — Generic exception → HTTP 500; log full traceback
            # ------------------------------------------------------------------
            logger.error("Unhandled exception during inference: %s", exc, exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": str(exc)},
            )

    finally:
        # ------------------------------------------------------------------
        # 4.8 — Always delete the temp file
        # ------------------------------------------------------------------
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError as cleanup_err:
                logger.warning("Could not delete temp file %s: %s", tmp_path, cleanup_err)


# ---------------------------------------------------------------------------
# Entry point (for direct execution, though uvicorn is preferred)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ml-server:app", host="0.0.0.0", port=8000, reload=True)
