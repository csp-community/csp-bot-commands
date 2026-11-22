import json

from chatom import Attachment
from chatom.format import CodeBlock, FormattedMessage
from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("JsonCommand", "JsonCommandModel")


class JsonCommand(ReplyCommand):
    raw_args = True

    def command(self) -> str:
        return "json"

    def name(self) -> str:
        return "JSON"

    def help(self) -> str:
        return "Validate and pretty-print JSON. Paste the JSON directly after the command."

    def usage(self) -> str:
        return "/json <JSON>"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}"
        attachments = []
        if len(command.args) == 1:
            try:
                formatted = json.dumps(json.loads(command.args[0]), indent=2, allow_nan=False)
            except (ValueError, RecursionError) as exc:
                content = f"Invalid JSON: {exc}"
            else:
                if len(formatted) > 1500:
                    content = "Formatted JSON attached."
                    attachments = [Attachment(filename="formatted.json", content_type="application/json", data=formatted.encode("utf-8"))]
                else:
                    content = FormattedMessage(content=[CodeBlock(content=formatted, language="json")]).render_for(command.backend)
        return Message(content=content, attachments=attachments, channel=command.channel, backend=command.backend)


class JsonCommandModel(BaseCommandModel):
    command: type[BaseCommand] = JsonCommand
