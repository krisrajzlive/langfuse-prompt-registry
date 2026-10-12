from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prompt_registry import registry
from prompt_registry.chains import to_langchain_prompt

DEFINITION = Path(__file__).parent.parent / "prompts" / "support_reply.yaml"


def test_definition_loads_with_required_fields():
    d = registry.load_definition(DEFINITION)
    assert d["name"] == "support-reply" and d["type"] == "chat"
    assert [m["role"] for m in d["messages"]] == ["system", "user"]


def test_definition_missing_field_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: x\n")
    with pytest.raises(ValueError):
        registry.load_definition(bad)


def test_publish_passes_definition_to_langfuse():
    client = MagicMock()
    registry.publish(client, registry.load_definition(DEFINITION))
    kwargs = client.create_prompt.call_args.kwargs
    assert kwargs["name"] == "support-reply" and kwargs["labels"] == ["staging"]
    assert kwargs["config"]["temperature"] == 0.2


def test_fetch_defaults_to_production_label():
    client = MagicMock()
    registry.fetch(client, "support-reply")
    client.get_prompt.assert_called_once_with("support-reply", label="production", type="chat")


def test_promote_moves_label():
    client = MagicMock()
    registry.promote(client, "support-reply", 2, "production")
    client.update_prompt.assert_called_once_with(
        name="support-reply", version=2, new_labels=["production"]
    )


def test_prompt_variables_are_converted_for_langchain():
    managed = MagicMock()
    managed.get_langchain_prompt.return_value = [
        ("system", "Tone: {tone}"),
        ("user", "Issue: {issue}"),
    ]
    template = to_langchain_prompt(managed)
    msgs = template.invoke({"tone": "calm", "issue": "login"}).to_messages()
    assert msgs[0].content == "Tone: calm" and msgs[1].content == "Issue: login"
