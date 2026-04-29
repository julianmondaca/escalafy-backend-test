"""
Main FastAPI application for the ingestion API.
"""
from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Analytics Ingestion API")

app.include_router(router)
