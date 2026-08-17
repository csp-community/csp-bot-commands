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
            ("stoic",),
            ("churchill",),
            ("confucius",),
            ("starwars",),
            ("hitch",),
            ("hemingway",),
            ("dad",),
            ("chuck",),
            ("soviet",),
            ("conspiracy",),
            ("magic8",),
            ("compliment",),
            ("latin",),
            ("pirate",),
            ("corporate",),
            ("motivational",),
            ("haiku",),
            ("programming",),
            ("whiskey",),
            ("highfive",),
        ],
    )
    def test_execute(self, args):
        if isinstance(args, str):
            args = (args,)
        msg = cmd.execute(
            BotCommand(
                backend="slack",
                channel_id="test_channel",
                channel_name="test_channel",
                source=User(
                    id="123",
                ),
                targets=(User(id="456"),),
                args=args,
            )
        )
        assert msg is not None
        assert msg.backend == "slack"
        assert msg.channel_id == "test_channel"

        if args[0] == "icelandic":
            assert msg.content.startswith("<@123> consoles <@456> with an Icelandic folk saying:")
        elif args[0] == "german":
            assert msg.content.startswith("<@123> teaches <@456> some German:")
        elif args[0] in ("cocktail", "beer"):
            assert msg.content.startswith("<@123> calls <@456> over to the")
        elif args[0] == "dune":
            assert msg.content.startswith("<@123> scrapes wisdom for <@456> off the sands of Arrakis:")
        elif args[0] == "bush":
            assert msg.content.startswith("<@123> impresses <@456> with a quote from George W. Bush:")
        elif args[0] == "shakespeare":
            assert msg.content.startswith("<@123> hurls a Shakespearean insult at <@456>:")
        elif args[0] == "yogi":
            assert msg.content.startswith("<@123> shares some Yogi Berra wisdom with <@456>:")
        elif args[0] == "tolkien":
            assert msg.content.startswith("<@123> offers <@456> wisdom from Middle-earth:")
        elif args[0] == "fortune":
            assert msg.content.startswith("<@123> cracks open a fortune cookie for <@456>:")
        elif args[0] == "pratchett":
            assert msg.content.startswith("<@123> enlightens <@456> with Pratchett:")
        elif args[0] == "wilde":
            assert msg.content.startswith("<@123> graces <@456> with an Oscar Wilde quip:")
        elif args[0] == "wine":
            assert msg.content.startswith("<@123> calls <@456> over to the")
        elif args[0] == "nietzsche":
            assert msg.content.startswith("<@123> darkly enlightens <@456> with Nietzsche:")
        elif args[0] == "twain":
            assert msg.content.startswith("<@123> shares a Mark Twain quip with <@456>:")
        elif args[0] == "zen":
            assert msg.content.startswith("<@123> offers <@456> a moment of zen:")
        elif args[0] == "stoic":
            assert msg.content.startswith("<@123> offers <@456> some Stoic counsel:")
        elif args[0] == "churchill":
            assert msg.content.startswith("<@123> channels Churchill for <@456>:")
        elif args[0] == "confucius":
            assert msg.content.startswith("<@123> shares ancient wisdom with <@456>:")
        elif args[0] == "starwars":
            assert msg.content.startswith("<@123> reaches for the Force on behalf of <@456>:")
        elif args[0] == "hitch":
            assert msg.content.startswith("<@123> consults the Guide for <@456>:")
        elif args[0] == "hemingway":
            assert msg.content.startswith("<@123> pours a drink and quotes Hemingway for <@456>:")
        elif args[0] == "dad":
            assert msg.content.startswith("<@123> subjects <@456> to a dad joke:")
        elif args[0] == "chuck":
            assert msg.content.startswith("<@123> informs <@456> of a Chuck Norris fact:")
        elif args[0] == "soviet":
            assert msg.content.startswith("<@123> reminds <@456>:")
        elif args[0] == "conspiracy":
            assert msg.content.startswith("<@123> whispers to <@456>:")
        elif args[0] == "magic8":
            assert msg.content.startswith("<@123> shakes the Magic 8-Ball for <@456>:")
        elif args[0] == "compliment":
            assert msg.content.startswith("<@123> lavishes praise on <@456>:")
        elif args[0] == "latin":
            assert msg.content.startswith("<@123> schools <@456> in Latin:")
        elif args[0] == "pirate":
            assert msg.content.startswith("<@123> makes <@456> walk the plank:")
        elif args[0] == "corporate":
            assert msg.content.startswith("<@123> synergizes with <@456>:")
        elif args[0] == "motivational":
            assert msg.content.startswith("<@123> puts a poster on <@456>")
        elif args[0] == "haiku":
            assert msg.content.startswith("<@123> composes a haiku for <@456>:")
        elif args[0] == "programming":
            assert msg.content.startswith("<@123> shares a programming joke with <@456>:")
        elif args[0] == "whiskey":
            assert msg.content.startswith("<@123> calls <@456> over to the")
        elif args[0] == "highfive":
            assert msg.content.startswith("<@123> gives <@456> a magnificent")
        else:
            assert False
