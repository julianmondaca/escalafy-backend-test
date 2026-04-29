"""
Main FastAPI application for the reporting API.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.connection import init_pool, close_pool
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages lifespan events for the FastAPI app.
    """
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="Analytics Reporting API", lifespan=lifespan)
app.include_router(router)
