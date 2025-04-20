import pytest
from csp_bot import BotCommand, User

from csp_bot_commands.trout import TroutSlapCommand

cmd = TroutSlapCommand()


class TestTroutSlap:
    def test_statics(self):
        assert cmd.backends() == []  # All
        assert cmd.command() == "slap"
        assert cmd.name() == "Slap"
        assert cmd.help() == "Slap someone with a wet fish. Syntax: /slap <user> [/channel <channel>]"

    @pytest.mark.parametrize(
        "args,",
        [
            ("random",),
            ("trout",),
        ],
    )
    def test_execute(self, args):
        msg = cmd.execute(
            BotCommand(
                backend="slack",
                channel="test_channel",
                source=User(
                    id="123",
                ),
                targets=(User(id="456"),),
                args=args,
            )
        )
        assert msg is not None
        assert msg.backend == "slack"
        assert msg.channel == "test_channel"
        assert msg.msg.startswith("<@123> slaps <@456> with")
        if args[0] == "trout":
            assert "trout" in msg.msg
