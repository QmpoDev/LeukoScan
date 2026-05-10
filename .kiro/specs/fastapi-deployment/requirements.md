# Requirements Document

## Introduction

This feature adds a FastAPI-based REST API to the blood cell image classification project (Finals Laboratory 1 — Event-Driven Programming). The API exposes a POST endpoint that accepts an uploaded blood cell image and returns the model's predicted class and confidence score, integrating directly with the existing `classify_image()` function from `classify.py` and the trained `.keras` models in `saved_model/`.

## Glossary

- **API**: The FastAPI application that serves the blood cell classification endpoint.
- **Classifier**: The component that loads a trained Keras model and runs inference on a preprocessed image, implemented in `classify.py`.
- **Model**: A trained Keras model file (`.keras`) stored in `saved_model/`, used by the Classifier to predict blood cell type.
- **Prediction_Response**: The JSON object returned by the API containing the predicted class label and confidence score.
- **Client**: Any HTTP client (browser, curl, Swagger UI, test script) that sends requests to the API.
- **Image_File**: A JPEG or PNG image uploaded by the Client representing a blood cell microscopy image.
- **Class_Label**: One of the four blood cell type strings: `"Eosinophil"`, `"Lymphocyte"`, `"Monocyte"`, or `"Neutrophil"`.
- **Confidence_Score**: A floating-point value in the range [0.0, 1.0] representing the model's probability for the predicted class.

---

## Requirements

### Requirement 1: POST Endpoint for Image Classification

**User Story:** As a student demonstrating the lab project, I want to send a blood cell image to a POST endpoint and receive the model's predicted class, so that I can show the trained model working through an API.

#### Acceptance Criteria

1. THE API SHALL expose a POST endpoint at the path `/predict`.
2. WHEN a Client sends a POST request to `/predict` with a valid Image_File, THE API SHALL return a Prediction_Response containing the Class_Label and Confidence_Score.
3. WHEN a Client sends a POST request to `/predict` with a valid Image_File, THE Classifier SHALL preprocess the image by resizing it to 150×150 pixels and normalizing pixel values to the range [0.0, 1.0].
4. WHEN the Classifier produces a prediction, THE API SHALL return the Prediction_Response as a JSON object with the fields `predicted_class` (string) and `confidence` (float rounded to 4 decimal places).
5. THE API SHALL accept Image_File uploads using the `multipart/form-data` content type via a form field named `file`.

---

### Requirement 2: Model Loading and Selection

**User Story:** As a developer, I want the API to load a trained model at startup and optionally select between available models, so that inference is fast and the correct model is used.

#### Acceptance Criteria

1. WHEN the API starts, THE Classifier SHALL load the default Model (`saved_model/blood_cell_model_full.keras`) into memory once.
2. WHILE the Model is loaded, THE Classifier SHALL reuse the in-memory Model for all subsequent prediction requests without reloading from disk.
3. WHERE a `model` query parameter is provided in the request to `/predict`, THE API SHALL load and use the specified Model file from the `saved_model/` directory instead of the default.
4. IF the specified Model file does not exist in `saved_model/`, THEN THE API SHALL return an HTTP 404 response with a descriptive error message.
5. IF the default Model file (`saved_model/blood_cell_model_full.keras`) is not found at startup, THEN THE API SHALL log a warning and defer model loading until the first request.

---

### Requirement 3: Input Validation

**User Story:** As a developer, I want the API to validate uploaded files and reject invalid inputs, so that the Classifier does not receive malformed data.

#### Acceptance Criteria

1. IF a Client sends a POST request to `/predict` without a file, THEN THE API SHALL return an HTTP 422 response with a descriptive error message.
2. IF a Client uploads a file that is not a JPEG or PNG image, THEN THE API SHALL return an HTTP 400 response with the message `"Unsupported file type. Please upload a JPEG or PNG image."`.
3. IF the uploaded Image_File cannot be decoded as a valid image, THEN THE API SHALL return an HTTP 400 response with a descriptive error message.
4. THE API SHALL accept files with MIME types `image/jpeg` and `image/png`.

---

### Requirement 4: Health Check Endpoint

**User Story:** As a developer, I want a health check endpoint, so that I can verify the API is running before sending classification requests.

#### Acceptance Criteria

1. THE API SHALL expose a GET endpoint at the path `/health`.
2. WHEN a Client sends a GET request to `/health`, THE API SHALL return an HTTP 200 response with a JSON body `{"status": "ok"}`.

---

### Requirement 5: Interactive API Documentation

**User Story:** As a student demonstrating the lab, I want to access auto-generated API documentation in the browser, so that I can test the endpoint interactively without writing code.

#### Acceptance Criteria

1. THE API SHALL serve interactive Swagger UI documentation at the path `/docs`.
2. WHEN a Client navigates to `/docs`, THE API SHALL display the `/predict` and `/health` endpoints with their request and response schemas.
3. THE API SHALL serve ReDoc documentation at the path `/redoc`.

---

### Requirement 6: Error Handling

**User Story:** As a developer, I want the API to handle unexpected errors gracefully, so that the server does not crash and the Client receives a meaningful response.

#### Acceptance Criteria

1. IF an unhandled exception occurs during prediction, THEN THE API SHALL return an HTTP 500 response with a JSON body containing an `"error"` field describing the failure.
2. WHILE processing a request, THE API SHALL log all exceptions with their stack traces to standard output.
3. IF the Classifier raises an exception during inference, THEN THE API SHALL return an HTTP 500 response and THE API SHALL remain available to process subsequent requests.
