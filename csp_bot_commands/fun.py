import logging
from random import choice
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand, mention_user

from .common import (
    BEER,
    BUSH,
    CHUCK_NORRIS,
    CHURCHILL,
    COCKTAILS,
    COLORS,
    COMPLIMENTS,
    CONFUCIUS,
    CONSPIRACY,
    CORPORATE,
    DAD_JOKES,
    DRINKING_ESTABLISHMENTS,
    DUNE,
    FORTUNE,
    GERMAN,
    HAIKU,
    HEMINGWAY,
    HITCHHIKER,
    ICELANDIC,
    LATIN,
    MAGIC8,
    MOTIVATIONAL,
    NIETZSCHE,
    PIRATE,
    PRATCHETT,
    PROGRAMMING_JOKES,
    SHAKEPEREAN_MODIFIERS_ONE,
    SHAKEPEREAN_MODIFIERS_TWO,
    SHAKESPEREAN_NOUNS,
    SOVIET,
    STARWARS,
    STOIC,
    TOLKIEN,
    TWAIN,
    WHISKEY,
    WILDE,
    WINE,
    YOGI,
    ZEN,
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
        elif "shakespeare" in command.args:
            insult = f"Thou {choice(SHAKEPEREAN_MODIFIERS_ONE)} {choice(SHAKEPEREAN_MODIFIERS_TWO)} {choice(SHAKESPEREAN_NOUNS)}!"
            message = f'{author} hurls a Shakespearean insult at {" ".join(target)}: "{insult}"'
        elif "yogi" in command.args:
            quote = choice(YOGI)
            message = f'{author} shares some Yogi Berra wisdom with {" ".join(target)}: "{quote}"'
        elif "tolkien" in command.args:
            quote = choice(TOLKIEN)
            message = f'{author} offers {" ".join(target)} wisdom from Middle-earth: "{quote}"'
        elif "fortune" in command.args:
            quote = choice(FORTUNE)
            message = f'{author} cracks open a fortune cookie for {" ".join(target)}: "{quote}"'
        elif "pratchett" in command.args:
            quote = choice(PRATCHETT)
            message = f'{author} enlightens {" ".join(target)} with Pratchett: "{quote}"'
        elif "wilde" in command.args:
            quote = choice(WILDE)
            message = f'{author} graces {" ".join(target)} with an Oscar Wilde quip: "{quote}"'
        elif "wine" in command.args:
            venue = choice(DRINKING_ESTABLISHMENTS)
            wine = choice(WINE)
            message = f'{author} calls {" ".join(target)} over to the {venue} for a glass of wine: "How about {a_or_an(wine)} {wine}?"'
        elif "nietzsche" in command.args:
            quote = choice(NIETZSCHE)
            message = f'{author} darkly enlightens {" ".join(target)} with Nietzsche: "{quote}"'
        elif "twain" in command.args:
            quote = choice(TWAIN)
            message = f'{author} shares a Mark Twain quip with {" ".join(target)}: "{quote}"'
        elif "zen" in command.args:
            quote = choice(ZEN)
            message = f'{author} offers {" ".join(target)} a moment of zen: "{quote}"'
        elif "stoic" in command.args:
            quote = choice(STOIC)
            message = f'{author} offers {" ".join(target)} some Stoic counsel: "{quote}"'
        elif "churchill" in command.args:
            quote = choice(CHURCHILL)
            message = f'{author} channels Churchill for {" ".join(target)}: "{quote}"'
        elif "confucius" in command.args:
            quote = choice(CONFUCIUS)
            message = f'{author} shares ancient wisdom with {" ".join(target)}: "Confucius says: {quote}"'
        elif "starwars" in command.args:
            quote = choice(STARWARS)
            message = f'{author} reaches for the Force on behalf of {" ".join(target)}: "{quote}"'
        elif "hitch" in command.args:
            quote = choice(HITCHHIKER)
            message = f'{author} consults the Guide for {" ".join(target)}: "{quote}"'
        elif "hemingway" in command.args:
            quote = choice(HEMINGWAY)
            message = f'{author} pours a drink and quotes Hemingway for {" ".join(target)}: "{quote}"'
        elif "dad" in command.args:
            joke = choice(DAD_JOKES)
            message = f'{author} subjects {" ".join(target)} to a dad joke: "{joke}"'
        elif "chuck" in command.args:
            fact = choice(CHUCK_NORRIS)
            message = f'{author} informs {" ".join(target)} of a Chuck Norris fact: "{fact}"'
        elif "soviet" in command.args:
            soviet = choice(SOVIET)
            message = f'{author} reminds {" ".join(target)}: "{soviet}"'
        elif "conspiracy" in command.args:
            theory = choice(CONSPIRACY)
            message = f'{author} whispers to {" ".join(target)}: "{theory}"'
        elif "magic8" in command.args:
            response = choice(MAGIC8)
            message = f'{author} shakes the Magic 8-Ball for {" ".join(target)}: "\U0001f3b1 {response}"'
        elif "compliment" in command.args:
            compliment = choice(COMPLIMENTS)
            message = f'{author} lavishes praise on {" ".join(target)}: "{compliment}"'
        elif "latin" in command.args:
            phrase = choice(LATIN)
            message = f'{author} schools {" ".join(target)} in Latin: "{phrase}"'
        elif "pirate" in command.args:
            taunt = choice(PIRATE)
            message = f'{author} makes {" ".join(target)} walk the plank: "{taunt}"'
        elif "corporate" in command.args:
            buzzword = choice(CORPORATE)
            message = f'{author} synergizes with {" ".join(target)}: "{buzzword}"'
        elif "motivational" in command.args:
            poster = choice(MOTIVATIONAL)
            message = f'{author} puts a poster on {" ".join(target)}\u2019s wall: "{poster}"'
        elif "haiku" in command.args:
            haiku = choice(HAIKU)
            message = f"{author} composes a haiku for {' '.join(target)}:\n{haiku}"
        elif "programming" in command.args:
            joke = choice(PROGRAMMING_JOKES)
            message = f'{author} shares a programming joke with {" ".join(target)}: "{joke}"'
        elif "whiskey" in command.args:
            venue = choice(DRINKING_ESTABLISHMENTS)
            dram = choice(WHISKEY)
            message = f'{author} calls {" ".join(target)} over to the {venue} for a dram: "How about {a_or_an(dram)} {dram}?"'
        elif "highfive" in command.args:
            color = choice(COLORS)
            message = f"{author} gives {' '.join(target)} a magnificent {color} high five! \u270b"
        else:
            return None
        return Message(
            msg=message,
            channel=command.channel,
            backend=command.backend,
        )


class FunCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = FunCommand
