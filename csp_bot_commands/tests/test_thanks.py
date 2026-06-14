import pytest
from csp_bot import BotCommand, User

from csp_bot_commands.thanks import ThanksCommand

cmd = ThanksCommand()


class TestThanks:
    def test_statics(self):
        assert cmd.backends() == []  # All
        assert cmd.command() == "thanks"
        assert cmd.name() == "Thanks"
        assert cmd.help() == "Thank someone. Syntax: /thanks <user> [/channel <channel>]"

    @pytest.mark.parametrize(
        "args,",
        [
            ("cash",),
            ("other",),
        ],
    )
    def test_execute(self, args):
        if isinstance(args, str):
            args = (args,)
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
        msg_text = msg.msg.replace("<@", "@").replace(">", "")
        assert msg_text.startswith("@123 thanks @456 with")
