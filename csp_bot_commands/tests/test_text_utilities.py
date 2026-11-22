import json
from unittest.mock import patch
from uuid import UUID

import pytest
from chatom import Channel, Message, User
from csp_bot import Bot, BotCommand, BotConfig
from csp_bot.commands import HelpCommandModel
from hydra.utils import instantiate

from csp_bot_commands import CountCommand, EpochCommand, JsonCommand, UuidCommand


def _command(*args):
    return BotCommand.model_validate({"args": args, "backend": "slack", "channel_id": "room", "channel_name": "general", "source": User(id="user")})


@pytest.mark.parametrize(
    "timestamp,iso",
    [
        ("0", "1970-01-01T00:00:00Z"),
        ("1", "1970-01-01T00:00:01Z"),
        ("-1", "1969-12-31T23:59:59Z"),
        ("0.000001", "1970-01-01T00:00:00.000001Z"),
        ("-0.000001", "1969-12-31T23:59:59.999999Z"),
        ("1234567890.123456", "2009-02-13T23:31:30.123456Z"),
        ("-62135596800", "0001-01-01T00:00:00Z"),
        ("253402300799.999999", "9999-12-31T23:59:59.999999Z"),
    ],
)
def test_epoch_round_trip_is_exact_to_microseconds(timestamp, iso):
    command = EpochCommand()
    assert command.execute(_command(timestamp)).content == iso
    assert command.execute(_command(iso)).content == timestamp


@pytest.mark.parametrize("iso", ["1970-01-01T05:30:00+05:30", "1969-12-31T19:00:00-05:00"])
def test_epoch_honors_iso_offset(iso):
    assert EpochCommand().execute(_command(iso)).content == "0"


@pytest.mark.parametrize("value", ["nan", "Infinity", "1e99999", "1e-99999", "0.0000001", "-62135596801", "253402300800", "not-a-date"])
def test_epoch_rejects_invalid_or_unrepresentable_values(value):
    assert "Cannot convert timestamp" in EpochCommand().execute(_command(value)).content


def test_epoch_requires_timezone_on_iso_input():
    assert "requires a UTC offset" in EpochCommand().execute(_command("2026-11-22T09:00:00")).content


def test_uuid_is_version_four_and_canonical():
    result = UuidCommand().execute(_command()).content
    parsed = UUID(result)
    assert parsed.version == 4
    assert str(parsed) == result


@pytest.mark.parametrize("value", [{"message": "hello world", "nested": [True, None, 2]}, [1, 2], "string", 42, True, None])
def test_json_formats_valid_values(value):
    result = JsonCommand().execute(_command(json.dumps(value)))
    assert json.dumps(value, indent=2) in result.content


@pytest.mark.parametrize("text", ['{"key":}', "{'key': 1}", "NaN", "Infinity", '{"bad": 1e9999}', "[] trailing"])
def test_json_rejects_invalid_json(text):
    assert "Invalid JSON" in JsonCommand().execute(_command(text)).content


def test_large_json_is_attached_without_truncation():
    value = {"items": list(range(1000))}
    result = JsonCommand().execute(_command(json.dumps(value)))
    assert result.content == "Formatted JSON attached."
    assert len(result.attachments) == 1
    attachment = result.attachments[0]
    assert attachment.filename == "formatted.json"
    assert attachment.content_type == "application/json"
    assert attachment.data == json.dumps(value, indent=2).encode()


@pytest.mark.parametrize(
    "text,counts",
    [("hello world", (11, 2, 1)), ("hello  world\nnext\tline", (22, 4, 2)), ("café 🐟", (6, 2, 1)), ('"quoted text"', (13, 2, 1))],
)
def test_count_preserves_internal_whitespace_and_unicode(text, counts):
    characters, words, lines = counts
    assert CountCommand().execute(_command(text)).content == f"Characters: {characters}\nWords: {words}\nLines: {lines}"


@pytest.mark.parametrize(
    "command,args", [(EpochCommand, ()), (EpochCommand, ("0", "extra")), (UuidCommand, ("extra",)), (JsonCommand, ()), (CountCommand, ())]
)
def test_missing_or_extra_arguments_show_usage(command, args):
    assert "Usage:" in command().execute(_command(*args)).content


@pytest.mark.parametrize("backend", ["slack", "discord", "symphony", "telegram", "matrix", "zulip", "irc"])
@pytest.mark.parametrize(
    "model,text,expected",
    [
        ("EpochCommandModel", "/epoch 0", "1970-01-01T00:00:00Z"),
        ("EpochCommandModel", "/epoch 1970-01-01T01:00:00+01:00", "0"),
        ("UuidCommandModel", "/uuid", None),
        ("JsonCommandModel", '/json {"key": "value with spaces", "items": [1, 2]}', "value with spaces"),
        ("CountCommandModel", "/count hello  world\nnext\tline", "Characters: 22\nWords: 4\nLines: 2"),
    ],
)
def test_text_utilities_parse_route_and_appear_in_help(backend, model, text, expected):
    bot = Bot(config=BotConfig())
    bot.load_commands([instantiate({"_target_": f"csp_bot_commands.{model}"}), HelpCommandModel()])
    message = Message(content=text, author=User(id="user"), channel=Channel(id="room"))
    with patch.object(Bot, "_get_bot_id", return_value="bot"), patch.object(Bot, "_get_bot_name", return_value="helper"):
        parsed = bot._extract_commands(message, backend, "room", text, [])
    assert isinstance(parsed, BotCommand)
    response = bot._execute_command(parsed)[0]
    if expected is None:
        assert UUID(response.content).version == 4
    else:
        assert expected in response.content
    assert response.channel_id == "room" and response.backend == backend
    assert response.metadata["backend"] == backend
    parsed.args = (parsed.command,)
    parsed.command = "help"
    assert "Syntax:" in bot._execute_command(parsed)[0].content


def test_json_keeps_embedded_directives_and_mentions_as_data():
    bot = Bot(config=BotConfig())
    bot.load_commands([instantiate({"_target_": "csp_bot_commands.JsonCommandModel"})])
    payload = json.dumps({"route": "/room elsewhere", "mention": "@user", "quote": 'a \\"word"'})
    text = f"/json {payload}"
    with (
        patch.object(Bot, "_get_bot_id", return_value="bot"),
        patch.object(Bot, "_get_bot_name", return_value="helper"),
        patch.object(Bot, "_resolve_channel") as resolve,
    ):
        parsed = bot._extract_commands(Message(content=text), "slack", "room", text, [User(id="user")])
    assert parsed.args == (payload,)
    assert parsed.targets == () and parsed.channel_id == "room"
    resolve.assert_not_called()
    assert "Invalid JSON" not in bot._execute_command(parsed)[0].content
