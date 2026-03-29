# SkinIntel — AI-Powered Skin Analysis

```
SkinIntel/
  backend/          Python Flask API + CNN model + DynamoDB auth
    app/            Flask application (controllers, services, ml, data)
    ml/             Training scripts (train.py, evaluate.py)
    models/         Trained model weights (model.keras)
    data/           Product dataset CSV
    tests/          Unit and property tests
    run.py          Server entry point
    requirements.txt
    Dockerfile
    .env

  frontend/         React + TypeScript + Vite
    src/            Application source
    index.html
    package.json
    vite.config.ts
    Dockerfile
    .env

  docker-compose.yml   Runs both services together
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker (both together)
```bash
docker-compose up --build
```
