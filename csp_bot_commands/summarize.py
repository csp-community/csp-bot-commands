"""SummarizeCommand — AI-powered channel summary.

Usage::

    /summarize [N]
    /summarize "Room Name" [N]
    /summarize "Room Name" [N] /room "Output Room"

Summarizes the last N messages (default 50) in the current channel,
or in the named room if specified.  The /room directive controls where
the summary is posted (defaults to the channel where the command was issued).

Reply to the bot's response to ask follow-up questions about the summary.
"""

import logging
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand

try:
    from chatom.agent.toolset import AccessPolicy
    from csp_bot.commands.agent import AgentCommand
    from pydantic_ai import Agent

    _HAS_AGENT = True
except ImportError:
    _HAS_AGENT = False

log = logging.getLogger(__name__)

__all__ = (
    "SummarizeCommandModel",
    "SummarizeCommand",
)


def _parse_summarize_args(command: BotCommand) -> tuple[Optional[str], int]:
    """Parse summarize args into (source_room_name, message_count).

    Args are whatever remains after /room has been stripped by the bot.
    Heuristics:
      - A purely numeric arg → message count
      - A non-numeric arg → source room name
    """
    source_room: Optional[str] = None
    count = 50

    for arg in command.args:
        try:
            count = int(arg)
        except ValueError:
            source_room = arg

    return source_room, count


if _HAS_AGENT:

    class SummarizeCommand(AgentCommand):
        """Summarize recent channel messages using an AI agent."""

        def command(self) -> str:
            return "summarize"

        def name(self) -> str:
            return "Summarize"

        def help(self) -> str:
            return '/summarize ["Room Name"] [N] — AI summary of the last N messages (default 50)'

        def build_agent(self, command: BotCommand) -> Agent:
            toolset = self.build_toolset(command)
            if toolset is None:
                raise RuntimeError(f"No backend available for {command.backend}; cannot read channel history.")
            return Agent(
                self.get_model(),
                toolsets=[toolset],
                instructions=(
                    "You are a concise summarizer. When asked to summarize, "
                    "use the read_channel_history tool to fetch recent messages, "
                    "then provide a clear, organized summary. Group related topics "
                    "together. Highlight action items and decisions."
                ),
            )

        def build_prompt(self, command: BotCommand) -> str:
            source_room, n = _parse_summarize_args(command)

            if source_room:
                # User specified a source room by name
                return (
                    f'Read the last {n} messages from the channel named "{source_room}" '
                    "using the read_channel_history tool, "
                    "then provide a concise summary. Group by topic, highlight decisions and action items."
                )
            else:
                # Default: read from the original invoking channel (not /room redirect)
                # command.message.channel_id is the channel where the user typed the command
                origin_channel_id = command.message.channel_id if command.message and command.message.channel_id else command.channel_id
                origin_channel_name = ""
                if command.message and command.message.channel:
                    origin_channel_name = command.message.channel.name or ""
                if not origin_channel_name:
                    origin_channel_name = origin_channel_id
                return (
                    f'Read the last {n} messages from the channel with id="{origin_channel_id}" '
                    f'(name: "{origin_channel_name}") using the read_channel_history tool, '
                    "then provide a concise summary. Group by topic, highlight decisions and action items."
                )

        def build_access_policy(self, command: BotCommand) -> "AccessPolicy":
            """Allow cross-channel access when a source room is specified."""
            source_room, _ = _parse_summarize_args(command)

            # The origin channel is where the user typed the command
            origin_channel_id = command.message.channel_id if command.message and command.message.channel_id else command.channel_id

            if source_room:
                # Cross-channel: rely on membership check to verify access
                return AccessPolicy(
                    requesting_user=command.source,
                    invoking_channel_id=origin_channel_id,
                    restrict_to_invoking_channel=False,
                    require_membership=True,
                    block_dm_reads=True,
                )
            else:
                # Same-channel: restrict to the origin channel
                return AccessPolicy(
                    requesting_user=command.source,
                    invoking_channel_id=origin_channel_id,
                    restrict_to_invoking_channel=True,
                    require_membership=True,
                    block_dm_reads=True,
                )

        def wrap_symphony_output(self, messageml: str, command: BotCommand) -> str:
            """Wrap summary in a collapsible expandable-card."""
            source_room, n = _parse_summarize_args(command)
            if source_room:
                header_text = f"Summary of {source_room} ({n} messages)"
            else:
                header_text = f"Channel summary ({n} messages)"
            return f'<expandable-card state="collapsed"><header><b>{header_text}</b></header><body>{messageml}</body></expandable-card>'

else:
    from csp_bot import ReplyCommand

    class SummarizeCommand(ReplyCommand):  # type: ignore[no-redef]
        def command(self) -> str:
            return "summarize"

        def name(self) -> str:
            return "Summarize"

        def help(self) -> str:
            return "/summarize [N] \u2014 AI summary (requires agent extra)"

        def preexecute(self, command: BotCommand) -> BotCommand:
            return command

        def execute(self, command: BotCommand):
            from chatom import Message

            return Message(
                content="The /summarize command requires the `agent` extra. Install with: pip install csp-bot[agent]",
                channel=command.channel,
                metadata={"backend": command.backend},
            )


class SummarizeCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = SummarizeCommand
