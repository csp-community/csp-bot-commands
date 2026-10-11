import runpy
import sys
from unittest.mock import Mock

import pytest

from csp_bot_commands import *


def test_all():
    assert True


@pytest.mark.parametrize(
    "command_type,description,syntax",
    [
        (AskCommand, "Ask the AI anything", "/ask <question>"),
        (SummarizeCommand, "AI summary of the last N messages", '/summarize ["Room Name"] [N]'),
        ("GifCommand", "Search and attach a visually reviewed workplace-safe GIF", "/gif <description>"),
    ],
)
def test_agent_help_separates_description_and_usage(command_type, description, syntax):
    if command_type == "GifCommand":
        from csp_bot_commands.gif import GifCommand

        command_type = GifCommand

    command = command_type()
    assert command.help().startswith(description)
    assert "Syntax:" not in command.help()
    assert command.usage() == syntax


@pytest.mark.parametrize(
    "module_name,class_name,syntax", [("ask", "AskCommand", "/ask <question>"), ("summarize", "SummarizeCommand", "/summarize [N]")]
)
def test_fallback_help_separates_description_and_usage(monkeypatch, module_name, class_name, syntax):
    from csp_bot_commands import ask, summarize

    module = {"ask": ask, "summarize": summarize}[module_name]
    monkeypatch.setitem(sys.modules, "csp_bot.commands.agent", None)
    monkeypatch.setitem(sys.modules, "pydantic_ai", None)
    command = runpy.run_path(module.__file__)[class_name]()
    assert "requires agent extra" in command.help()
    assert "Syntax:" not in command.help()
    assert command.usage() == syntax


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
