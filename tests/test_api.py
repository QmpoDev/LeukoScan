"""
Unit and example-based tests for the Blood Cell Classifier API (ml-server.py).

Task 6: Tests for GET /health, POST /predict, and OpenAPI schema.

Since tensorflow may not be installed in the test environment, we mock it
at the sys.modules level before importing ml-server so the import chain
(ml-server → classify → tensorflow) does not fail.

Note: unittest.mock.patch() does not accept module names containing hyphens
(e.g. "ml-server.classify_image") because the hyphen is not a valid Python
identifier character.  We use patch.object(ml_server, "classify_image", ...)
instead, which patches the name directly on the already-imported module object.
"""
import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# 6.1 — Stub out tensorflow and keras before importing ml-server / classify
# ---------------------------------------------------------------------------

def _make_tf_stub():
    """Return a minimal tensorflow stub that satisfies classify.py's imports."""
    tf = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    preprocessing = types.ModuleType("tensorflow.keras.preprocessing")
    image_mod = types.ModuleType("tensorflow.keras.preprocessing.image")

    # image.load_img / img_to_array stubs (never called in unit tests)
    image_mod.load_img = MagicMock()
    image_mod.img_to_array = MagicMock()

    # tf.keras.models.load_model stub
    models = types.ModuleType("tensorflow.keras.models")
    models.load_model = MagicMock()
    keras.models = models
    keras.preprocessing = preprocessing
    preprocessing.image = image_mod
    tf.keras = keras

    return tf


# Register stubs before any import of classify or ml-server
_tf_stub = _make_tf_stub()
sys.modules.setdefault("tensorflow", _tf_stub)
sys.modules.setdefault("tensorflow.keras", _tf_stub.keras)
sys.modules.setdefault("tensorflow.keras.models", _tf_stub.keras.models)
sys.modules.setdefault("tensorflow.keras.preprocessing", _tf_stub.keras.preprocessing)
sys.modules.setdefault("tensorflow.keras.preprocessing.image", _tf_stub.keras.preprocessing.image)

# numpy stub (used in classify.py)
if "numpy" not in sys.modules:
    np_stub = types.ModuleType("numpy")
    np_stub.expand_dims = MagicMock(return_value=MagicMock())
    np_stub.argmax = MagicMock(return_value=0)
    sys.modules["numpy"] = np_stub

# ---------------------------------------------------------------------------
# Import app from ml-server.py (hyphenated filename requires importlib)
# ---------------------------------------------------------------------------
ml_server = importlib.import_module("ml-server")
app = ml_server.app
CLASS_LABELS = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


# Convenience: minimal valid upload tuples
VALID_JPEG = ("test.jpg", b"fake-image-bytes", "image/jpeg")
VALID_PNG  = ("test.png", b"fake-image-bytes", "image/png")

# Default mock return value for classify_image
MOCK_LABEL      = "Lymphocyte"
MOCK_CONFIDENCE = 0.9876


# ---------------------------------------------------------------------------
# 6.2 — GET /health returns 200 and {"status": "ok"}
# ---------------------------------------------------------------------------

def test_health_returns_200_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# 6.3 — POST /predict with a missing file returns 422
# ---------------------------------------------------------------------------

def test_predict_missing_file_returns_422(client):
    response = client.post("/predict")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 6.4 — POST /predict with an unsupported MIME type returns 400
# ---------------------------------------------------------------------------

def test_predict_unsupported_mime_returns_400(client):
    response = client.post(
        "/predict",
        files={"file": ("test.gif", b"fake-gif-bytes", "image/gif")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "Unsupported file type. Please upload a JPEG or PNG image."


# ---------------------------------------------------------------------------
# 6.5 — POST /predict with a valid mocked response returns 200
# ---------------------------------------------------------------------------

def test_predict_valid_jpeg_returns_200(client):
    with patch.object(ml_server, "classify_image", return_value=(MOCK_LABEL, MOCK_CONFIDENCE)):
        response = client.post(
            "/predict",
            files={"file": VALID_JPEG},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in CLASS_LABELS
    assert 0.0 <= body["confidence"] <= 1.0


def test_predict_valid_png_returns_200(client):
    with patch.object(ml_server, "classify_image", return_value=("Eosinophil", 0.7531)):
        response = client.post(
            "/predict",
            files={"file": VALID_PNG},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in CLASS_LABELS
    assert 0.0 <= body["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# 6.6 — POST /predict with a non-existent model query param returns 404
# ---------------------------------------------------------------------------

def test_predict_nonexistent_model_returns_404(client):
    response = client.post(
        "/predict",
        files={"file": VALID_JPEG},
        params={"model": "nonexistent_model.keras"},
    )
    assert response.status_code == 404
    body = response.json()
    assert "error" in body


# ---------------------------------------------------------------------------
# 6.7 — POST /predict when classify_image raises an exception returns 500
# ---------------------------------------------------------------------------

def test_predict_classify_exception_returns_500(client):
    with patch.object(ml_server, "classify_image", side_effect=RuntimeError("model exploded")):
        response = client.post(
            "/predict",
            files={"file": VALID_JPEG},
        )
    assert response.status_code == 500
    body = response.json()
    assert "error" in body


# ---------------------------------------------------------------------------
# 6.8 — Server resilience: a second valid request after a 500 still returns 200
# ---------------------------------------------------------------------------

def test_server_resilience_after_500(client):
    # First request: classify_image raises → 500
    with patch.object(ml_server, "classify_image", side_effect=ValueError("boom")):
        r1 = client.post("/predict", files={"file": VALID_JPEG})
    assert r1.status_code == 500

    # Second request: classify_image works normally → 200
    with patch.object(ml_server, "classify_image", return_value=(MOCK_LABEL, MOCK_CONFIDENCE)):
        r2 = client.post("/predict", files={"file": VALID_JPEG})
    assert r2.status_code == 200
    body = r2.json()
    assert body["predicted_class"] in CLASS_LABELS
    assert 0.0 <= body["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# 6.9 — GET /openapi.json contains /predict and /health paths
# ---------------------------------------------------------------------------

def test_openapi_json_contains_predict_and_health(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/predict" in paths, "/predict not found in OpenAPI schema"
    assert "/health" in paths, "/health not found in OpenAPI schema"
