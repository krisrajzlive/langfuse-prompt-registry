"""Publish, fetch, and promote prompts stored in Langfuse."""
from pathlib import Path
from typing import Any

import yaml
from langfuse import Langfuse

from .config import Settings


def get_client(settings: Settings | None = None) -> Langfuse:
    s = settings or Settings.from_env()
    return Langfuse(
        public_key=s.langfuse_public_key,
        secret_key=s.langfuse_secret_key,
        host=s.langfuse_host,
    )


def load_definition(path: Path) -> dict[str, Any]:
    definition = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key in ("name", "type", "messages"):
        if key not in definition:
            raise ValueError(f"{path}: missing required field '{key}'")
    return definition


def publish(client: Langfuse, definition: dict[str, Any]):
    """Create a new immutable prompt version from a definition file."""
    return client.create_prompt(
        name=definition["name"],
        type=definition["type"],
        prompt=definition["messages"],
        labels=definition.get("labels", []),
        config=definition.get("config", {}),
        commit_message=definition.get("commit_message"),
    )


def fetch(client: Langfuse, name: str, *, label: str | None = None, version: int | None = None):
    """Fetch by version, else by label (default 'production')."""
    if version is not None:
        return client.get_prompt(name, version=version, type="chat")
    return client.get_prompt(name, label=label or "production", type="chat")


def promote(client: Langfuse, name: str, version: int, label: str) -> None:
    """Move a label to a version; moving it back is the rollback."""
    client.update_prompt(name=name, version=version, new_labels=[label])
