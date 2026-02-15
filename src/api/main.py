"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import logger
from src.api.routes import health, documents, query


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="Production-ready RAG application for document Q&A",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(query.router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )