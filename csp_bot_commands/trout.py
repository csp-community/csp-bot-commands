import logging
from random import choice
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand, mention_user

from .common import (
    COLORS,
    FISH,
    SHAKEPEREAN_MODIFIERS_ONE,
    SHAKEPEREAN_MODIFIERS_TWO,
    SHAKESPEREAN_NOUNS,
    a_or_an,
)

__all__ = (
    "TroutSlapCommandModel",
    "TroutSlapCommand",
)


log = logging.getLogger(__name__)


class TroutSlapCommand(ReplyToOtherCommand):
    def command(self) -> str:
        return "slap"

    def name(self) -> str:
        return "Slap"

    def help(self) -> str:
        return "Slap someone with a wet fish. Syntax: /slap <user> [/channel <channel>]"

    def execute(self, command: BotCommand) -> Optional[Message]:
        log.info(f"Trout command: {command}")
        author = mention_user(command.source.id, command.backend)
        target = [mention_user(user.id, command.backend) for user in command.targets]
        if not target:
            return
        color = choice(COLORS)
        fish = choice(FISH) if "random" in command.args else "trout"
        modifier_one = choice(SHAKEPEREAN_MODIFIERS_ONE)
        modifier_two = choice(SHAKEPEREAN_MODIFIERS_TWO)
        noun = choice(SHAKESPEREAN_NOUNS)
        message = (
            f'{author} slaps {" ".join(target)} with {a_or_an(color)} {color} {fish} while yelling "Thou {modifier_one}, {modifier_two} {noun}!"'
        )
        return Message(
            msg=message,
            channel=command.channel,
            backend=command.backend,
        )


class TroutSlapCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = TroutSlapCommand
