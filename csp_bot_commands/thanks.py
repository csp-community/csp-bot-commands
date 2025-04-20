import logging
from random import choice, randint
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand, mention_user

from .common import COLORS, MONEY, RANDOM_SINGULAR_NOUNS, a_or_an

__all__ = (
    "ThanksCommandModel",
    "ThanksCommand",
)

log = logging.getLogger(__name__)


class ThanksCommand(ReplyToOtherCommand):
    def command(self) -> str:
        return "thanks"

    def name(self) -> str:
        return "Thanks"

    def help(self) -> str:
        return "Thank someone. Syntax: /thanks <user> [/channel <channel>]"

    def execute(self, command: BotCommand) -> Optional[Message]:
        log.info(f"Thanks command: {command}")
        author = mention_user(command.source.id, command.backend)
        target = [mention_user(user.id, command.backend) for user in command.targets]
        if not target:
            return

        if "cash" in command.args:
            amount = randint(1, 11) * choice((10, 100))
            payment_type = choice(MONEY)
            message = f"{author} thanks {' '.join(target)} with ${amount} in {payment_type}"
        else:
            color = choice(COLORS)
            gift = choice(RANDOM_SINGULAR_NOUNS)
            message = f"{author} thanks {' '.join(target)} with {a_or_an(color)} {color} {gift}"
        return Message(
            msg=message,
            channel=command.channel,
            backend=command.backend,
        )


class ThanksCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = ThanksCommand
