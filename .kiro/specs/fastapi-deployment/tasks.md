# Tasks

## Task List

- [x] 1. Project setup and dependencies
  - [x] 1.1 Add `fastapi`, `uvicorn[standard]`, `python-multipart`, `tensorflow`, `pillow` to `requirements.txt` (or create a separate `requirements-api.txt`)
  - [x] 1.2 Verify `classify.py` is importable as a module (no `if __name__ == "__main__"` guard issues for `classify_image`)

- [x] 2. Create `ml-server.py` — application skeleton
  - [x] 2.1 Create `ml-server.py` with a FastAPI app instance, title, and description
  - [x] 2.2 Define Pydantic response models: `PredictionResponse`, `HealthResponse`, `ErrorResponse`
  - [x] 2.3 Implement the `lifespan` context manager that loads `saved_model/blood_cell_model_full.keras` at startup into `app.state.model`; log a warning and set `app.state.model = None` if the file is missing

- [x] 3. Implement `GET /health` endpoint
  - [x] 3.1 Add `GET /health` route that returns `{"status": "ok"}` with HTTP 200

- [x] 4. Implement `POST /predict` endpoint
  - [x] 4.1 Add `POST /predict` route accepting `file: UploadFile` (multipart form) and optional `model: str` query parameter
  - [x] 4.2 Validate `file.content_type` is `image/jpeg` or `image/png`; return HTTP 400 with `{"error": "Unsupported file type. Please upload a JPEG or PNG image."}` if not
  - [x] 4.3 If `model` query parameter is provided, resolve the path to `saved_model/<model>` and return HTTP 404 with `{"error": "Model file not found: <name>"}` if the file does not exist
  - [x] 4.4 Write uploaded bytes to a `NamedTemporaryFile` (with `delete=False` for Windows compatibility)
  - [x] 4.5 Call `classify_image(tmp_path, model_path)` from `classify.py`; use `app.state.model` path for the default model
  - [x] 4.6 Round `confidence` to 4 decimal places and return `PredictionResponse`
  - [x] 4.7 Wrap the entire prediction block in `try/except Exception`; log the traceback to stdout and return HTTP 500 with `{"error": "<message>"}` on failure
  - [x] 4.8 Add a `finally` block to `os.unlink` the temp file regardless of success or failure

- [x] 5. Error handling for corrupt images
  - [x] 5.1 Catch `PIL.UnidentifiedImageError` (and generic `Exception`) from `classify_image` when the image bytes cannot be decoded; return HTTP 400 with a descriptive error message

- [x] 6. Write unit and example-based tests (`tests/test_api.py`)
  - [x] 6.1 Set up `pytest` with FastAPI `TestClient`; mock `classify_image` using `unittest.mock.patch`
  - [x] 6.2 Test `GET /health` returns 200 and `{"status": "ok"}`
  - [x] 6.3 Test `POST /predict` with a missing file returns 422
  - [x] 6.4 Test `POST /predict` with an unsupported MIME type returns 400 with the exact error message
  - [x] 6.5 Test `POST /predict` with a valid mocked response returns 200 with `predicted_class` in CLASS_LABELS and `confidence` in [0.0, 1.0]
  - [x] 6.6 Test `POST /predict` with a non-existent `model` query param returns 404
  - [x] 6.7 Test `POST /predict` when `classify_image` raises an exception returns 500 with an `"error"` field
  - [x] 6.8 Test that a second valid request after a 500 still returns 200 (server resilience)
  - [x] 6.9 Test `GET /openapi.json` contains `/predict` and `/health` paths

- [x] 7. Write property-based tests (`tests/test_properties.py`)
  - [x] 7.1 Property 1 — For any mocked (label, confidence) pair from valid label set × [0,1], response `predicted_class` is in CLASS_LABELS and `confidence` is in [0.0, 1.0] (min 100 iterations)
  - [x] 7.2 Property 2 — For any mocked confidence float in [0,1], `round(response["confidence"], 4) == response["confidence"]` (min 100 iterations)
  - [x] 7.3 Property 3 — For any MIME type string that is not `image/jpeg` or `image/png`, POST /predict returns 400 with the exact rejection message (min 100 iterations)
  - [x] 7.4 Property 4 — For any GET /health request variation, response is always 200 with `{"status": "ok"}` (min 100 iterations)
  - [x] 7.5 Property 5 — For any sequence of requests where some trigger a mocked exception, each failing request returns 500 with `"error"` and the next valid request returns 200 (min 100 iterations)
  - [x] 7.6 Property 6 — For any string that is not a real filename in `saved_model/`, POST /predict with that `model` param returns 404 with `"error"` (min 100 iterations)

- [ ] 8. Manual smoke test
  - [ ] 8.1 Start server with `uvicorn ml-server:app --reload` and confirm `/docs` loads in browser
  - [ ] 8.2 Use Swagger UI to upload a test image from `data_split_4000/TEST/` and verify a valid prediction response
  - [ ] 8.3 Confirm `/redoc` renders correctly
