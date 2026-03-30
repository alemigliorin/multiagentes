
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for the multi-agent backend.
    Loads from environment variables and provides defaults.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None

    # Supabase Configuration
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_DB_URL: str | None = None

    # App Configuration
    CORS_ORIGINS: str = "https://multiagentes.migliorinlabs.cloud,https://api.migliorinlabs.cloud,http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001"
    SKIP_PDF_LOAD: bool = False

    # Model Defaults
    DEFAULT_MODEL_ID: str = "gpt-5-nano"
    ORCHESTRATOR_MODEL_ID: str = "gpt-5-mini"
    CRIADOR_MIDIA_MODEL_ID: str = "gemini-2.5-flash"

    # Database Constants
    SESSION_TABLE: str = "sessions"
    PDF_TABLE: str = "pdf_documents"

    # Storage Paths
    UPLOAD_TMP_DIR: str = "tmp/uploads"
    VIDEO_BASE_DIR: str = "videos"

settings = Settings()
