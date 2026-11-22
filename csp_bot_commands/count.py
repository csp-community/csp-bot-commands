from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("CountCommand", "CountCommandModel")


class CountCommand(ReplyCommand):
    raw_args = True

    def command(self) -> str:
        return "count"

    def name(self) -> str:
        return "Count"

    def help(self) -> str:
        return "Count Unicode characters, whitespace-separated words, and lines in text."

    def usage(self) -> str:
        return "/count <text>"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}"
        if len(command.args) == 1:
            text = command.args[0]
            content = f"Characters: {len(text)}\nWords: {len(text.split())}\nLines: {len(text.splitlines())}"
        return Message(content=content, channel=command.channel, backend=command.backend)


class CountCommandModel(BaseCommandModel):
    command: type[BaseCommand] = CountCommand
