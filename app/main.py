from fastapi import FastAPI
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.profiles import router as profiles_router
from app.api.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Identity & Profile Microservice for E-Learning Platform",
    version="1.0.0",
    docs_url="/docs",  
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(profiles_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}