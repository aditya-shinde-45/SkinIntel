# Implementation Plan: SkinIntel Backend

## Overview

Implement the SkinIntel Flask backend incrementally, starting with project scaffolding and data models, then the image preprocessing pipeline, CNN inference service, recommendation engine, REST API routes, middleware, and finally tests. Each task builds on the previous and ends with wired, runnable code.

## Tasks

- [x] 1. Scaffold project structure, config, and data models
  - Create the directory layout: `app/`, `app/controllers/`, `app/services/`, `app/ml/`, `app/data/`, `tests/unit/`, `tests/property/`
  - Create `app/config.py` — `Config` dataclass reading all env vars (`MODEL_PATH`, `MODEL_VERSION`, `PRODUCTS_CSV_PATH`, `ALLOWED_ORIGIN`, `MAX_IMAGE_SIZE_MB`, `PORT`, `ENV`, `RATE_LIMIT_PER_MINUTE`, `CONFIDENCE_THRESHOLD`) with documented defaults
  - Create `app/models.py` — `Product`, `ProductLinks`, `InferenceResult`, `RecommendationResult` dataclasses
  - Create `app/response.py` — `success_response()` and `error_response()` helpers that produce the Standard_Response envelope with `meta.request_id`, `meta.timestamp`, `success`, `data`, `error`
  - Create `requirements.txt` with pinned versions: `flask`, `flask-cors`, `tensorflow`, `pillow`, `numpy`, `pandas`, `requests`, `hypothesis`, `pytest`, `pytest-flask`
  - Create `.env.example` documenting all environment variables
  - _Requirements: 1.6, 8.2, 8.3, 8.4, 8.5_

- [ ] 2. Implement DatasetLoader and in-memory product index
  - [ ] 2.1 Implement `app/data/dataset_loader.py` — `DatasetLoader` class with `load(csv_path)` classmethod
    - Read CSV with pandas, validate required columns (`product_id`, `name`, `brand`, `price`, `currency`, `rating`, `description`, `concern_tags`, `available_countries`, `links_amazon`, `links_nykaa`, `links_flipkart`)
    - Parse `concern_tags` and `available_countries` from comma-separated strings to lists
    - Skip and log a warning for records missing required fields (include record index in warning)
    - Build inverted index: `dict[(concern, country)] → list[Product]` via Cartesian product of tags × countries
    - Store `_products` list and `_index` dict as class-level attributes
    - Expose `is_loaded()`, `record_count()`, `get_index()` classmethods
    - Exit with code 1 if CSV is missing; log schema warnings for unexpected columns
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7_

  - [ ]* 2.2 Write property test for dataset index completeness
    - **Property 8: Dataset index completeness**
    - **Validates: Requirements 5.7**
    - Generate random lists of Product objects with random concern_tags and available_countries using `hypothesis`
    - Assert every product appears in the index under every `(concern, country)` pair from its tags × countries
    - `# Feature: skinintel-backend, Property 8: dataset index completeness`

  - [ ]* 2.3 Write unit tests for DatasetLoader
    - Test missing CSV exits with SystemExit
    - Test malformed rows are skipped and valid rows are loaded
    - Test schema warning logged for unexpected columns
    - _Requirements: 5.3, 5.4, 5.6_

- [ ] 3. Implement ImagePreprocessorService
  - [ ] 3.1 Implement `app/services/image_preprocessor.py` — `ImagePreprocessorService` class
    - `preprocess_file(file)`: validate MIME type (jpeg/png/webp → 415), validate size vs `MAX_IMAGE_SIZE_MB` (→ 413), call `_decode_and_normalize()`
    - `preprocess_url(url)`: call `_ssrf_guard(url)` (validate scheme is http/https, resolve hostname, reject RFC 1918 ranges → 400), call `_fetch_with_retry(url, max_retries=3)` with exponential backoff and per-attempt timeouts (connect=5s, read=10s) (→ 502 on failure), call `_decode_and_normalize()`
    - `_decode_and_normalize(image_bytes)`: open with PIL, resize to (224, 224), convert to float32 numpy array, divide by 255.0, `np.expand_dims(axis=0)` → shape (1, 224, 224, 3); raise 422 on PIL decode error
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 3.2 Write property test for preprocessing output invariant
    - **Property 1: Preprocessing output invariant**
    - **Validates: Requirements 2.3**
    - Use `hypothesis` to generate random valid image bytes (create synthetic PIL images of random sizes/colors)
    - Assert output shape is always `(1, 224, 224, 3)` and all values are in `[0.0, 1.0]`
    - `# Feature: skinintel-backend, Property 1: preprocessing output invariant`

  - [ ]* 3.3 Write unit tests for ImagePreprocessorService
    - Test 415 for unsupported MIME type
    - Test 413 for oversized file
    - Test 422 for corrupted bytes
    - Test 400 for private IP URL (e.g., `http://192.168.1.1/img.jpg`)
    - Test 400 for non-http/https scheme
    - Test 502 when URL fetch fails after retries (mock `requests.get`)
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6_

- [ ] 4. Implement ModelLoader and InferenceService
  - [ ] 4.1 Implement `app/ml/model_loader.py` — `ModelLoader` singleton
    - `load(model_path)`: call `tf.keras.models.load_model(model_path)`, store in `_model`; log error and `sys.exit(1)` if file missing or load fails
    - `get_model()`: return `_model`; raise `RuntimeError` if not loaded
    - `is_loaded()`: return bool
    - _Requirements: 3.2, 3.5, 3.6_

  - [ ] 4.2 Implement `app/ml/inference_service.py` — `InferenceService` class
    - Define `LABELS` list (8 concern labels) and `EXPLANATIONS` dict (one human-readable sentence per label)
    - `predict(tensor)`: call `ModelLoader.get_model().predict(tensor)`, `np.argmax()` on output, map to label and confidence; set `low_confidence = confidence < CONFIDENCE_THRESHOLD`; set `effective_concern = "general_skincare"` if low_confidence else `concern_label`; return `InferenceResult`
    - Wrap `model.predict()` in try/except; re-raise as a typed `ModelInferenceError` for the controller to catch
    - _Requirements: 3.1, 3.3, 3.4, 3.7_

  - [ ]* 4.3 Write property tests for inference result invariants
    - **Property 2: Inference label validity**
    - **Property 3: Inference result invariants**
    - **Validates: Requirements 3.1, 3.3, 3.4**
    - Mock `ModelLoader.get_model()` to return a model that outputs random softmax vectors
    - Assert `concern_label` is always in `LABELS`
    - Assert `confidence` is always in `[0.0, 1.0]`
    - Assert `low_confidence` is `True` iff `confidence < 0.40`
    - Assert `effective_concern` is `"general_skincare"` iff `low_confidence` is `True`
    - `# Feature: skinintel-backend, Property 2: inference label validity`
    - `# Feature: skinintel-backend, Property 3: inference result invariants`

  - [ ]* 4.4 Write unit tests for InferenceService
    - Test `ModelInferenceError` raised when model raises exception
    - Test explanation is non-empty string for each label
    - _Requirements: 3.7, 9.4_

- [ ] 5. Implement RecommendationService
  - [ ] 5.1 Implement `app/services/recommendation_service.py` — `RecommendationService` class
    - `get_recommendations(concern, country, min_price, max_price, limit=10, offset=0)`:
      1. Look up `DatasetLoader.get_index()[(concern, country)]` → candidate list
      2. Filter by `min_price <= product.price <= max_price`
      3. If empty, fall back to `("general_skincare", country)` with same price filter
      4. If still empty, return `RecommendationResult(products=[], total_count=0, no_results=True)`
      5. Sort by `rating` descending
      6. Record `total_count = len(sorted_list)`
      7. Apply slice `[offset : offset + limit]`
      8. Return `RecommendationResult`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8_

  - [ ]* 5.2 Write property test for recommendation filter correctness
    - **Property 5: Recommendation filter correctness**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - Use `hypothesis` to generate random lists of `Product` objects and random filter params
    - Assert every returned product has `concern` in `concern_tags`, `country` in `available_countries`, and `min_price <= price <= max_price`
    - `# Feature: skinintel-backend, Property 5: recommendation filter correctness`

  - [ ]* 5.3 Write property test for recommendation sort invariant
    - **Property 6: Recommendation sort invariant**
    - **Validates: Requirements 4.4**
    - Use `hypothesis` to generate random product lists
    - Assert returned products are in non-increasing order of `rating`
    - `# Feature: skinintel-backend, Property 6: recommendation sort invariant`

  - [ ]* 5.4 Write property test for pagination correctness
    - **Property 7: Pagination correctness**
    - **Validates: Requirements 4.5**
    - Use `hypothesis` to generate random product lists and random `limit`/`offset` values
    - Assert returned slice equals `all_filtered_sorted[offset:offset+limit]`
    - Assert `total_count` equals `len(all_filtered_sorted)` regardless of pagination
    - `# Feature: skinintel-backend, Property 7: pagination correctness`

  - [ ]* 5.5 Write unit tests for RecommendationService
    - Test fallback to `general_skincare` when no results for original concern
    - Test `no_results: true` when fallback also returns nothing
    - Test 400 when `min_price > max_price` (validate in controller, assert service not called)
    - _Requirements: 4.6, 4.7_

- [ ] 6. Checkpoint — Ensure all service-layer tests pass
  - Run `pytest tests/unit/ tests/property/ -v` and confirm all tests pass. Ask the user if any questions arise before proceeding.

- [ ] 7. Implement Flask app factory, middleware, and error handlers
  - [ ] 7.1 Implement `app/__init__.py` — `create_app(config)` factory
    - Initialize Flask app
    - Configure `flask-cors` with `origins=config.ALLOWED_ORIGIN`
    - Register before/after request hooks for structured JSON logging (emit `request_id`, `method`, `path`, `status_code`, `total_time_ms`, `timestamp` as JSON to stdout)
    - Register global error handlers for 400, 413, 415, 422, 429, 500, 504 that return Standard_Response envelopes
    - Register handler for unhandled exceptions → 500 `internal_server_error` (no stack trace in body)
    - _Requirements: 8.1, 9.1, 9.2, 9.3, 9.5_

  - [ ] 7.2 Implement `app/middleware/rate_limiter.py` — in-memory sliding window rate limiter
    - Use `collections.defaultdict` keyed by client IP (`request.remote_addr`)
    - Track request timestamps in a deque per IP; evict entries older than 60 seconds
    - If count >= `RATE_LIMIT_PER_MINUTE`, return 429 Standard_Response before route handler runs
    - Register as a `before_request` hook in `create_app`
    - _Requirements: 8.6_

  - [ ]* 7.3 Write unit tests for middleware
    - Test CORS headers present on all routes (OPTIONS preflight)
    - Test rate limiter returns 429 after exceeding limit
    - Test rate limiter resets after 60 seconds (mock time)
    - _Requirements: 8.1, 8.6_

- [ ] 8. Implement API controllers and wire routes
  - [ ] 8.1 Implement `app/controllers/analyze_controller.py` — `POST /api/v1/analyze`
    - Validate `country` (must be in supported set) → 400 if invalid
    - Validate `min_price`, `max_price` (must be numeric, min <= max) → 400 if invalid
    - Determine image source: `request.files.get("image")` or `request.form.get("image_url")`; return 400 if neither present
    - Call `ImagePreprocessorService.preprocess_file()` or `preprocess_url()`
    - Record `t0`; call `InferenceService.predict(tensor)`; record `inference_time_ms`
    - Call `RecommendationService.get_recommendations(effective_concern, country, min_price, max_price, limit, offset)`
    - Build and return Standard_Response with `data`, `meta` (including `inference_time_ms`, `total_time_ms`, `model_version`, `request_id`)
    - Catch `ModelInferenceError` → 500 `model_inference_failed`
    - Enforce 10-second total timeout via `signal` or threading; return 504 on breach
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 3.8_

  - [ ] 8.2 Implement `app/controllers/products_controller.py` — `GET /api/v1/products`
    - Validate `concern`, `country`, `min_price`, `max_price` query params → 400 if invalid
    - Call `RecommendationService.get_recommendations()` with same logic as analyze controller
    - Return Standard_Response with `data.products`, `meta` (pagination fields, `request_id`)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 8.3 Implement `app/controllers/health_controller.py` — `GET /api/v1/health`
    - Return Standard_Response with `data` containing `status`, `model_loaded`, `dataset_loaded`, `model_version`, `dataset_record_count`
    - _Requirements: 7.1, 7.2_

  - [ ] 8.4 Register all blueprints in `create_app` and implement `run.py` startup script
    - `run.py`: load `Config` from env, call `ModelLoader.load()` then `DatasetLoader.load()`, call `create_app(config)`, run with `app.run(port=config.PORT, debug=(config.ENV == "dev"))`
    - _Requirements: 3.2, 5.1_

  - [ ]* 8.5 Write property tests for response envelope invariant and no stack traces
    - **Property 9: Response envelope invariant**
    - **Property 10: No stack traces in error responses**
    - **Validates: Requirements 1.6, 9.1, 9.5**
    - Use `hypothesis` to generate many different request types (valid, invalid, error-triggering)
    - Assert every response contains `meta.request_id` as a non-empty string
    - Assert `success` is `True` iff HTTP status is 2xx
    - Assert error response bodies do not contain `"Traceback"`, `"File \""`, `"line "`, `"raise "`
    - `# Feature: skinintel-backend, Property 9: response envelope invariant`
    - `# Feature: skinintel-backend, Property 10: no stack traces in error responses`

  - [ ]* 8.6 Write property test for products/analyze endpoint consistency
    - **Property 11: Products/analyze endpoint consistency**
    - **Validates: Requirements 6.4**
    - Use `hypothesis` to generate random concern/country/price/pagination params
    - Mock `InferenceService.predict()` to return a fixed concern label
    - Assert `GET /api/v1/products` returns same `products` and `total_count` as `POST /api/v1/analyze` for the same params
    - `# Feature: skinintel-backend, Property 11: products/analyze endpoint consistency`

  - [ ]* 8.7 Write unit tests for all controllers
    - Test each 4xx error path for analyze and products endpoints
    - Test health endpoint returns correct fields
    - Test 504 when inference exceeds timeout (mock slow inference)
    - Test `model_inference_failed` 500 when model raises exception
    - _Requirements: 1.3, 1.4, 1.5, 6.2, 6.3, 7.1, 9.4_

- [ ] 9. Checkpoint — Ensure all tests pass end-to-end
  - Run `pytest tests/ -v --tb=short` and confirm all unit and property tests pass. Ask the user if any questions arise before proceeding.

- [ ] 10. Add CNN model training script
  - [ ] 10.1 Implement `ml/train.py` — MobileNetV2 fine-tuning script
    - Load dataset from `DATA_DIR` env var (expects subdirectories per class matching `LABELS`)
    - Apply data augmentation: `ImageDataGenerator` with horizontal flip, rotation_range=15, zoom_range=0.1, brightness_range=[0.8, 1.2]
    - Build model: `MobileNetV2(include_top=False, input_shape=(224,224,3))` → `GlobalAveragePooling2D` → `Dense(256, relu)` → `Dropout(0.3)` → `Dense(8, softmax)`
    - Phase 1: freeze backbone, compile with `lr=1e-3`, train 10 epochs
    - Phase 2: unfreeze top 30 layers, recompile with `lr=1e-5`, train 10 epochs
    - Save model to `MODEL_OUTPUT_PATH` env var as `model.keras`
    - _Requirements: 3.1, 3.2_

  - [ ] 10.2 Implement `ml/evaluate.py` — evaluation script
    - Load saved model, run on validation split, print per-class accuracy and confusion matrix
    - _Requirements: 3.1_

- [ ] 11. Add Docker and environment configuration
  - [ ] 11.1 Create `Dockerfile` — multi-stage build
    - Stage 1 (`builder`): install Python deps into `/install`
    - Stage 2 (`runtime`): copy `/install`, copy `app/`, `run.py`; set `CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]`
    - _Requirements: 8.2, 8.4_

  - [ ] 11.2 Create `docker-compose.yml` for local development
    - Mount `./models/` and `./data/` as volumes
    - Pass all env vars from `.env` file
    - _Requirements: 8.2_

- [ ] 12. Final checkpoint — Full test suite and smoke test
  - Run `pytest tests/ -v --cov=app --cov-report=term-missing` and confirm ≥80% coverage and all tests pass. Ask the user if any questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use `hypothesis` with `@settings(max_examples=100)`
- The CNN training script (`ml/train.py`) requires the Kaggle dataset downloaded locally; model weights are not committed to the repo
- Checkpoints at tasks 6, 9, and 12 ensure incremental validation before proceeding
