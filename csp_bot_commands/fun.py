import logging
from random import choice
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand, mention_user

from .common import (
    BEER,
    BUSH,
    COCKTAILS,
    DRINKING_ESTABLISHMENTS,
    DUNE,
    GERMAN,
    ICELANDIC,
    a_or_an,
)

__all__ = (
    "FunCommandModel",
    "FunCommand",
)
log = logging.getLogger(__name__)


class FunCommand(ReplyToOtherCommand):
    def command(self) -> str:
        return "_fun"

    def name(self) -> str:
        return ""

    def help(self) -> str:
        return ""

    def execute(self, command: BotCommand) -> Optional[Message]:
        log.info(f"Fun command: {command}")
        author = mention_user(command.source.id, command.backend)
        target = [mention_user(user.id, command.backend) for user in command.targets]
        if not target:
            return
        if "icelandic" in command.args:
            message = f'{author} consoles {" ".join(target)} with an Icelandic folk saying: "{choice(ICELANDIC)}"'
        elif "german" in command.args:
            message = f"{author} teaches {' '.join(target)} some German: {choice(GERMAN)}. Prost!"
        elif "cocktail" in command.args:
            venue = choice(DRINKING_ESTABLISHMENTS)
            cocktail = choice(COCKTAILS)
            message = f'{author} calls {" ".join(target)} over to the {venue} for a cocktail: "How about {a_or_an(cocktail)} {cocktail}?"'
        elif "beer" in command.args:
            venue = choice(DRINKING_ESTABLISHMENTS)
            beer = choice(BEER)
            message = f'{author} calls {" ".join(target)} over to the {venue} for a beer: "How about {a_or_an(beer)} {beer}?"'
        elif "dune" in command.args:
            quote = choice(DUNE)
            message = f'{author} scrapes wisdom for {" ".join(target)} off the sands of Arrakis: "{quote}"'
        elif "bush" in command.args:
            quote = choice(BUSH)
            message = f'{author} impresses {" ".join(target)} with a quote from George W. Bush: "{quote}"'
        else:
            return None
        return Message(
            msg=message,
            channel=command.channel,
            backend=command.backend,
        )


class FunCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = FunCommand
