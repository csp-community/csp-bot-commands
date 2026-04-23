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
            ("shakespeare",),
            ("yogi",),
            ("tolkien",),
            ("fortune",),
            ("pratchett",),
            ("wilde",),
            ("wine",),
            ("nietzsche",),
            ("twain",),
            ("zen",),
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
        elif args[0] == "shakespeare":
            assert msg.msg.startswith("<@123> hurls a Shakespearean insult at <@456>:")
        elif args[0] == "yogi":
            assert msg.msg.startswith("<@123> shares some Yogi Berra wisdom with <@456>:")
        elif args[0] == "tolkien":
            assert msg.msg.startswith("<@123> offers <@456> wisdom from Middle-earth:")
        elif args[0] == "fortune":
            assert msg.msg.startswith("<@123> cracks open a fortune cookie for <@456>:")
        elif args[0] == "pratchett":
            assert msg.msg.startswith("<@123> enlightens <@456> with Pratchett:")
        elif args[0] == "wilde":
            assert msg.msg.startswith("<@123> graces <@456> with an Oscar Wilde quip:")
        elif args[0] == "wine":
            assert msg.msg.startswith("<@123> calls <@456> over to the")
        elif args[0] == "nietzsche":
            assert msg.msg.startswith("<@123> darkly enlightens <@456> with Nietzsche:")
        elif args[0] == "twain":
            assert msg.msg.startswith("<@123> shares a Mark Twain quip with <@456>:")
        elif args[0] == "zen":
            assert msg.msg.startswith("<@123> offers <@456> a moment of zen:")
        else:
            assert False
