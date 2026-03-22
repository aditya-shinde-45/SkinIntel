# Requirements Document

## Introduction

SkinIntel is an AI-powered skincare web application. The backend is a Python Flask REST API that accepts a user-uploaded skin image along with country and price range preferences, runs a CNN-based skin concern classifier, and returns structured product recommendations sourced from a Kaggle skincare products dataset. The backend must serve the existing React + TypeScript frontend via CORS-enabled JSON endpoints. The system follows a layered architecture: Controller → Service → ML → Data, and is designed to be deployable on a single server or serverless setup without external caching infrastructure.

## Glossary

- **API**: The Flask REST API backend service, versioned under `/api/v1/`
- **Analyzer**: The CNN inference component that classifies skin concerns from images
- **Classifier**: The trained CNN model (MobileNetV2/EfficientNet backbone) that outputs a skin concern label and confidence score
- **Concern_Label**: A string identifying a detected skin condition (e.g., `acne`, `dark_circles`, `blackheads`, `oily_skin`, `dry_skin`, `normal_skin`, `hyperpigmentation`, `wrinkles`)
- **Product**: A skincare product record containing name, brand, price, rating, description, and availability links
- **Recommendation_Engine**: The component that filters and ranks products by concern label, country, and price range using an in-memory index
- **Image_Preprocessor**: The component that validates, decodes, and normalizes uploaded images for model inference
- **Dataset_Loader**: The component that loads, validates, and indexes the Kaggle skincare products CSV at startup into an in-memory dictionary structure
- **Price_Range**: A tuple of (min_price, max_price) in the currency of the selected country
- **Country_Code**: An ISO 3166-1 alpha-2 code from the supported set: IN, US, UK, CA, AU, DE, FR, JP
- **Request_ID**: A UUID generated per request for distributed tracing
- **Standard_Response**: The unified JSON envelope `{ "success": bool, "data": {}, "error": {}, "meta": {} }`
- **Confidence_Score**: A float in [0.0, 1.0] representing the model's certainty for the top predicted class
- **Fallback_Concern**: The label `general_skincare` used when model confidence is below threshold or inference fails

---

## Requirements

### Requirement 1: Image Upload and Analysis Endpoint

**User Story:** As a frontend developer, I want a single POST endpoint that accepts an image and user preferences, so that the frontend can trigger the full analysis pipeline in one request.

#### Acceptance Criteria

1. WHEN a client sends a POST request to `/api/v1/analyze` with a multipart/form-data body containing an image file, a `country` field, a `min_price` field, and a `max_price` field, THE API SHALL return a Standard_Response with `data` containing `concern_label`, `confidence`, `explanation`, `low_confidence` flag, and a `products` array.
2. WHEN a client sends a POST request to `/api/v1/analyze` with an `image_url` string field instead of a file upload, THE API SHALL fetch the image from the URL and process it identically to a file upload.
3. WHEN the `country` field is absent or not a supported Country_Code, THE API SHALL return a 400 Standard_Response with a descriptive error message.
4. WHEN the `min_price` or `max_price` field is absent or non-numeric, THE API SHALL return a 400 Standard_Response with a descriptive error message.
5. THE API SHALL respond to all valid `/api/v1/analyze` requests within 10 seconds; IF the request exceeds 10 seconds, THE API SHALL return a 504 Standard_Response with `error: "request_timeout"`.
6. THE API SHALL include a unique `request_id` in the `meta` field of every Standard_Response.
7. THE API SHALL include `inference_time_ms` and `total_time_ms` in the `meta` field of every `/api/v1/analyze` response.

---

### Requirement 2: Image Validation and Preprocessing

**User Story:** As a system operator, I want the backend to validate and preprocess uploaded images, so that the CNN model receives correctly formatted input and invalid uploads are rejected early.

#### Acceptance Criteria

1. WHEN an uploaded file has a MIME type other than `image/jpeg`, `image/png`, or `image/webp`, THE Image_Preprocessor SHALL return a 415 Standard_Response with a descriptive error message.
2. WHEN an uploaded image file exceeds the configured `MAX_IMAGE_SIZE_MB` limit, THE Image_Preprocessor SHALL return a 413 Standard_Response with a descriptive error message.
3. WHEN a valid image is received, THE Image_Preprocessor SHALL resize it to 224×224 pixels, normalize pixel values to the range [0.0, 1.0], and expand dimensions to produce a tensor of shape (1, 224, 224, 3).
4. IF the image cannot be decoded (e.g., corrupted file), THEN THE Image_Preprocessor SHALL return a 422 Standard_Response with a descriptive error message.
5. WHEN an `image_url` is provided, THE Image_Preprocessor SHALL validate that the URL scheme is `http` or `https` and that the hostname does not resolve to a private IP range (RFC 1918); IF either check fails, THEN THE Image_Preprocessor SHALL return a 400 Standard_Response.
6. IF the HTTP request to fetch an `image_url` returns a non-200 status code after up to 3 retry attempts with exponential backoff, THEN THE Image_Preprocessor SHALL return a 502 Standard_Response with a descriptive error message.
7. WHEN fetching an `image_url`, THE Image_Preprocessor SHALL enforce a connection timeout of 5 seconds and a read timeout of 10 seconds per attempt.

---

### Requirement 3: CNN Skin Concern Classification

**User Story:** As a user, I want the system to accurately identify my skin concern from my uploaded photo, so that I receive relevant product recommendations.

#### Acceptance Criteria

1. THE Classifier SHALL support the following concern labels: `acne`, `dark_circles`, `blackheads`, `oily_skin`, `dry_skin`, `normal_skin`, `hyperpigmentation`, `wrinkles`.
2. WHEN the API server starts, THE Classifier SHALL load the trained model weights from the path specified by `MODEL_PATH` into memory exactly once before accepting requests.
3. WHEN a preprocessed image tensor is passed to the Classifier, THE Classifier SHALL return the concern label with the highest softmax probability along with a Confidence_Score between 0.0 and 1.0.
4. IF the Classifier's highest Confidence_Score is below 0.40, THEN THE API SHALL set `low_confidence: true` in the response and use `general_skincare` as the Fallback_Concern for product filtering.
5. IF the model file is missing or fails to load at startup, THEN THE API SHALL log the error and exit with a non-zero status code.
6. WHILE the model is loaded and the server is running, THE Classifier SHALL process each inference request without reloading model weights from disk.
7. THE Classifier SHALL include a human-readable `explanation` string in the response that describes the detected concern and its common characteristics (e.g., "Acne is characterized by clogged pores and inflammation...").
8. THE API SHALL expose the active model version via the `MODEL_VERSION` environment variable and include it in the `meta` field of every `/api/v1/analyze` response.

---

### Requirement 4: Product Recommendation Filtering

**User Story:** As a user, I want to receive product recommendations that match my detected skin concern, my country, and my budget, so that I can find products I can actually buy.

#### Acceptance Criteria

1. WHEN a concern label, country code, and price range are provided, THE Recommendation_Engine SHALL return only products whose `concern_tags` field contains the given concern label.
2. WHEN filtering by country, THE Recommendation_Engine SHALL return only products whose `available_countries` field contains the given country code.
3. WHEN filtering by price range, THE Recommendation_Engine SHALL return only products whose `price` field is greater than or equal to `min_price` and less than or equal to `max_price`.
4. THE Recommendation_Engine SHALL sort the filtered products by `rating` in descending order.
5. THE Recommendation_Engine SHALL support pagination via `limit` (default 10, max 50) and `offset` (default 0) parameters, and include `total_count`, `limit`, and `offset` in the `meta` field.
6. IF no products match the combined filters, THEN THE Recommendation_Engine SHALL fall back to filtering by `general_skincare` concern with the same country and price range; IF still no results, THEN THE Recommendation_Engine SHALL return an empty `products` array with `no_results: true` in the response.
7. WHEN `min_price` is greater than `max_price`, THE API SHALL return a 400 Standard_Response with a descriptive error message.
8. THE Recommendation_Engine SHALL use an in-memory index keyed by `(concern_label, country_code)` to avoid full dataset scans on every request.

---

### Requirement 5: Product Data and Dataset Integration

**User Story:** As a developer, I want the backend to load and index a Kaggle skincare products dataset at startup, so that product lookups are fast and do not require repeated disk reads.

#### Acceptance Criteria

1. WHEN the API server starts, THE Dataset_Loader SHALL read the skincare products CSV file from the path specified by `PRODUCTS_CSV_PATH` and load all records into an in-memory data structure before accepting requests.
2. THE Dataset_Loader SHALL parse each product record to extract: `product_id`, `name`, `brand`, `price`, `currency`, `rating`, `description`, `concern_tags` (list), `available_countries` (list), and `links` (dict with keys `amazon`, `nykaa`, `flipkart`).
3. IF the products CSV file is missing at startup, THEN THE Dataset_Loader SHALL log an error and the API SHALL exit with a non-zero status code.
4. IF a product record is missing required fields, THEN THE Dataset_Loader SHALL skip that record and log a warning with the record index.
5. THE Dataset_Loader SHALL complete loading and indexing within 5 seconds for datasets up to 50,000 records.
6. THE Dataset_Loader SHALL validate the CSV schema at startup and log a warning if unexpected columns are present.
7. THE Dataset_Loader SHALL build an inverted index mapping `(concern_label, country_code)` → list of product records at load time to support O(1) lookup by concern and country.

---

### Requirement 6: Product Listing Endpoint

**User Story:** As a frontend developer, I want a GET endpoint to retrieve products filtered by concern, country, and price range independently of image analysis, so that the frontend can display products without re-uploading an image.

#### Acceptance Criteria

1. WHEN a client sends a GET request to `/api/v1/products` with query parameters `concern`, `country`, `min_price`, and `max_price`, THE API SHALL return a Standard_Response with a `data.products` array of matching products.
2. WHEN the `concern` query parameter is not one of the supported concern labels, THE API SHALL return a 400 Standard_Response with a descriptive error message.
3. WHEN the `country` query parameter is not one of the supported country codes, THE API SHALL return a 400 Standard_Response with a descriptive error message.
4. THE API SHALL apply the same filtering, sorting, and pagination logic as the Recommendation_Engine used in the `/api/v1/analyze` endpoint.
5. THE `/api/v1/products` endpoint SHALL support the same `limit` and `offset` pagination parameters as the analyze endpoint.

---

### Requirement 7: Health Check Endpoint

**User Story:** As a system operator, I want a health check endpoint, so that I can verify the API is running and its dependencies are loaded.

#### Acceptance Criteria

1. WHEN a client sends a GET request to `/api/v1/health`, THE API SHALL return a 200 Standard_Response with `data` containing `status: "ok"`, `model_loaded: true/false`, `dataset_loaded: true/false`, `model_version`, and `dataset_record_count`.
2. WHILE the model is not yet loaded, THE API SHALL return `model_loaded: false` in the health check response.
3. THE API SHALL return the health check response within 200 milliseconds.

---

### Requirement 8: CORS, Rate Limiting, and Environment Configuration

**User Story:** As a frontend developer and system operator, I want the backend to allow cross-origin requests, enforce rate limits, and be fully configurable via environment variables, so that the API is secure and operable across environments.

#### Acceptance Criteria

1. THE API SHALL enable CORS for all routes, with the allowed origin configurable via the `ALLOWED_ORIGIN` environment variable.
2. THE API SHALL read the following configuration from environment variables: `MODEL_PATH`, `MODEL_VERSION`, `PRODUCTS_CSV_PATH`, `ALLOWED_ORIGIN`, `MAX_IMAGE_SIZE_MB`, `PORT`, `ENV` (dev/staging/prod), `RATE_LIMIT_PER_MINUTE`.
3. WHERE `ALLOWED_ORIGIN` is not set, THE API SHALL default to allowing all origins (`*`).
4. WHERE `PORT` is not set, THE API SHALL default to port `5000`.
5. WHERE `MAX_IMAGE_SIZE_MB` is not set, THE API SHALL default to `10`.
6. THE API SHALL enforce a per-IP rate limit on `/api/v1/analyze` using an in-memory counter, configurable via `RATE_LIMIT_PER_MINUTE` (default: 30 requests per minute); IF the limit is exceeded, THE API SHALL return a 429 Standard_Response.
7. WHERE `ENV` is set to `prod`, THE API SHALL disable debug mode and suppress verbose error details in responses.

---

### Requirement 9: Error Handling and Structured Logging

**User Story:** As a system operator, I want all errors to be logged with context and returned as structured JSON, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. IF an unhandled exception occurs during request processing, THEN THE API SHALL return a 500 Standard_Response with `error.code: "internal_server_error"` and a `error.message` field.
2. THE API SHALL emit structured JSON log entries for every request containing: `request_id`, `method`, `path`, `status_code`, `total_time_ms`, and `timestamp`.
3. THE API SHALL emit structured JSON log entries for every error containing: `request_id`, `error_type`, `message`, `stack_trace`, and `timestamp`.
4. IF the model inference raises an exception, THEN THE API SHALL return a 500 Standard_Response with `error.code: "model_inference_failed"` and a descriptive `error.message`.
5. THE API SHALL never include raw stack traces or internal file paths in HTTP response bodies.
6. THE API SHALL log inference time in milliseconds for every `/api/v1/analyze` request.
