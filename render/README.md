# Render Deployment

This folder contains the backend deployment files for Render.

## What it deploys

- Flask API from `backend/`
- Health check at `/api/v1/health`
- Keras model from `backend/models/model.keras`
- Products dataset from `backend/data/skincare_products_clean.csv`

## Deploy steps

1. Create a new Render service from `render/render.yaml`.
2. Use the `skinintel-backend` web service definition.
3. Set the secret environment variables in Render:
   - `JWT_SECRET`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `DYNAMODB_ENDPOINT` if you are not using AWS DynamoDB directly
4. Update `ALLOWED_ORIGIN` to your frontend URL before going live.
5. Verify the service on `GET /api/v1/health`.

## Notes

- The service runs with `gunicorn` and listens on Render's `$PORT` value.
- `MODEL_PATH` and `PRODUCTS_CSV_PATH` are relative to the `backend/` root.
- `CONCERN_MODEL_PATH` is set to the same packaged model file to keep startup consistent.
- Keep secrets out of git; only placeholders belong in committed files.