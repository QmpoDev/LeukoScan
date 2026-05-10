# Requirements Document

## Introduction

This feature delivers **EventDP — Blood Cell Image Classification**, a full-stack web system that wraps the existing FastAPI inference backend (`ml-server.py` / `classify.py`) with a four-page React frontend. The system allows users to upload a blood cell microscopy image through a browser, receive a predicted cell type (Eosinophil, Lymphocyte, Monocyte, or Neutrophil) and a confidence score, and explore background information about the project. The backend is already implemented; this spec covers the CORS addition to the backend, the complete React frontend, a README, a technical summary document, and the test suites for both tiers.

## Glossary

- **API**: The FastAPI application (`ml-server.py`) that exposes `POST /predict` and `GET /health`.
- **Frontend**: The React single-page application served on a separate development port (default 5173).
- **Classifier**: The CNN inference pipeline in `classify.py` that loads a Keras model and returns a class label and confidence score.
- **Class_Label**: One of the four blood cell type strings: `"Eosinophil"`, `"Lymphocyte"`, `"Monocyte"`, or `"Neutrophil"`.
- **Confidence_Score**: A floating-point value in [0.0, 1.0] representing the model's probability for the predicted class, rounded to 4 decimal places.
- **Prediction_Response**: The JSON object `{ "predicted_class": string, "confidence": float }` returned by `POST /predict`.
- **Image_File**: A JPEG or PNG image uploaded by the User representing a blood cell microscopy image.
- **User**: A person interacting with the Frontend in a web browser.
- **FormData**: The browser `FormData` object used to encode the Image_File for transmission to the API, with the field name `file`.
- **CORS**: Cross-Origin Resource Sharing — the HTTP mechanism that allows the Frontend (on port 5173) to call the API (on port 8000).
- **Result_Card**: The UI component that displays the Class_Label and a visual confidence percentage bar after a successful prediction.
- **Drop_Zone**: The drag-and-drop file upload area on the Prediction page.
- **Router**: React Router, used to navigate between the four pages without a full page reload.

---

## Requirements

### Requirement 1: CORS Middleware on the FastAPI Backend

**User Story:** As a developer, I want the FastAPI backend to allow cross-origin requests from the React frontend, so that the browser does not block API calls made from a different port.

#### Acceptance Criteria

1. THE API SHALL include `fastapi.middleware.cors.CORSMiddleware` in its middleware stack.
2. WHEN the Frontend sends a preflight `OPTIONS` request to any API endpoint, THE API SHALL respond with the appropriate CORS headers permitting the request.
3. THE API SHALL allow requests from all origins (`"*"`) for development purposes.
4. THE API SHALL allow the HTTP methods `GET`, `POST`, and `OPTIONS`.
5. THE API SHALL allow all request headers.

---

### Requirement 2: React Application Structure and Navigation

**User Story:** As a User, I want to navigate between four distinct pages — Home, About, Features, and Prediction — without a full page reload, so that the application feels fast and cohesive.

#### Acceptance Criteria

1. THE Frontend SHALL contain exactly four pages: Home, About, Features, and Prediction.
2. THE Frontend SHALL use React Router to manage client-side navigation between pages.
3. WHEN a User clicks a navigation link, THE Router SHALL render the target page without triggering a full browser reload.
4. THE Frontend SHALL display a persistent navigation bar on all four pages containing links to each page.
5. THE Frontend SHALL apply Tailwind CSS utility classes throughout all pages and components for styling.
6. THE Frontend SHALL use Lucide-React icons in the navigation bar and on content pages.

---

### Requirement 3: Home Page

**User Story:** As a User, I want a landing page that introduces the project, so that I understand the purpose of the application before using it.

#### Acceptance Criteria

1. THE Frontend SHALL render a Home page at the `/` route.
2. THE Home page SHALL display the project name "EventDP — Blood Cell Image Classification" as the primary heading.
3. THE Home page SHALL include a brief description of the system's purpose: classifying blood cell images into one of four categories using a convolutional neural network.
4. THE Home page SHALL include a call-to-action element (button or link) that navigates the User to the Prediction page.
5. THE Home page SHALL use a medical/professional aesthetic with the following color palette applied via Tailwind CSS arbitrary-value classes:
   - Primary (deep navy `#172F7C`): navigation background, primary buttons, headings
   - Secondary (teal `#2DC6B2`): section backgrounds, card borders, secondary UI elements
   - Accent (cyan `#1CBDC9`): hover states, active navigation links, confidence bar fill
   - Success (mint green `#A2F9AB`): result card background, successful prediction accents
   - Error (coral `#F0756C`): error messages, invalid file type warnings

---

### Requirement 4: About Page

**User Story:** As a User, I want an About page that describes the project background and team, so that I can understand the academic context of the work.

#### Acceptance Criteria

1. THE Frontend SHALL render an About page at the `/about` route.
2. THE About page SHALL describe the academic context of the project (course name, laboratory assignment).
3. THE About page SHALL include team or author information.
4. THE About page SHALL describe the dataset used: blood cell microscopy images organized into four classes (Eosinophil, Lymphocyte, Monocyte, Neutrophil).
5. THE About page SHALL be styled with Tailwind CSS using the project color palette (`#172F7C`, `#2DC6B2`, `#1CBDC9`, `#A2F9AB`, `#F0756C`) consistent with the rest of the application.

---

### Requirement 5: Features Page

**User Story:** As a User, I want a Features page that explains the classification capabilities of the system, so that I know what the model can and cannot do.

#### Acceptance Criteria

1. THE Frontend SHALL render a Features page at the `/features` route.
2. THE Features page SHALL list the four supported blood cell classes: Eosinophil, Lymphocyte, Monocyte, and Neutrophil.
3. THE Features page SHALL include a brief description of each cell type.
4. THE Features page SHALL describe the model's input requirements: JPEG or PNG images, resized internally to 150×150 pixels.
5. THE Features page SHALL use Lucide-React icons to visually distinguish each feature item.
6. THE Features page SHALL be styled with Tailwind CSS using the project color palette (`#172F7C`, `#2DC6B2`, `#1CBDC9`, `#A2F9AB`, `#F0756C`) consistent with the rest of the application.

---

### Requirement 6: Prediction Page — File Upload

**User Story:** As a User, I want to upload a blood cell image through a drag-and-drop interface, so that I can submit an image for classification without navigating a complex form.

#### Acceptance Criteria

1. THE Frontend SHALL render a Prediction page at the `/predict` route.
2. THE Prediction page SHALL display a Drop_Zone that accepts file drops and click-to-browse file selection.
3. WHEN a User drags a file over the Drop_Zone, THE Drop_Zone SHALL provide a visual highlight indicating the drop target is active.
4. WHEN a User selects or drops a file, THE Frontend SHALL validate that the file's MIME type is `image/jpeg` or `image/png`.
5. IF a User selects or drops a file with an unsupported MIME type, THEN THE Frontend SHALL display a user-friendly error message styled in coral (`#F0756C`) (e.g., "Only JPEG and PNG images are supported.") without submitting the file to the API.
6. WHEN a valid Image_File is selected, THE Frontend SHALL display a preview of the selected image inside or adjacent to the Drop_Zone.
7. THE Prediction page SHALL display a "Predict" button that is enabled only when a valid Image_File has been selected.

---

### Requirement 7: Prediction Page — API Call and Result Display

**User Story:** As a User, I want to click "Predict" and see the classification result with a confidence bar, so that I can interpret the model's output at a glance.

#### Acceptance Criteria

1. WHEN a User clicks the "Predict" button, THE Frontend SHALL construct a FormData object with the Image_File appended under the field name `file`.
2. WHEN a User clicks the "Predict" button, THE Frontend SHALL send a `POST` request to `http://localhost:8000/predict` with the FormData as the request body.
3. WHILE the API request is in progress, THE Frontend SHALL display a loading indicator and disable the "Predict" button to prevent duplicate submissions.
4. WHEN the API returns a successful Prediction_Response, THE Frontend SHALL display a Result_Card showing the Class_Label as the cell type name.
5. WHEN the API returns a successful Prediction_Response, THE Result_Card SHALL display the Confidence_Score as a percentage (e.g., 94.73%) with a filled progress bar in cyan (`#1CBDC9`) whose width corresponds to the confidence value, on a mint green (`#A2F9AB`) card background.
6. IF the API returns an HTTP error response, THEN THE Frontend SHALL display a user-friendly error message in coral (`#F0756C`) describing the failure (e.g., "Prediction failed. Please try again.").
7. IF a network error occurs (API unreachable), THEN THE Frontend SHALL display a user-friendly error message in coral (`#F0756C`) (e.g., "Could not reach the server. Is the backend running?").
8. WHEN a new Image_File is selected after a prediction, THE Frontend SHALL clear the previous Result_Card and error messages.

---

### Requirement 8: README Documentation

**User Story:** As a developer, I want a README that explains how to install dependencies and run both servers, so that anyone can set up the project from scratch.

#### Acceptance Criteria

1. THE project SHALL include a `README.md` file at the repository root.
2. THE README SHALL include step-by-step instructions for installing Python dependencies (e.g., `pip install -r requirements.txt`).
3. THE README SHALL include the command to start the FastAPI backend server (`uvicorn ml-server:app --reload`).
4. THE README SHALL include step-by-step instructions for installing Node.js dependencies for the Frontend (e.g., `npm install`).
5. THE README SHALL include the command to start the React development server (e.g., `npm run dev`).
6. THE README SHALL specify the default ports for both servers: backend on port 8000, frontend on port 5173.
7. THE README SHALL list the prerequisite software versions (Python ≥ 3.9, Node.js ≥ 18).

---

### Requirement 9: Technical Summary Document

**User Story:** As a student, I want a one-page technical summary explaining CNN Convolutional Blocks and Softmax output, so that I can prepare for a 5–10 minute presentation.

#### Acceptance Criteria

1. THE project SHALL include a `TECHNICAL_SUMMARY.md` file.
2. THE Technical_Summary SHALL explain what a Convolutional Block is, including the roles of the convolutional layer, activation function (ReLU), and pooling layer.
3. THE Technical_Summary SHALL explain how the Softmax output layer converts raw logits into class probabilities that sum to 1.0.
4. THE Technical_Summary SHALL describe how the model maps an input image (150×150×3) through convolutional blocks to a final 4-class Softmax output.
5. THE Technical_Summary SHALL be concise enough to support a 5–10 minute verbal presentation (approximately one printed page).

---

### Requirement 10: Backend Unit Tests

**User Story:** As a developer, I want a pytest test script for the backend, so that I can verify the API endpoints behave correctly.

#### Acceptance Criteria

1. THE project SHALL include a `tests/test_api.py` file (or extend the existing one) with pytest tests for the API.
2. THE tests SHALL use FastAPI's `TestClient` and mock `classify_image` to avoid loading the real Keras model.
3. THE tests SHALL verify that `GET /health` returns HTTP 200 with `{"status": "ok"}`.
4. THE tests SHALL verify that `POST /predict` with a valid mocked image returns HTTP 200 with `predicted_class` in `["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]` and `confidence` in [0.0, 1.0].
5. THE tests SHALL verify that `POST /predict` with an unsupported MIME type returns HTTP 400 with the exact message `"Unsupported file type. Please upload a JPEG or PNG image."`.
6. THE tests SHALL verify that `POST /predict` with no file returns HTTP 422.

---

### Requirement 11: Frontend Component Tests

**User Story:** As a developer, I want basic component rendering tests for the React frontend, so that I can confirm key UI elements are present.

#### Acceptance Criteria

1. THE Frontend project SHALL include a test configuration using Vitest and React Testing Library.
2. THE Frontend tests SHALL verify that the Home page renders the project name heading.
3. THE Frontend tests SHALL verify that the Prediction page renders the Drop_Zone and the "Predict" button.
4. THE Frontend tests SHALL verify that the navigation bar renders links to all four pages.
5. WHEN the Frontend tests are run with `npm test -- --run`, THE test runner SHALL exit with code 0 if all tests pass.
