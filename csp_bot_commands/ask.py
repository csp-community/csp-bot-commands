"""AskCommand — free-form Q&A via a pydantic-ai agent.

Usage::

    /ask <question>

Reply to the bot's response to continue the conversation.
"""

import logging
from typing import Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand

try:
    from csp_bot.commands.agent import AgentCommand
    from pydantic_ai import Agent

    _HAS_AGENT = True
except ImportError:
    _HAS_AGENT = False

log = logging.getLogger(__name__)

__all__ = (
    "AskCommandModel",
    "AskCommand",
)


if _HAS_AGENT:

    class AskCommand(AgentCommand):
        """Free-form Q&A command. Replies to the bot continue the conversation."""

        def command(self) -> str:
            return "ask"

        def name(self) -> str:
            return "Ask"

        def help(self) -> str:
            return "/ask <question> \u2014 Ask the AI anything (reply to continue)"

        def build_agent(self, command: BotCommand) -> Agent:
            toolset = self.build_toolset(command)
            return Agent(
                self.get_model(),
                toolsets=[toolset] if toolset else [],
                instructions=(
                    "You are a helpful assistant in a team chat. Be concise and direct. "
                    "Use markdown formatting when helpful. "
                    "Images the user attaches to their message are provided to you directly — "
                    "look at them to answer. To share a file, image, chart, or document back to "
                    "the chat, use the upload_file tool with base64-encoded data. To read other "
                    "files or documents posted in the channel, use list_recent_attachments then "
                    "download_attachment."
                ),
            )

        def build_prompt(self, command: BotCommand) -> str:
            return " ".join(command.args) if command.args else "Hello"

else:
    # Fallback when agent extra is not installed
    from csp_bot import ReplyCommand

    class AskCommand(ReplyCommand):  # type: ignore[no-redef]
        def command(self) -> str:
            return "ask"

        def name(self) -> str:
            return "Ask"

        def help(self) -> str:
            return "/ask <question> \u2014 Ask the AI (requires agent extra)"

        def preexecute(self, command: BotCommand) -> BotCommand:
            return command

        def execute(self, command: BotCommand):
            from chatom import Message

            return Message(
                content="The /ask command requires the `agent` extra. Install with: pip install csp-bot[agent]",
                channel=command.channel,
                metadata={"backend": command.backend},
            )


class AskCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = AskCommand
