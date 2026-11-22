from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("EpochCommand", "EpochCommandModel")

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


class EpochCommand(ReplyCommand):
    def command(self) -> str:
        return "epoch"

    def name(self) -> str:
        return "Epoch"

    def help(self) -> str:
        return "Convert Unix seconds to a UTC ISO datetime, or an ISO datetime with an explicit offset to Unix seconds."

    def usage(self) -> str:
        return "/epoch <unix-seconds|ISO-datetime>"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}"
        if len(command.args) == 1:
            raw = command.args[0]
            try:
                try:
                    seconds = Decimal(raw)
                except InvalidOperation:
                    instant = datetime.fromisoformat(raw)
                    if instant.tzinfo is None:
                        raise ValueError("ISO datetime requires a UTC offset, such as Z or +05:30.")
                    delta = instant.astimezone(UTC) - _EPOCH
                    micros = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
                    content = format((Decimal(micros) / 1_000_000).normalize(), "f")
                else:
                    if not seconds.is_finite() or not Decimal(-62135596800) <= seconds <= Decimal("253402300799.999999"):
                        raise ValueError("Unix seconds must be finite and within the ISO datetime range (years 1-9999).")
                    if seconds != seconds.quantize(Decimal("0.000001")):
                        raise ValueError("Unix seconds support at most microsecond precision.")
                    instant = _EPOCH + timedelta(microseconds=int(seconds * 1_000_000))
                    content = instant.isoformat().replace("+00:00", "Z")
            except (ValueError, OverflowError, InvalidOperation) as exc:
                content = f"Cannot convert timestamp: {exc}"
        return Message(content=content, channel=command.channel, backend=command.backend)


class EpochCommandModel(BaseCommandModel):
    command: type[BaseCommand] = EpochCommand
