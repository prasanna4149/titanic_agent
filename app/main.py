from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
from scalar_fastapi import get_scalar_api_reference

from app.core.config import settings
from app.services.dataset_loader import dataset_loader
from app.agent.agent_builder import agent_builder
from app.routes import router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("Initializing API application...")

    # 1. Load Titanic CSV once into memory
    try:
        dataset_loader.load_dataset()
    except Exception as e:
        logger.error(f"Failed to load dataset on startup: {e}")

    # 2. Pre-build the LangGraph agent (no re-init per request)
    try:
        agent_builder.build_agent()
    except Exception as e:
        logger.error(f"Failed to build agent on startup: {e}")

    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("Shutting down API application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent chat agent for the Titanic dataset powered by LangChain + Groq (Llama 3.3-70b).",
    version="1.0.0",
    # Disable the built-in Swagger UI & ReDoc so Scalar is the sole docs UI
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ────────────────────────────────────────────────────────────────
app.include_router(router)

# ── Scalar API reference ──────────────────────────────────────────────────────
@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title=settings.PROJECT_NAME,
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
