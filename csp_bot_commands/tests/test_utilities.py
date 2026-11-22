from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from chatom import Message, User
from csp_bot import Bot, BotCommand, BotConfig
from csp_bot.commands import HelpCommandModel
from hydra.utils import instantiate

from csp_bot_commands import ChooseCommand, ConvertCommand, TimeCommand


def _command(args, backend="slack"):
    return BotCommand.model_validate(
        {
            "args": tuple(args),
            "backend": backend,
            "channel_id": "room",
            "channel_name": "general",
            "source": User(id="user"),
        }
    )


def test_choose_returns_one_complete_option():
    options = ("pizza", "fish and chips", "sushi")
    with patch("csp_bot_commands.choose.choice", return_value="fish and chips") as choice:
        result = ChooseCommand().execute(_command(options))
    choice.assert_called_once_with(list(options))
    assert result.content == "fish and chips"


@pytest.mark.parametrize("args", [(), ("pizza",), ("", "pizza"), (" ", "")])
def test_choose_requires_two_nonempty_options(args):
    assert "Usage: /choose" in ChooseCommand().execute(_command(args)).content


@pytest.mark.parametrize(
    "args,expected",
    [
        (("10", "mi", "to", "km"), "10 mi = 16.09344 km"),
        (("1", "kg", "to", "lb"), "1 kg = 2.204622622 lb"),
        (("2.5", "l", "to", "ml"), "2.5 l = 2500 ml"),
        (("90", "min", "to", "h"), "90 min = 1.5 h"),
        (("32", "F", "to", "C"), "32 f = 0 c"),
        (("100", "c", "to", "f"), "100 c = 212 f"),
        (("0", "k", "to", "c"), "0 k = -273.15 c"),
        (("-40", "c", "to", "f"), "-40 c = -40 f"),
        (("1e3", "m", "to", "km"), "1000 m = 1 km"),
        (("12", "m", "to", "m"), "12 m = 12 m"),
        (("1e308", "km", "to", "km"), "1e+308 km = 1e+308 km"),
        (("1e-20", "c", "to", "c"), "1e-20 c = 1e-20 c"),
    ],
)
def test_convert_units(args, expected):
    assert ConvertCommand().execute(_command(args)).content == expected


@pytest.mark.parametrize(
    "args,error",
    [
        ((), "Usage: /convert"),
        (("10", "m", "km"), "Usage: /convert"),
        (("10", "m", "as", "km"), "Usage: /convert"),
        (("ten", "m", "to", "km"), "finite number"),
        (("nan", "m", "to", "km"), "finite number"),
        (("inf", "m", "to", "km"), "finite number"),
        (("1e309", "m", "to", "km"), "finite number"),
        (("10", "m", "to", "kg"), "same kind"),
        (("10", "m", "to", "unknown"), "Supported units:"),
        (("1e308", "km", "to", "mm"), "too large"),
    ],
)
def test_convert_invalid_inputs(args, error):
    assert error in ConvertCommand().execute(_command(args)).content


@pytest.mark.parametrize(
    "args,expected",
    [
        (
            ("2026-11-22T09:00", "America/New_York", "in", "Europe/London", "Asia/Tokyo"),
            ["2026-11-22T09:00:00-05:00 America/New_York", "2026-11-22T14:00:00+00:00 Europe/London", "2026-11-22T23:00:00+09:00 Asia/Tokyo"],
        ),
        (
            ("2026-07-01T23:30", "America/New_York", "in", "Europe/London"),
            ["2026-07-01T23:30:00-04:00 America/New_York", "2026-07-02T04:30:00+01:00 Europe/London"],
        ),
        (
            ("2026-11-01T06:30", "UTC", "in", "America/New_York"),
            ["2026-11-01T01:30:00-05:00 America/New_York"],
        ),
    ],
)
def test_time_conversion_includes_date_and_offset(args, expected):
    content = TimeCommand().execute(_command(args)).content
    for line in expected:
        assert line in content


@pytest.mark.parametrize(
    "args,error",
    [
        ((), "Usage: /time"),
        (("2026-11-22T09:00", "UTC", "to", "Europe/London"), "Usage: /time"),
        (("09:00", "UTC", "in", "Europe/London"), "ISO date and time"),
        (("2026-11-22T09:00+01:00", "UTC", "in", "Europe/London"), "without a UTC offset"),
        (("2026-11-22T09:00", "Nowhere/Unknown", "in", "UTC"), "Unknown timezone"),
        (("2026-11-22T09:00", "UTC", "in", "Nowhere/Unknown"), "Unknown timezone"),
        (("2026-11-01T01:30", "America/New_York", "in", "UTC"), "ambiguous"),
        (("2026-03-08T02:30", "America/New_York", "in", "UTC"), "does not exist"),
    ],
)
def test_time_rejects_invalid_or_ambiguous_inputs(args, error):
    assert error in TimeCommand().execute(_command(args)).content


def test_time_now_uses_current_instant():
    with patch("csp_bot_commands.time.datetime", wraps=datetime) as clock:
        clock.now.return_value = datetime(2026, 11, 22, 14, 0, tzinfo=UTC)
        content = TimeCommand().execute(_command(("now", "UTC", "in", "Asia/Tokyo"))).content
    assert "2026-11-22T23:00:00+09:00 Asia/Tokyo" in content


@pytest.mark.parametrize("backend", ["slack", "discord", "symphony", "telegram", "matrix", "zulip", "irc"])
@pytest.mark.parametrize(
    "model_name,text,expected",
    [
        ("ChooseCommandModel", '/choose "fish and chips" "fish and chips"', "fish and chips"),
        ("ConvertCommandModel", "/convert 10 mi to km", "10 mi = 16.09344 km"),
        ("TimeCommandModel", "/time 2026-11-22T09:00 America/New_York in Europe/London", "2026-11-22T14:00:00+00:00 Europe/London"),
    ],
)
def test_utilities_load_from_config_parse_and_route(backend, model_name, text, expected):
    bot = Bot(config=BotConfig())
    bot.load_commands([instantiate({"_target_": f"csp_bot_commands.{model_name}"}), HelpCommandModel()])
    with patch.object(Bot, "_get_bot_id", return_value="bot"), patch.object(Bot, "_get_bot_name", return_value="helper"):
        parsed = bot._extract_commands(Message(content=text, author=User(id="user")), backend, "room", text, [])
    assert isinstance(parsed, BotCommand)
    responses = bot._execute_command(parsed)
    assert len(responses) == 1
    response = responses[0]
    assert expected in response.content
    assert response.channel_id == "room"
    assert response.backend == backend
    assert response.metadata["backend"] == backend

    help_command = _command((parsed.command,), backend)
    help_command.command = "help"
    help_text = bot._execute_command(help_command)[0].content
    assert f"/{parsed.command}" in help_text
