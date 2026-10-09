from unittest.mock import Mock

import pytest

from csp_bot_commands import *


def test_all():
    assert True


def test_ask_instructions_use_real_file_tools_and_defaults(monkeypatch):
    from csp_bot_commands import ask

    agent_type = Mock()
    monkeypatch.setattr(ask, "Agent", agent_type)
    command = ask.AskCommand()
    monkeypatch.setattr(command, "get_model", lambda: object())
    monkeypatch.setattr(command, "build_toolset", lambda _command: object())
    command.build_agent(object())
    instructions = agent_type.call_args.kwargs["instructions"]
    for term in ("generate_image", "create_file", "read_file", "defaults", "message ID", "Do not fabricate"):
        assert term in instructions


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
