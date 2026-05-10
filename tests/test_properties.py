"""
Property-based tests for the Blood Cell Classifier API (ml-server.py).

Task 7: Six Hypothesis property tests covering correctness properties
defined in the design document.

The tensorflow stub pattern is reused from tests/test_api.py.
We use sys.modules.setdefault() to avoid re-registering stubs if
test_api.py has already been imported in the same pytest session.
"""
import importlib
import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Stub out tensorflow and keras before importing ml-server / classify
# (same pattern as test_api.py — use setdefault to avoid double-registration)
# ---------------------------------------------------------------------------

def _make_tf_stub():
    """Return a minimal tensorflow stub that satisfies classify.py's imports."""
    tf = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    preprocessing = types.ModuleType("tensorflow.keras.preprocessing")
    image_mod = types.ModuleType("tensorflow.keras.preprocessing.image")

    image_mod.load_img = MagicMock()
    image_mod.img_to_array = MagicMock()

    models = types.ModuleType("tensorflow.keras.models")
    models.load_model = MagicMock()
    keras.models = models
    keras.preprocessing = preprocessing
    preprocessing.image = image_mod
    tf.keras = keras

    return tf


def _make_numpy_stub():
    """Return a numpy stub that satisfies both classify.py and Hypothesis internals."""
    np_stub = types.ModuleType("numpy")
    np_stub.__path__ = []  # make it look like a package so sub-imports work
    np_stub.__package__ = "numpy"
    np_stub.expand_dims = MagicMock(return_value=MagicMock())
    np_stub.argmax = MagicMock(return_value=0)

    # Hypothesis checks for numpy.ndarray
    np_stub.ndarray = type("ndarray", (), {})

    # Hypothesis imports numpy.random and calls get_state/set_state/seed
    # Provide a stub that satisfies the NumpyRandomWrapper in hypothesis.internal.entropy
    _state = {"state": None}

    def _get_state():
        return _state["state"]

    def _set_state(s):
        _state["state"] = s

    def _seed(s=None):
        pass

    random_stub = types.ModuleType("numpy.random")
    random_stub.seed = _seed
    random_stub.get_state = _get_state
    random_stub.set_state = _set_state
    random_stub.RandomState = MagicMock()
    np_stub.random = random_stub
    sys.modules["numpy.random"] = random_stub

    return np_stub


# Only register stubs if not already present (avoids double-registration
# when test_api.py is collected in the same pytest session)
if "tensorflow" not in sys.modules:
    _tf_stub = _make_tf_stub()
    sys.modules["tensorflow"] = _tf_stub
    sys.modules["tensorflow.keras"] = _tf_stub.keras
    sys.modules["tensorflow.keras.models"] = _tf_stub.keras.models
    sys.modules["tensorflow.keras.preprocessing"] = _tf_stub.keras.preprocessing
    sys.modules["tensorflow.keras.preprocessing.image"] = _tf_stub.keras.preprocessing.image
else:
    sys.modules.setdefault("tensorflow.keras", sys.modules["tensorflow"].keras)
    sys.modules.setdefault("tensorflow.keras.models", sys.modules["tensorflow"].keras.models)
    sys.modules.setdefault("tensorflow.keras.preprocessing", sys.modules["tensorflow"].keras.preprocessing)
    sys.modules.setdefault("tensorflow.keras.preprocessing.image", sys.modules["tensorflow"].keras.preprocessing.image)

if "numpy" not in sys.modules:
    _np_stub = _make_numpy_stub()
    sys.modules["numpy"] = _np_stub
else:
    # Ensure numpy.random sub-module is registered even if numpy was already stubbed
    existing_np = sys.modules["numpy"]
    if not hasattr(existing_np, "ndarray"):
        existing_np.ndarray = type("ndarray", (), {})
    if "numpy.random" not in sys.modules:
        _state = {"state": None}
        random_stub = types.ModuleType("numpy.random")
        random_stub.seed = lambda s=None: None
        random_stub.get_state = lambda: _state["state"]
        random_stub.set_state = lambda s: _state.update({"state": s})
        random_stub.RandomState = MagicMock()
        existing_np.random = random_stub
        sys.modules["numpy.random"] = random_stub
    else:
        # Ensure get_state/set_state exist on the already-registered stub
        existing_random = sys.modules["numpy.random"]
        if not hasattr(existing_random, "get_state"):
            _state = {"state": None}
            existing_random.get_state = lambda: _state["state"]
            existing_random.set_state = lambda s: _state.update({"state": s})
            existing_random.seed = lambda s=None: None

# ---------------------------------------------------------------------------
# Import app from ml-server.py (hyphenated filename requires importlib)
# ---------------------------------------------------------------------------
ml_server = importlib.import_module("ml-server")
app = ml_server.app
CLASS_LABELS = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

VALID_JPEG = ("test.jpg", b"fake-image-bytes", "image/jpeg")
VALID_PNG  = ("test.png", b"fake-image-bytes", "image/png")


# ---------------------------------------------------------------------------
# Property 1 — Prediction response fields are always valid
#
# For any mocked (label, confidence) pair from valid label set × [0,1],
# response predicted_class is in CLASS_LABELS and confidence is in [0.0, 1.0].
#
# Validates: Requirements 1.2, 1.4
# ---------------------------------------------------------------------------

@given(
    label=st.sampled_from(CLASS_LABELS),
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_property1_prediction_response_fields_always_valid(label, confidence):
    """**Validates: Requirements 1.2, 1.4**"""
    with TestClient(app) as client:
        with patch.object(ml_server, "classify_image", return_value=(label, confidence)):
            response = client.post(
                "/predict",
                files={"file": VALID_JPEG},
            )
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in CLASS_LABELS
    assert 0.0 <= body["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# Property 2 — Confidence is always rounded to 4 decimal places
#
# For any mocked confidence float in [0,1],
# round(response["confidence"], 4) == response["confidence"].
#
# Validates: Requirements 1.4
# ---------------------------------------------------------------------------

@given(
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_property2_confidence_always_rounded_to_4_decimal_places(confidence):
    """**Validates: Requirements 1.4**"""
    with TestClient(app) as client:
        with patch.object(ml_server, "classify_image", return_value=("Lymphocyte", confidence)):
            response = client.post(
                "/predict",
                files={"file": VALID_JPEG},
            )
    assert response.status_code == 200
    body = response.json()
    returned_confidence = body["confidence"]
    assert round(returned_confidence, 4) == returned_confidence


# ---------------------------------------------------------------------------
# Property 3 — Unsupported MIME types are always rejected with HTTP 400
#
# For any MIME type string that is not image/jpeg or image/png,
# POST /predict returns 400 with the exact rejection message.
#
# Validates: Requirements 3.2, 3.4
# ---------------------------------------------------------------------------

@given(
    mime_type=st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd"),
            whitelist_characters="/-+.",
        ),
        min_size=1,
    ).filter(lambda x: x not in {"image/jpeg", "image/png"}),
)
@settings(max_examples=100)
def test_property3_unsupported_mime_types_always_rejected_with_400(mime_type):
    """**Validates: Requirements 3.2, 3.4**"""
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("test.img", b"fake-image-bytes", mime_type)},
        )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "Unsupported file type. Please upload a JPEG or PNG image."


# ---------------------------------------------------------------------------
# Property 4 — Health endpoint always returns {"status": "ok"}
#
# For any GET /health request, response is always 200 with {"status": "ok"}.
# We use st.integers() as a dummy draw to satisfy @given, then call /health
# 100 times total across all examples.
#
# Validates: Requirements 4.1, 4.2
# ---------------------------------------------------------------------------

@given(st.integers())
@settings(max_examples=100)
def test_property4_health_endpoint_always_returns_ok(_dummy):
    """**Validates: Requirements 4.1, 4.2**"""
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Property 5 — Inference exceptions always produce HTTP 500 and server remains available
#
# For any sequence of requests where some trigger a mocked exception,
# each failing request returns 500 with "error" and the next valid request
# returns 200.
#
# Validates: Requirements 6.1, 6.3
# ---------------------------------------------------------------------------

@given(
    request_sequence=st.lists(st.booleans(), min_size=1, max_size=10),
)
@settings(max_examples=100)
def test_property5_inference_exceptions_produce_500_server_remains_available(request_sequence):
    """**Validates: Requirements 6.1, 6.3**

    True in the sequence = raise exception (expect 500)
    False in the sequence = valid request (expect 200)
    After the full sequence, a final valid request must return 200.
    """
    with TestClient(app) as client:
        for should_raise in request_sequence:
            if should_raise:
                with patch.object(
                    ml_server, "classify_image", side_effect=RuntimeError("inference error")
                ):
                    response = client.post("/predict", files={"file": VALID_JPEG})
                assert response.status_code == 500
                body = response.json()
                assert "error" in body
            else:
                with patch.object(
                    ml_server, "classify_image", return_value=("Neutrophil", 0.8765)
                ):
                    response = client.post("/predict", files={"file": VALID_JPEG})
                assert response.status_code == 200

        # After the sequence, a final valid request must still return 200
        with patch.object(
            ml_server, "classify_image", return_value=("Eosinophil", 0.9123)
        ):
            final_response = client.post("/predict", files={"file": VALID_JPEG})
        assert final_response.status_code == 200
        final_body = final_response.json()
        assert final_body["predicted_class"] in CLASS_LABELS
        assert 0.0 <= final_body["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# Property 6 — Non-existent model files always produce HTTP 404
#
# For any string that is not a real filename in saved_model/,
# POST /predict with that model param returns 404 with "error".
#
# Validates: Requirements 2.4
# ---------------------------------------------------------------------------

@given(
    model_name=st.text(min_size=1, max_size=50).filter(
        lambda s: not os.path.exists(os.path.join("saved_model", s))
    ),
)
@settings(max_examples=100)
def test_property6_nonexistent_model_always_returns_404(model_name):
    """**Validates: Requirements 2.4**"""
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": VALID_JPEG},
            params={"model": model_name},
        )
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
