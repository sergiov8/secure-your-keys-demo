"""Shared settings read from the environment.

Every sample reads the same three variables, so one export block in your
shell configures the whole repository.
"""

import os
from dataclasses import dataclass

DEFAULT_LOCATION = "us-central1"
DEFAULT_MODEL = "gemini-3.8-flash"


class ConfigError(RuntimeError):
    """Raised when a required setting is missing."""


@dataclass(frozen=True)
class Settings:
    project: str
    location: str
    model: str


def load_settings(env=None) -> Settings:
    """Reads GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION and GEMINI_MODEL."""
    env = os.environ if env is None else env
    project = env.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise ConfigError(
            "GOOGLE_CLOUD_PROJECT is not set. Run: "
            "export GOOGLE_CLOUD_PROJECT=your-project-id"
        )
    return Settings(
        project=project,
        location=env.get("GOOGLE_CLOUD_LOCATION", "").strip() or DEFAULT_LOCATION,
        model=env.get("GEMINI_MODEL", "").strip() or DEFAULT_MODEL,
    )
