from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("TimeCommand", "TimeCommandModel")


class TimeCommand(ReplyCommand):
    def command(self) -> str:
        return "time"

    def name(self) -> str:
        return "Time"

    def help(self) -> str:
        return "Convert a local ISO date and time, or now, between IANA timezones. Include a date for daylight saving time."

    def usage(self) -> str:
        return "/time <YYYY-MM-DDTHH:MM|now> <source-zone> in <target-zone> [<target-zone> ...]"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}"
        if len(command.args) >= 4 and command.args[2].lower() == "in":
            raw_time, source_name, _, *target_names = command.args
            try:
                zones = [ZoneInfo(name) for name in [source_name, *target_names]]
                source = zones[0]
                if raw_time.lower() == "now":
                    instant = datetime.now(source).astimezone(UTC)
                else:
                    try:
                        local = datetime.fromisoformat(raw_time)
                    except ValueError:
                        raise ValueError("Use an ISO date and time such as 2026-11-22T09:00, or now.") from None
                    if local.tzinfo is not None:
                        raise ValueError("Supply a local date and time without a UTC offset, followed by its timezone.")
                    aware = local.replace(tzinfo=source)
                    instant = aware.astimezone(UTC)
                    if instant.astimezone(source).replace(tzinfo=None) != local:
                        raise ValueError("That local time does not exist because of a daylight saving transition.")
                    if aware.utcoffset() != local.replace(tzinfo=source, fold=1).utcoffset():
                        raise ValueError("That local time is ambiguous because of a daylight saving transition. Supply the time in UTC instead.")
                content = "\n".join(f"{instant.astimezone(zone).isoformat(timespec='seconds')} {zone.key}" for zone in zones)
            except ZoneInfoNotFoundError as exc:
                content = f"Unknown timezone: {exc.args[0]}. Use an IANA name such as America/New_York."
            except ValueError as exc:
                content = str(exc)
        return Message(content=content, channel=command.channel, backend=command.backend)


class TimeCommandModel(BaseCommandModel):
    command: type[BaseCommand] = TimeCommand
