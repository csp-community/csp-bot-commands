from random import choice

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("ChooseCommand", "ChooseCommandModel")


class ChooseCommand(ReplyCommand):
    def command(self) -> str:
        return "choose"

    def name(self) -> str:
        return "Choose"

    def help(self) -> str:
        return "Pick one option at random. Use double quotes for options containing spaces."

    def usage(self) -> str:
        return "/choose <option> <option> [<option> ...]"

    def execute(self, command: BotCommand) -> Message:
        options = [arg.strip() for arg in command.args if arg.strip()]
        content = choice(options) if len(options) >= 2 else f"Usage: {self.usage()}"
        return Message(content=content, channel=command.channel, backend=command.backend)


class ChooseCommandModel(BaseCommandModel):
    command: type[BaseCommand] = ChooseCommand
