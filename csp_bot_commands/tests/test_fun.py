import pytest
from csp_bot import BotCommand, User

from csp_bot_commands.fun import FunCommand

cmd = FunCommand()


class TestFun:
    def test_statics(self):
        assert cmd.backends() == []  # All
        assert cmd.command() == "_fun"

        # hidden
        assert cmd.name() == ""
        assert cmd.help() == ""

    @pytest.mark.parametrize(
        "args,",
        [
            ("icelandic",),
            ("german",),
            ("cocktail",),
            ("beer",),
            ("dune",),
            ("bush",),
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

        if args[0] == "icelandic":
            assert msg.msg.startswith("<@123> consoles <@456> with an Icelandic folk saying:")
        elif args[0] == "german":
            assert msg.msg.startswith("<@123> teaches <@456> some German:")
        elif args[0] == "cocktail":
            assert msg.msg.startswith("<@123> calls <@456> over to the")
        elif args[0] == "beer":
            assert msg.msg.startswith("<@123> calls <@456> over to the")
        elif args[0] == "dune":
            assert msg.msg.startswith("<@123> scrapes wisdom for <@456> off the sands of Arrakis:")
        elif args[0] == "bush":
            assert msg.msg.startswith("<@123> impresses <@456> with a quote from George W. Bush:")
        else:
            assert False
