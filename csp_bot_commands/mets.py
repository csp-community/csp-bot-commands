import logging
from typing import Optional, Type

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand

try:
    import lxml  # noqa: F401
    import pandas

    # Required for pandas functions we use
    import tabulate  # noqa: F401
except ModuleNotFoundError:
    pandas = None

__all__ = (
    "get_stats",
    "get_roster",
    "get_schedule",
    "get_standings",
    "MetsCommand",
    "MetsCommandModel",
)
log = logging.getLogger(__name__)


def get_stats():
    dfs = pandas.read_html("https://www.espn.com/mlb/team/stats/_/name/nym/new-york-mets")
    df = pandas.concat(dfs[:2], axis=1)
    return df


def get_roster():
    dfs = pandas.read_html("https://www.espn.com/mlb/team/roster/_/name/nym/new-york-mets")
    df = pandas.concat(dfs)[["Name", "POS", "BAT", "THW", "Age", "HT", "WT"]]
    df["Name"] = df["Name"].str.replace("\\d+", "")
    return df


def get_schedule():
    df = pandas.read_html("https://www.espn.com/mlb/team/schedule/_/name/nym")[0]
    df = df.iloc[1:]
    df.columns = ["Date", "Opponent", "Result", "W-L", "Win", "Loss", "Save", "Att"]
    df = df[df["Date"] != "DATE"]
    return df


def get_standings():
    dfs = pandas.read_html("https://www.espn.com/mlb/standings/_/group/overall")
    teams = dfs[0].columns.tolist() + dfs[0].iloc[:, 0].tolist()
    teams = [n.replace("e --", "") for n in teams]
    team_names = []
    team_acronyms = []
    for team in teams:
        # 2 letter
        for _ in ("TB", "SF", "SD", "KC"):
            if team.startswith(_):
                team_acronyms.append(_)
                team_names.append(team[2:])
                break
        else:
            team_acronyms.append(team[:3])
            team_names.append(team[3:])
    df = dfs[1]
    df["Team"] = team_acronyms
    df["Name"] = team_names
    df = df[
        [
            "Team",
            "Name",
            "W",
            "L",
            "PCT",
            "GB",
            "HOME",
            "AWAY",
            "RS",
            "RA",
            "DIFF",
            "STRK",
            "L10",
        ]
    ]
    return df


class MetsCommand(ReplyToOtherCommand):
    def command(self) -> str:
        return "mets"

    def name(self) -> str:
        return "Mets Information"

    def help(self) -> str:
        return "Information about the Mets. Syntax: /mets [stats roster schedule standings]"

    def execute(self, command: BotCommand) -> Optional[Message]:
        log.info(f"Mets command: {command}")

        try:
            if pandas is None:
                raise ValueError("pandas not installed")
            if "stats" in command.args:
                message = get_stats()
                kind = "Mets Statistics"
            elif "roster" in command.args:
                message = get_roster()
                kind = "Mets Roster"
            elif "schedule" in command.args:
                message = get_schedule()
                kind = "Mets Schedule"
            else:
                message = get_standings()
                kind = "League Standings"

            if command.backend == "symphony":
                message = message.to_html(index=False).replace('border="1"', "")
                message = f'<expandable-card state="collapsed"><header>{kind}</header><body variant="default">{message}</body></expandable-card>'
            elif command.backend == "slack":
                message = f"{kind}\n```\n{message.to_markdown(index=False)}\n```"
            elif command.backend == "discord":
                message = f"{kind}\n```\n{message.to_markdown(index=False)}\n```"
            else:
                raise NotImplementedError(f"Unsupported backend: {command.backend}")

            return Message(
                msg=message,
                channel=command.channel,
                backend=command.backend,
            )
        except ValueError:
            # error pulling tables
            log.exception("Error pulling Mets data")
            message = "Mets data unavailable right now!"
            if pandas is None:
                message += " (pandas not installed)"
            return Message(
                msg=message,
                channel=command.channel,
                backend=command.backend,
            )


class MetsCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = MetsCommand
