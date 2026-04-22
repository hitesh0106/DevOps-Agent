"""
DevOps Agent — Application Settings
=====================================
Centralized configuration using Pydantic Settings.
All values are loaded from environment variables or .env file.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class LLMSettings(BaseSettings):
    """LLM Provider Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    llm_provider: str = Field(default="anthropic", description="LLM provider: 'anthropic' or 'openai'")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", description="Anthropic model name")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")


class DatabaseSettings(BaseSettings):
    """Database Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR / 'devops_agent.db'}",
        description="Database connection URL"
    )


class RedisSettings(BaseSettings):
    """Redis Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")


class GitHubSettings(BaseSettings):
    """GitHub Integration Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    github_token: str = Field(default="", description="GitHub personal access token")
    github_webhook_secret: str = Field(default="", description="GitHub webhook secret")
    github_default_org: str = Field(default="", description="Default GitHub organization")


class DockerSettings(BaseSettings):
    """Docker Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    docker_host: str = Field(default="unix:///var/run/docker.sock", description="Docker daemon socket")
    docker_registry: str = Field(default="docker.io", description="Docker registry URL")
    docker_username: str = Field(default="", description="Docker registry username")
    docker_password: str = Field(default="", description="Docker registry password")


class KubernetesSettings(BaseSettings):
    """Kubernetes Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    kubeconfig_path: str = Field(default="~/.kube/config", description="Kubeconfig file path")
    k8s_default_namespace: str = Field(default="default", description="Default Kubernetes namespace")


class MonitoringSettings(BaseSettings):
    """Monitoring Stack Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    prometheus_url: str = Field(default="http://localhost:9090", description="Prometheus URL")
    grafana_url: str = Field(default="http://localhost:3000", description="Grafana URL")
    grafana_api_key: str = Field(default="", description="Grafana API key")
    alertmanager_url: str = Field(default="http://localhost:9093", description="Alertmanager URL")


class NotificationSettings(BaseSettings):
    """Notification Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    slack_webhook_url: str = Field(default="", description="Slack webhook URL")
    slack_channel: str = Field(default="#devops-alerts", description="Slack channel")
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")


class AgentSettings(BaseSettings):
    """Agent Behavior Configuration"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    agent_max_iterations: int = Field(default=15, description="Max ReAct loop iterations")
    agent_timeout_seconds: int = Field(default=300, description="Agent task timeout in seconds")
    agent_memory_collection: str = Field(default="incident_history", description="ChromaDB collection name")
    chroma_persist_dir: str = Field(
        default=str(BASE_DIR / "data" / "chromadb"),
        description="ChromaDB persistence directory"
    )


class Settings(BaseSettings):
    """
    Master Settings — Aggregates all configuration sections.
    
    Usage:
        from config.settings import settings
        print(settings.api_port)
        print(settings.llm.anthropic_model)
    """
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────
    simulation_mode: bool = Field(default=True, description="Use mock/simulated responses")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # ── API ───────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_key: str = Field(default="dev-api-key-change-me", description="API authentication key")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated CORS origins"
    )

    # ── Sub-configurations ────────────────────
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    docker: DockerSettings = Field(default_factory=DockerSettings)
    kubernetes: KubernetesSettings = Field(default_factory=KubernetesSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def is_simulation(self) -> bool:
        """Check if running in simulation mode."""
        return self.simulation_mode


# Global settings instance — import this everywhere
settings = Settings()
