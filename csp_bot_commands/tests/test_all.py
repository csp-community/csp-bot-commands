from unittest.mock import Mock

import pytest

from csp_bot_commands import *


def test_all():
    assert True


def test_summarize_instructions_resolve_user_ids(monkeypatch):
    pytest.importorskip("pydantic_ai")
    from csp_bot_commands import summarize

    agent_type = Mock()
    monkeypatch.setattr(summarize, "Agent", agent_type)
    command = summarize.SummarizeCommand()
    monkeypatch.setattr(command, "get_model", lambda: object())
    monkeypatch.setattr(command, "build_toolset", lambda _command: object())

    command.build_agent(object())

    instructions = agent_type.call_args.kwargs["instructions"]
    assert "display names" in instructions
    assert "lookup_user" in instructions
    assert "numeric user IDs" in instructions
