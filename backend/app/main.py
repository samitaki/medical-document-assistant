from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router
from app.config import get_settings
from app.errors import ServiceError
from ingest.store import embedder


@asynccontextmanager
async def lifespan(app: FastAPI):
    # the onnx weights take a few seconds to load, so pay that before the first request
    embedder()
    if get_settings().rerank_enabled:
        from rag.rerank import model as rerank_model

        rerank_model()
    yield


app = FastAPI(title="medical document assistant", lifespan=lifespan)

# the frontend runs on a different port in dev, so it needs cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(ServiceError)
async def service_error(request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"error": exc.message})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
