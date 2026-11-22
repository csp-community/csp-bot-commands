from math import isfinite

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyCommand

__all__ = ("ConvertCommand", "ConvertCommandModel")

_UNITS = {
    "mm": ("length", 0.001, 0),
    "cm": ("length", 0.01, 0),
    "m": ("length", 1, 0),
    "km": ("length", 1000, 0),
    "in": ("length", 0.0254, 0),
    "ft": ("length", 0.3048, 0),
    "yd": ("length", 0.9144, 0),
    "mi": ("length", 1609.344, 0),
    "mg": ("mass", 0.000001, 0),
    "g": ("mass", 0.001, 0),
    "kg": ("mass", 1, 0),
    "oz": ("mass", 0.028349523125, 0),
    "lb": ("mass", 0.45359237, 0),
    "ml": ("volume", 0.001, 0),
    "l": ("volume", 1, 0),
    "ms": ("duration", 0.001, 0),
    "s": ("duration", 1, 0),
    "min": ("duration", 60, 0),
    "h": ("duration", 3600, 0),
    "day": ("duration", 86400, 0),
    "c": ("temperature", 1, 0),
    "f": ("temperature", 5 / 9, -32 * 5 / 9),
    "k": ("temperature", 1, -273.15),
}


class ConvertCommand(ReplyCommand):
    def command(self) -> str:
        return "convert"

    def name(self) -> str:
        return "Convert"

    def help(self) -> str:
        return f"Convert length, mass, volume, duration, or temperature. Supported units: {', '.join(_UNITS)}."

    def usage(self) -> str:
        return "/convert <value> <unit> to <unit>"

    def execute(self, command: BotCommand) -> Message:
        content = f"Usage: {self.usage()}"
        if len(command.args) == 4 and command.args[2].lower() == "to":
            raw_value, source, _, target = command.args
            source, target = source.lower(), target.lower()
            try:
                value = float(raw_value)
                if not isfinite(value):
                    raise ValueError
            except ValueError:
                content = "Enter a finite number to convert."
            else:
                if source not in _UNITS or target not in _UNITS:
                    content = f"Unknown unit. Supported units: {', '.join(_UNITS)}."
                elif _UNITS[source][0] != _UNITS[target][0]:
                    content = "Units must measure the same kind of quantity."
                else:
                    _, source_scale, source_offset = _UNITS[source]
                    _, target_scale, target_offset = _UNITS[target]
                    result = value * (source_scale / target_scale) + (source_offset - target_offset) / target_scale
                    if isfinite(result):
                        content = f"{value:.10g} {source} = {result:.10g} {target}"
                    else:
                        content = "Conversion result is too large."
        return Message(content=content, channel=command.channel, backend=command.backend)


class ConvertCommandModel(BaseCommandModel):
    command: type[BaseCommand] = ConvertCommand
