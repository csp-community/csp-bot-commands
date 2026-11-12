import asyncio
import builtins
import runpy

import pytest

pytest.importorskip("pydantic_ai")
pytest.importorskip("csp_bot.commands.agent")

from chatom import Channel, Message, User
from csp_bot import BotCommand
from csp_bot.commands.agent import AgentCommand
from csp_bot.commands.mcp import MCPServerConfig
from fastmcp import FastMCP
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import Tool
from pydantic_ai.toolsets import FunctionToolset

from csp_bot_commands.ask import AskCommandModel
from csp_bot_commands.summarize import SummarizeCommandModel


@pytest.mark.parametrize("model_type", [AskCommandModel, SummarizeCommandModel])
def test_agent_model_passes_model_and_mcp_configuration(model_type):
    model = model_type(
        model_name="test",
        mcp_servers=[
            {
                "url": "https://tools.example.com/mcp",
                "prefix": "knowledge",
                "tools": ["search"],
            }
        ],
    )

    command = model.create_command()

    assert command.model_name == "test"
    assert len(command.mcp_servers) == 1
    assert command.mcp_servers[0].url == "https://tools.example.com/mcp"
    assert command.mcp_servers[0].tools == ["search"]


@pytest.mark.parametrize("model_type", [AskCommandModel, SummarizeCommandModel])
def test_agent_uses_local_and_allowed_remote_tools(model_type, monkeypatch):
    def read_channel_history() -> str:
        return "channel history"

    def search() -> str:
        return "remote evidence"

    def delete_record() -> str:
        raise AssertionError("A filtered tool must not be called")

    command = model_type().create_command()
    command.mcp_servers = [
        MCPServerConfig(url="https://tools.example.com/mcp", prefix="knowledge", tools=["search"]),
    ]
    remote = FastMCP("knowledge")
    remote.tool(search)
    remote.tool(delete_record)
    model = TestModel(call_tools=["knowledge_search"])
    monkeypatch.setattr(command, "get_model", lambda: model)
    monkeypatch.setattr(command, "build_toolset", lambda _: FunctionToolset(tools=[Tool(read_channel_history, takes_ctx=False)]))
    monkeypatch.setattr(MCPServerConfig, "build_server", lambda _: MCPToolset(remote))
    invocation = BotCommand.model_validate(
        {
            "command": command.command(),
            "backend": "slack",
            "source": User(id="user-1"),
            "channel_id": "channel-1",
            "args": ("hello",),
            "message": Message(id="message-1", channel=Channel(id="channel-1")),
        }
    )

    result = asyncio.run(command.build_agent(invocation).run("Find supporting evidence"))

    assert "remote evidence" in result.output
    assert model.last_model_request_parameters is not None
    assert {tool.name for tool in model.last_model_request_parameters.function_tools} == {
        "read_channel_history",
        "knowledge_search",
    }


@pytest.mark.parametrize("model_type", [AskCommandModel, SummarizeCommandModel])
def test_agent_without_mcp_keeps_local_tools(model_type, monkeypatch):
    def read_channel_history() -> str:
        return "channel history"

    command = model_type().create_command()
    model = TestModel(call_tools=["read_channel_history"])
    monkeypatch.setattr(command, "get_model", lambda: model)
    monkeypatch.setattr(command, "build_toolset", lambda _: FunctionToolset(tools=[Tool(read_channel_history, takes_ctx=False)]))
    invocation = BotCommand.model_validate({"command": command.command(), "backend": "slack", "source": User(id="user-1"), "channel_id": "channel-1"})

    result = asyncio.run(command.build_agent(invocation).run("Summarize this channel"))

    assert "channel history" in result.output
    assert command.mcp_servers == []


def test_summarize_requires_chat_backend_even_with_mcp(monkeypatch):
    command = SummarizeCommandModel().create_command()
    assert isinstance(command, AgentCommand)
    command.mcp_servers = [MCPServerConfig(url="https://tools.example.com/mcp", prefix="knowledge")]
    monkeypatch.setattr(command, "build_toolset", lambda _: None)
    invocation = BotCommand.model_validate({"command": "summarize", "backend": "slack", "source": User(id="user-1"), "channel_id": "channel-1"})

    with pytest.raises(RuntimeError, match="cannot read channel history"):
        command.build_agent(invocation)


@pytest.mark.parametrize("module_name", ["ask", "summarize"])
def test_command_fallback_without_agent_dependencies(module_name, monkeypatch):
    import importlib

    module = importlib.import_module(f"csp_bot_commands.{module_name}")
    original_import = builtins.__import__

    def without_agent(name, *args, **kwargs):
        if name == "csp_bot.commands.agent":
            raise ImportError("Agent dependencies are unavailable")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_agent)
    assert module.__file__ is not None
    fallback = runpy.run_path(module.__file__)
    model_name = "AskCommandModel" if module_name == "ask" else "SummarizeCommandModel"
    command = fallback[model_name]().create_command()
    invocation = BotCommand.model_validate(
        {"command": module_name, "backend": "slack", "source": User(id="user-1"), "channel_id": "channel-1", "channel_name": "general"}
    )

    response = command.execute(invocation)

    assert "requires the `agent` extra" in response.content
