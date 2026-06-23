import logging
from html import escape

from chatom import DISCORD_CAPABILITIES, SLACK_CAPABILITIES, TELEGRAM_CAPABILITIES
from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand

log = logging.getLogger(__name__)

try:
    import pandas
except ModuleNotFoundError:
    pandas = None
    log.warning("pandas is not installed, `/mets` commands will not function properly.")

for _optional_dependency in ("html5lib", "lxml", "tabulate"):
    try:
        __import__(_optional_dependency)
    except ModuleNotFoundError:
        log.warning("%s is not installed, `/mets` commands may not function properly.", _optional_dependency)

__all__ = (
    "MetsCommand",
    "MetsCommandModel",
    "get_roster",
    "get_schedule",
    "get_standings",
    "get_stats",
)


def _chunk_lines(lines: list[str], prefix: str, suffix: str, limit: int, line_len=len, format_chunk=lambda chunk: chunk) -> list[str]:
    lines = list(lines)
    available = limit - len(prefix) - len(suffix)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    if not lines:
        return [f"{prefix}{suffix}"]

    for line in lines:
        safe_line = line if line_len(line) <= available else line[: max(0, available - 3)] + "..."
        additional_len = line_len(safe_line) + (1 if current else 0)
        if current and current_len + additional_len > available:
            chunks.append("\n".join(current))
            current = [safe_line]
            current_len = line_len(safe_line)
        else:
            current.append(safe_line)
            current_len += additional_len

    if current:
        chunks.append("\n".join(current))

    return [f"{prefix}{format_chunk(chunk)}{suffix}" for chunk in chunks]


def _plain_table_messages(kind: str, table: str, limit: int) -> list[str]:
    return _chunk_lines(table.splitlines(), f"{kind}\n```\n", "\n```", limit)


def _telegram_table_messages(kind: str, table: str) -> list[str]:
    prefix = f"<b>{escape(kind, quote=False)}</b>\n<pre>"
    suffix = "</pre>"
    return _chunk_lines(
        table.splitlines(),
        prefix,
        suffix,
        TELEGRAM_CAPABILITIES.max_message_length,
        line_len=lambda line: len(escape(line, quote=False)),
        format_chunk=lambda chunk: escape(chunk, quote=False),
    )


def _response_messages(command: BotCommand, contents: list[str]) -> Message | list[Message]:
    messages = [
        Message(
            content=content,
            channel=command.channel,
            backend=command.backend,
        )
        for content in contents
    ]
    return messages[0] if len(messages) == 1 else messages


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

    def execute(self, command: BotCommand) -> Message | list[Message] | None:
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
                return Message(
                    content=message,
                    channel=command.channel,
                    backend=command.backend,
                )
            table = message.to_markdown(index=False, tablefmt="plain")
            if command.backend == "slack":
                messages = _plain_table_messages(kind, table, SLACK_CAPABILITIES.max_message_length)
            elif command.backend == "discord":
                messages = _plain_table_messages(kind, table, DISCORD_CAPABILITIES.max_message_length)
            elif command.backend == "telegram":
                messages = _telegram_table_messages(kind, table)
            else:
                raise NotImplementedError(f"Unsupported backend: {command.backend}")

            return _response_messages(command, messages)
        except ValueError:
            # error pulling tables
            log.exception("Error pulling Mets data")
            message = "Mets data unavailable right now!"
            if pandas is None:
                message += " (pandas not installed)"
            return Message(
                content=message,
                channel=command.channel,
                backend=command.backend,
            )


class MetsCommandModel(BaseCommandModel):
    command: type[BaseCommand] = MetsCommand
