from uuid import uuid4

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("UuidCommand", "UuidCommandModel")


class UuidCommand(ReplyCommand):
    def command(self) -> str:
        return "uuid"

    def name(self) -> str:
        return "UUID"

    def help(self) -> str:
        return "Generate a random version 4 UUID."

    def usage(self) -> str:
        return "/uuid"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}" if command.args else str(uuid4())
        return Message(content=content, channel=command.channel, backend=command.backend)


class UuidCommandModel(BaseCommandModel):
    command: type[BaseCommand] = UuidCommand
