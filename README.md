# Langflow Contract API

This is a FastAPI-based contract API service deployed on Railway.

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn main:app --reload
```

## Deployment

This application is configured for deployment on Railway. The following files are used for deployment:

- `railway.toml`: Configuration for Railway deployment
- `Procfile`: Specifies how to run the application
- `requirements.txt`: Python dependencies

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc` 