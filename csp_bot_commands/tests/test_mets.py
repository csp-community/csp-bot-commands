from unittest.mock import patch

import pandas as pd
import pytest
from csp_bot import BotCommand, User

from csp_bot_commands.mets import MetsCommand, get_roster, get_schedule, get_standings, get_stats

cmd = MetsCommand()


class TestMets:
    def test_statics(self):
        assert cmd.backends() == []  # All
        assert cmd.command() == "mets"
        assert cmd.name() == "Mets Information"
        assert cmd.help() == "Information about the Mets. Syntax: /mets [stats roster schedule standings]"

    def test_data_fetch(self):
        assert get_roster() is not None
        assert get_schedule() is not None
        assert get_standings() is not None
        assert get_stats() is not None

    @pytest.mark.parametrize(
        "args,backend",
        [
            (("stats",), "discord"),
            (("stats",), "slack"),
            (("stats",), "symphony"),
            (("roster",), "discord"),
            (("roster",), "slack"),
            (("roster",), "symphony"),
            (("schedule",), "discord"),
            (("schedule",), "slack"),
            (("schedule",), "symphony"),
            (("standings",), "discord"),
            (("standings",), "slack"),
            (("standings",), "symphony"),
        ],
    )
    def test_execute(self, args, backend):
        print(args)
        with patch("csp_bot_commands.mets.pandas") as mock_pandas:
            if args[0] == "stats":
                mock_pandas.read_html.return_value = [
                    pd.DataFrame([{"Name": "Francisco Lindor SS"}]),
                    pd.DataFrame(
                        [
                            {
                                "GP": 21,
                                "AB": 85,
                                "R": 14,
                                "H": 23,
                                "2B": 4,
                                "3B": 0,
                                "HR": 3,
                                "RBI": 9,
                                "TB": 36,
                                "BB": 6,
                                "SO": 15,
                                "SB": 2,
                                "AVG": 0.271,
                                "OBP": 0.323,
                                "SLG": 0.424,
                                "OPS": 0.746,
                                "WAR": 0.1,
                            }
                        ]
                    ),
                ]
            elif args[0] == "roster":
                mock_pandas.read_html.return_value = [
                    pd.DataFrame(
                        [
                            {
                                "Unnamed: 0": 0,
                                "Name": "Edwin Diaz39",
                                "POS": "RP",
                                "BAT": "R",
                                "THW": "R",
                                "Age": 31,
                                "HT": "6' 3\"",
                                "WT": "165 lbs",
                                "Birth Place": "Naguabo, Puerto Rico",
                            }
                        ]
                    ),
                ]
            elif args[0] == "schedule":
                mock_pandas.read_html.return_value = [
                    pd.DataFrame(
                        [
                            {
                                0: "Sun, Jul 13",
                                1: "@ Kansas City",
                                2: "2:10 PM",
                                3: 0,
                                4: 0,
                                5: 0,
                                6: "Tickets as low as $11",
                                7: "Tickets as low as $11",
                            }
                        ]
                    )
                ]
            elif args[0] == "standings":
                mock_pandas.read_html.return_value = [
                    pd.DataFrame([{"SDSan Diego Padres": "NYMNew York Mets"}]),
                    pd.DataFrame(
                        [
                            {
                                "W": 3,
                                "L": 16,
                                "PCT": 0.158,
                                "GB": "11",
                                "HOME": "2-5",
                                "AWAY": "1-11",
                                "RS": 63,
                                "RA": 115,
                                "DIFF": -52,
                                "STRK": "L7",
                                "L10": "1-9",
                            },
                            {
                                "W": 7,
                                "L": 15,
                                "PCT": 0.318,
                                "GB": "8.5",
                                "HOME": "4-5",
                                "AWAY": "3-10",
                                "RS": 75,
                                "RA": 95,
                                "DIFF": -20,
                                "STRK": "L3",
                                "L10": "3-7",
                            },
                        ]
                    ),
                ]
            else:
                mock_pandas.read_html.return_value = [pd.DataFrame()]

            msg = cmd.execute(
                BotCommand(
                    backend=backend,
                    channel="test_channel",
                    source=User(
                        id="123",
                    ),
                    targets=(User(id="456"),),
                    args=args,
                )
            )
            assert msg is not None
            assert msg.backend == backend
            assert msg.channel == "test_channel"
            if args[0] == "stats":
                assert "Mets Statistics" in msg.msg
            elif args[0] == "roster":
                assert "Mets Roster" in msg.msg
            elif args[0] == "schedule":
                assert "Mets Schedule" in msg.msg
            elif args[0] == "standings":
                assert "League Standings" in msg.msg
