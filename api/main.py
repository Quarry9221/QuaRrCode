from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from api.dependencies import get_db
from api.routers import users, qr_codes
from database.repository import init_db
import asyncio

import logging
from config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="QR Bot API", description="API for QR Code Generator Telegram Bot", version="1.0.0")

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(qr_codes.router, prefix="/qr_codes", tags=["qr_codes"])

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key")
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return api_key

@app.get("/health")
async def health_check():
    return {"status": "healthy"}