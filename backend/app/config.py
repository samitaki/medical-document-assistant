from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# the .env lives at the repo root, so it is found whether we run from backend/ or the root
ENV_FILE = Path(__file__).parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    anthropic_api_key: str = ""

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "medical_docs"

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chat_model: str = "claude-sonnet-4-5"

    # how many chunks go to the model, and how many qdrant returns for the reranker to sort
    top_k: int = 5
    candidate_k: int = 20

    rerank_enabled: bool = False
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    upload_dir: str = "./uploads"


# settings are read once per process, the app has no reason to reload them
@lru_cache
def get_settings() -> Settings:
    return Settings()
