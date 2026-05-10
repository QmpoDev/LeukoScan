# Implementation Plan: Blood Cell Classifier Web App

## Overview

Implement the full-stack **EventDP — Blood Cell Image Classification** web application by:
1. Adding CORS middleware to the existing FastAPI backend.
2. Scaffolding and building a four-page React SPA (Home, About, Features, Prediction).
3. Writing backend pytest tests and frontend Vitest tests.
4. Producing README and TECHNICAL_SUMMARY documentation files.

Each task builds incrementally on the previous one. No code is left unintegrated.

---

## Tasks

- [x] 1. Add CORS middleware to the FastAPI backend
  - Open `ml-server.py` and add `from fastapi.middleware.cors import CORSMiddleware` at the top of the imports.
  - Insert `app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST","OPTIONS"], allow_headers=["*"])` immediately after the `app = FastAPI(...)` instantiation and before the first endpoint definition.
  - Verify the server still starts without errors by reviewing the file for syntax issues.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Scaffold the React frontend project
  - [x] 2.1 Create `frontend/package.json` with all required dependencies
    - Include runtime deps: `react@18`, `react-dom@18`, `react-router-dom@6`, `lucide-react`, `tailwindcss@3`, `autoprefixer`, `postcss`.
    - Include dev deps: `@vitejs/plugin-react`, `vite`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`.
    - Add scripts: `"dev": "vite"`, `"build": "vite build"`, `"test": "vitest"`.
    - _Requirements: 2.5, 11.1_

  - [x] 2.2 Create Vite and Tailwind configuration files
    - Create `frontend/vite.config.js` with `@vitejs/plugin-react` plugin and vitest config (`environment: "jsdom"`, `setupFiles: ["./src/setupTests.js"]`, `globals: true`).
    - Create `frontend/tailwind.config.js` with `content` pointing to `./index.html` and `./src/**/*.{js,jsx}`, and `theme.extend.colors` for the 5 custom colors: `primary: "#172F7C"`, `secondary: "#2DC6B2"`, `accent: "#1CBDC9"`, `success: "#A2F9AB"`, `error: "#F0756C"`.
    - Create `frontend/postcss.config.js` with `tailwindcss` and `autoprefixer` plugins.
    - _Requirements: 2.5, 3.5_

  - [x] 2.3 Create HTML entry point and CSS/JS entry files
    - Create `frontend/index.html` with a `<div id="root">` and a `<script type="module" src="/src/main.jsx">` tag.
    - Create `frontend/src/index.css` with the three Tailwind directives: `@tailwind base`, `@tailwind components`, `@tailwind utilities`.
    - Create `frontend/src/setupTests.js` that imports `@testing-library/jest-dom`.
    - _Requirements: 2.5, 11.1_

- [x] 3. Build shared UI components
  - [x] 3.1 Implement `frontend/src/components/Navbar.jsx`
    - Render a `<nav>` with `bg-[#172F7C] text-white px-6 py-3 flex items-center justify-between` classes.
    - Include four `<NavLink>` elements (Home `/`, About `/about`, Features `/features`, Predict `/predict`) using `react-router-dom`.
    - Apply active link styling `text-[#1CBDC9] font-semibold` via the `className` callback on `NavLink`.
    - _Requirements: 2.4, 2.6_

  - [x] 3.2 Implement `frontend/src/components/DropZone.jsx`
    - Accept props: `onFileAccepted`, `onFileRejected`, `previewUrl`.
    - Manage local `isDragging` state; handle `onDragOver`, `onDragLeave`, `onDrop`, and a hidden `<input type="file">` `onChange`.
    - On drop/select: check `file.type` against `["image/jpeg", "image/png"]`; call `onFileAccepted(file)` for valid files, `onFileRejected("Only JPEG and PNG images are supported.")` for invalid.
    - When `previewUrl` is set, render an `<img>` preview inside the zone.
    - Apply drag-active class `bg-[#2DC6B2]/20 border-[#1CBDC9]` when `isDragging` is true.
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 3.3 Implement `frontend/src/components/PredictButton.jsx`
    - Accept props: `onClick`, `disabled`.
    - Render a `<button>` with classes `bg-[#172F7C] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#1CBDC9] disabled:opacity-50 disabled:cursor-not-allowed transition-colors`.
    - Pass `disabled` prop directly to the button element.
    - _Requirements: 6.7, 7.3_

  - [x] 3.4 Implement `frontend/src/components/ResultCard.jsx`
    - Accept props: `predictedClass`, `confidence` (float in [0.0, 1.0]).
    - Display `predictedClass` as a heading.
    - Display `(confidence * 100).toFixed(2) + "%"` as the percentage label.
    - Render a progress bar: outer track `bg-gray-200 rounded-full h-4 w-full`, inner fill `bg-[#1CBDC9] h-4 rounded-full transition-all` with inline style `width: ${confidence * 100}%`.
    - Apply card background `bg-[#A2F9AB] rounded-xl p-6 shadow-md`.
    - _Requirements: 7.4, 7.5_

  - [x] 3.5 Implement `frontend/src/components/ErrorMessage.jsx`
    - Accept prop: `message`.
    - Render a `<div>` with classes `text-[#F0756C] bg-[#F0756C]/10 border border-[#F0756C] rounded-lg px-4 py-3 text-sm`.
    - _Requirements: 6.5, 7.6, 7.7_

  - [x] 3.6 Implement `frontend/src/components/LoadingSpinner.jsx`
    - Render a `<div>` with classes `animate-spin h-8 w-8 border-4 border-[#1CBDC9] border-t-transparent rounded-full mx-auto`.
    - Accept no props.
    - _Requirements: 7.3_

- [x] 4. Build the `usePrediction` custom hook
  - Create `frontend/src/hooks/usePrediction.js`.
  - Manage state: `file` (null), `previewUrl` (null), `isLoading` (false), `result` (null), `error` (null) using `useState`.
  - Implement `handleFileAccepted(file)`: set `file`, create `URL.createObjectURL(file)` for `previewUrl`, clear `result` and `error`.
  - Implement `handleFileRejected(reason)`: set `error = reason`, clear `file`, `previewUrl`, `result`.
  - Implement `handlePredict()`: set `isLoading = true`, build `FormData` with `fd.append("file", file)`, call `fetch("http://localhost:8000/predict", { method: "POST", body: fd })`.
    - On 200: parse JSON, set `result = { predictedClass: json.predicted_class, confidence: json.confidence }`, clear `error`.
    - On HTTP error (non-ok response): set `error = "Prediction failed. Please try again."`, clear `result`.
    - On network error (fetch throws): set `error = "Could not reach the server. Is the backend running?"`, clear `result`.
    - Always set `isLoading = false` in a `finally` block.
  - Return `{ file, previewUrl, isLoading, result, error, handleFileAccepted, handleFileRejected, handlePredict }`.
  - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7, 7.8_

- [x] 5. Build the four pages
  - [x] 5.1 Implement `frontend/src/pages/HomePage.jsx`
    - Render the primary heading `"EventDP — Blood Cell Image Classification"`.
    - Include a brief description paragraph about classifying blood cell images into four categories using a CNN.
    - Include a call-to-action `<Link to="/predict">` button styled with `bg-[#172F7C]` classes.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 5.2 Implement `frontend/src/pages/AboutPage.jsx`
    - Describe the academic context (course name, laboratory assignment).
    - Include team/author information.
    - Describe the dataset: blood cell microscopy images in four classes (Eosinophil, Lymphocyte, Monocyte, Neutrophil).
    - Apply project color palette via Tailwind classes.
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 5.3 Implement `frontend/src/pages/FeaturesPage.jsx`
    - List all four supported blood cell classes with a brief description of each.
    - Describe model input requirements: JPEG or PNG, resized to 150×150 pixels internally.
    - Use Lucide-React icons (e.g., `Microscope`, `Activity`, `Droplets`, `FlaskConical`) to visually distinguish each cell type.
    - Apply project color palette via Tailwind classes.
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 5.4 Implement `frontend/src/pages/PredictionPage.jsx`
    - Import and call `usePrediction()` to get all state and handlers.
    - Render `<DropZone onFileAccepted={handleFileAccepted} onFileRejected={handleFileRejected} previewUrl={previewUrl} />`.
    - Render `<PredictButton onClick={handlePredict} disabled={file === null || isLoading} />`.
    - Conditionally render `<LoadingSpinner />` when `isLoading === true`.
    - Conditionally render `<ResultCard predictedClass={result.predictedClass} confidence={result.confidence} />` when `result !== null`.
    - Conditionally render `<ErrorMessage message={error} />` when `error !== null`.
    - _Requirements: 6.1, 6.2, 6.7, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [x] 6. Wire up App entry point and routing
  - [x] 6.1 Implement `frontend/src/App.jsx`
    - Import `Navbar` and all four page components.
    - Import `Routes` and `Route` from `react-router-dom`.
    - Render `<Navbar />` above `<Routes>` so it appears on every page.
    - Define four `<Route>` entries: `path="/"` → `<HomePage />`, `path="/about"` → `<AboutPage />`, `path="/features"` → `<FeaturesPage />`, `path="/predict"` → `<PredictionPage />`.
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 6.2 Implement `frontend/src/main.jsx`
    - Import `React`, `ReactDOM`, `BrowserRouter` from `react-router-dom`, `App`, and `./index.css`.
    - Call `ReactDOM.createRoot(document.getElementById("root")).render(<BrowserRouter><App /></BrowserRouter>)`.
    - _Requirements: 2.2, 2.3_

- [ ] 7. Checkpoint — verify frontend renders without errors
  - Ensure all imports resolve (no missing files or typos in component names).
  - Ensure all four pages are reachable via their routes.
  - Ask the user if any questions arise before proceeding to tests.

- [x] 8. Write frontend Vitest tests
  - [x] 8.1 Create `frontend/src/__tests__/HomePage.test.jsx`
    - Import `render` and `screen` from `@testing-library/react`, wrap with `MemoryRouter`.
    - Assert that the heading `"EventDP — Blood Cell Image Classification"` is present in the document.
    - _Requirements: 11.2_

  - [ ]* 8.2 Write property test for confidence bar width (Property 1)
    - **Property 1: Confidence bar width matches confidence value**
    - Extract the bar-width calculation `(confidence * 100).toFixed(2) + "%"` into a pure helper function.
    - Use `fast-check` to generate arbitrary floats in [0.0, 1.0] and assert the helper returns a string ending in `"%"` whose numeric prefix equals `confidence * 100` rounded to 2 decimal places.
    - **Validates: Requirements 7.4, 7.5**

  - [x] 8.3 Create `frontend/src/__tests__/PredictionPage.test.jsx`
    - Import `render` and `screen`, wrap with `MemoryRouter`.
    - Assert that the drop zone area is present (e.g., by role or test-id).
    - Assert that the "Predict" button is present and initially disabled.
    - _Requirements: 11.3_

  - [ ]* 8.4 Write property test for MIME validation (Property 2)
    - **Property 2: Invalid MIME type always blocks the API call**
    - Extract the MIME validation logic from `DropZone` into a pure helper `isValidMime(type)`.
    - Use `fast-check` to generate arbitrary strings and assert that `isValidMime` returns `true` only for `"image/jpeg"` and `"image/png"`.
    - **Validates: Requirements 6.4, 6.5**

  - [x] 8.5 Create `frontend/src/__tests__/Navbar.test.jsx`
    - Import `render` and `screen`, wrap with `MemoryRouter`.
    - Assert that all four navigation links (Home, About, Features, Predict) are present in the document.
    - _Requirements: 11.4_

- [x] 9. Write backend pytest tests
  - [x] 9.1 Create or extend `tests/test_api.py` with example-based tests
    - Import `TestClient` from `fastapi.testclient` and `patch` from `unittest.mock`.
    - Patch `classify.classify_image` to return `("Neutrophil", 0.9473)` without loading the Keras model.
    - Write `test_health_ok`: assert `GET /health` returns 200 and `{"status": "ok"}`.
    - Write `test_predict_valid_jpeg`: POST a minimal JPEG bytes payload; assert 200, `predicted_class` in `CLASS_LABELS`, `confidence` in [0.0, 1.0].
    - Write `test_predict_valid_png`: same as above with PNG content-type.
    - Write `test_predict_invalid_mime`: POST with `content_type="text/plain"`; assert 400 and exact message `"Unsupported file type. Please upload a JPEG or PNG image."`.
    - Write `test_predict_no_file`: POST with no file field; assert 422.
    - Write `test_predict_confidence_range`: assert the mocked confidence value returned in the response is between 0.0 and 1.0 inclusive.
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 9.2 Write property test for confidence rounding idempotence (Property 6)
    - **Property 6: Backend confidence rounding is stable**
    - Use `hypothesis` with `@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))`.
    - Assert `round(round(x, 4), 4) == round(x, 4)` for all valid confidence floats.
    - **Validates: Requirements 10.4**

  - [ ]* 9.3 Write property test for MIME rejection (Property 2 — backend)
    - **Property 2: Invalid MIME type always blocks the API call (backend)**
    - Use `hypothesis` with `@given(st.text())` filtered to exclude `"image/jpeg"` and `"image/png"`.
    - For each generated MIME string, POST to `/predict` with that content-type and assert the response status is 400.
    - **Validates: Requirements 10.5**

- [ ] 10. Checkpoint — ensure all tests pass
  - Run backend tests: `pytest tests/test_api.py -v`.
  - Run frontend tests: `npm test -- --run` from the `frontend/` directory.
  - Fix any failures before proceeding.
  - Ask the user if any questions arise.

- [x] 11. Write documentation files
  - [x] 11.1 Create `README.md` at the repository root
    - List prerequisites: Python ≥ 3.9, Node.js ≥ 18.
    - Provide backend setup: `pip install -r requirements.txt`, then `uvicorn ml-server:app --reload` (runs on port 8000).
    - Provide frontend setup: `cd frontend && npm install`, then `npm run dev` (runs on port 5173).
    - Specify default ports: backend 8000, frontend 5173.
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 11.2 Create `TECHNICAL_SUMMARY.md` at the repository root
    - Explain what a Convolutional Block is: convolutional layer (feature map extraction via learned filters), ReLU activation (non-linearity, discards negatives), and pooling layer (spatial downsampling).
    - Explain how the Softmax output layer converts raw logits into class probabilities that sum to 1.0.
    - Describe the full input→output flow: 150×150×3 image → stacked convolutional blocks → flatten → dense layers → 4-class Softmax output.
    - Keep the document concise (≈ one printed page) to support a 5–10 minute verbal presentation.
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 12. Final checkpoint — ensure all tests pass and deliverables are complete
  - Confirm all files listed in the design's "File Deliverables" section exist.
  - Run `pytest tests/test_api.py -v` and `npm test -- --run` one final time.
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP.
- Each task references specific requirements for traceability.
- Checkpoints (tasks 7, 10, 12) ensure incremental validation at natural breaks.
- Property tests (8.2, 8.4, 9.2, 9.3) validate universal correctness properties from the design document.
- Unit/integration tests validate specific examples and edge cases.
- The backend server must be running on port 8000 before manual end-to-end testing; use `uvicorn ml-server:app --reload`.
- The frontend dev server runs on port 5173; use `npm run dev` from the `frontend/` directory.
