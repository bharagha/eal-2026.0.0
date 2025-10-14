import yaml
from fastapi import FastAPI
from routes import pipelines, devices, models, metrics

# Load OpenAPI schema
with open("api/vippet.yaml") as f:
    openapi_schema = yaml.safe_load(f)

# Initialize FastAPI app
app = FastAPI(
    title="Visual Pipeline and Platform Evaluation Tool API",
    description="API for Visual Pipeline and Platform Evaluation Tool",
    version="1.0.0",
)
app.openapi = lambda: openapi_schema

# Include routers from different modules
app.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

@app.get("/")
def read_root():
    return {"message": "Visual Pipeline and Platform Evaluation Tool API"}