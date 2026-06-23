"""
CowSense AI — App Configuration
app/config.py

Manages all environment variables with Pydantic Settings.
Falls back gracefully to demo mode if keys are missing.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # Featherless
    featherless_api_key: str = ""
    featherless_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    featherless_base_url: str = "https://api.featherless.ai/v1"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "cowsense2026"

    # Africa's Talking
    at_username: str = "sandbox"
    at_api_key: str = ""
    at_sender_id: str = "CowSense"

    # App
    app_env: str = "development"
    app_port: int = 8000
    debug: bool = True

    @property
    def is_demo_mode(self) -> bool:
        """True if Claude API key is not set — uses mock responses."""
        return not self.anthropic_api_key or self.anthropic_api_key.startswith("sk-ant-your")

    @property
    def has_neo4j(self) -> bool:
        """True if Neo4j is configured beyond localhost default."""
        return "databases.neo4j.io" in self.neo4j_uri or self.neo4j_uri != "bolt://localhost:7687"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
