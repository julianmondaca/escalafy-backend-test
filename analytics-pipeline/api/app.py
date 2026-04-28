"""
Main FastAPI application for the ingestion API.
"""
from fastapi import FastAPI

app = FastAPI(title="Analytics Ingestion API")

# TODO: Include routes from api.routes and configure lifespan/startup events
