# csp bot commands

Miscellaneous commands for [csp-bot](http://github.com/Point72/csp-bot/)

[![Build Status](https://github.com/csp-community/csp-bot-commands/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/csp-community/csp-bot-commands/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/csp-community/csp-bot-commands/branch/main/graph/badge.svg)](https://codecov.io/gh/csp-community/csp-bot-commands)
[![License](https://img.shields.io/github/license/csp-community/csp-bot-commands)](https://github.com/csp-community/csp-bot-commands)
[![PyPI](https://img.shields.io/pypi/v/csp-bot-commands.svg)](https://pypi.python.org/pypi/csp-bot-commands)

## Overview

This package contains fun, testing, and utility commands for [csp-bot](http://github.com/Point72/csp-bot/).

| Command      | Type      | Description                                                                                          |
| :----------- | :-------- | :--------------------------------------------------------------------------------------------------- |
| `/slap`      | `fun`     | Slap someone with a [wet trout](https://en.wikipedia.org/wiki/Wikipedia:Whacking_with_a_wet_trout)   |
| `/mets`      | `utility` | Get information about the NY Mets baseball team, including roster, players, and schedule information |
| `/thanks`    | `fun`     | Thank another user with a random object or cash                                                      |
| `/_fun`      | `fun`     | Randomly generated/selected quotes or trivia                                                         |
| `/delaytest` | `test`    | Tester command for delayed/repeated commands                                                         |
| `/choose`    | `utility` | Pick one supplied option at random                                                                   |
| `/convert`   | `utility` | Convert common units of length, mass, volume, duration, and temperature                              |
| `/time`      | `utility` | Convert a date and time between timezones                                                            |
| `/epoch`     | `utility` | Convert Unix seconds to an ISO datetime and back                                                     |
| `/uuid`      | `utility` | Generate a random version 4 UUID                                                                     |
| `/json`      | `utility` | Validate and pretty-print JSON                                                                       |
| `/count`     | `utility` | Count characters, words, and lines                                                                   |

Any of these commands can be included in a `csp-bot` configuration [following the documentation](https://github.com/Point72/csp-bot/wiki/Overview#writing-commands):

```yaml
# @package _global_
defaults:
  - /gateway: slack
  - _self_

bot_name: CSP Bot
app_token: .slack_app_token
bot_token: .slack_bot_token

gateway:
  _target_: csp_bot.Gateway
  modules:
    - /modules/bot
  commands:
    - /commands/help
    - _target_: csp_bot_commands.ChooseCommandModel
    - _target_: csp_bot_commands.ConvertCommandModel
    - _target_: csp_bot_commands.CountCommandModel
    - _target_: csp_bot_commands.DelayTestCommandModel
    - _target_: csp_bot_commands.EpochCommandModel
    - _target_: csp_bot_commands.FunCommandModel
    - _target_: csp_bot_commands.JsonCommandModel
    - _target_: csp_bot_commands.MetsCommandModel
    - _target_: csp_bot_commands.ThanksCommandModel
    - _target_: csp_bot_commands.TimeCommandModel
    - _target_: csp_bot_commands.TroutSlapCommandModel
    - _target_: csp_bot_commands.UuidCommandModel
```

## Utility commands

These commands use Python's standard library. They require no API keys, network
services, or agent extra.

### `/choose`

`/choose <option> <option> [<option> ...]` returns one randomly selected option.
At least two nonempty options are required. Double quotes group an option
containing spaces:

```text
/choose pizza "fish and chips" sushi
```

### `/convert`

`/convert <value> <unit> to <unit>` converts between units of the same quantity.
Unit names are case-insensitive. Results show up to ten significant digits.

| Quantity    | Units                                         |
| ----------- | --------------------------------------------- |
| Length      | `mm`, `cm`, `m`, `km`, `in`, `ft`, `yd`, `mi` |
| Mass        | `mg`, `g`, `kg`, `oz`, `lb`                   |
| Volume      | `ml`, `l`                                     |
| Duration    | `ms`, `s`, `min`, `h`, `day`                  |
| Temperature | `c`, `f`, `k`                                 |

`oz` means mass ounces. A `day` is 24 hours. Nonfinite numbers, unknown units,
incompatible quantities, and results outside the numeric range return an error.

```text
/convert 10 mi to km
/convert 32 F to C
/convert 90 min to h
```

### `/time`

`/time <YYYY-MM-DDTHH:MM|now> <source-zone> in <target-zone> [<target-zone> ...]`
shows the source and target times with dates and UTC offsets. Timezones use IANA
names such as `America/New_York`, `Europe/London`, and `Asia/Tokyo`; `UTC` is also
accepted. `now` uses the current instant.

Explicit times are local to the source timezone, without an offset in the
input. Times skipped or repeated by a daylight saving transition return an error;
UTC input identifies an instant when a local time is ambiguous.

```text
/time 2026-11-22T09:00 America/New_York in Europe/London Asia/Tokyo
/time now UTC in America/New_York
```

### `/epoch`

`/epoch <unix-seconds|ISO-datetime>` converts in either direction. Unix timestamps
are seconds since 1970-01-01T00:00:00Z, including negative and fractional values.
Output datetimes use UTC with a `Z` suffix. ISO input requires an explicit offset;
host-local time is never inferred. Conversion supports microsecond precision and
datetime years 1-9999. Timestamp values beyond that range or precision return an
error.

```text
/epoch 0
/epoch 1234567890.123456
/epoch 1970-01-01T05:30:00+05:30
```

The first and last examples return `1970-01-01T00:00:00Z` and `0`, respectively.

### `/uuid`

`/uuid` generates one random version 4 UUID in the standard hyphenated format.
It accepts no arguments.

### `/json`

`/json <JSON>` validates JSON and formats it with two-space indentation. JSON is
pasted directly after the command; quotes, internal whitespace, and embedded
`/room` or mention text are preserved as data. Objects, arrays, and scalar JSON
values are accepted. Invalid JSON and nonfinite numbers return an error.

```text
/json {"message": "hello world", "items": [1, 2, 3]}
```

Formatted output up to 1,500 characters appears in a code block. Larger output
is attached as `formatted.json`, using the backend's file-upload support.

### `/count`

`/count <text>` reports Unicode code points, whitespace-separated words, and
lines. Quotes are literal text. Internal whitespace and line breaks are
preserved; whitespace surrounding the command payload is trimmed by the bot.

```text
/count hello  world
```

This example reports 12 characters, two words, and one line. `/json` and `/count`
require `csp-bot` support for the command class's `raw_args` option.

## Agent commands and MCP

Install `csp-bot-commands[agent]` to enable `/ask` and `/summarize`. Both command
models accept `model_name` and optional `mcp_servers` alongside the local chat
tools:

```yaml
_target_: csp_bot_commands.AskCommandModel
model_name: "anthropic:<model>"
mcp_servers:
  - url: https://tools.example.com/mcp
    prefix: knowledge
    headers_env:
      Authorization: KNOWLEDGE_MCP_AUTH
    tools: [search]
    timeout: 60
```

Use `SummarizeCommandModel` for the same configuration on `/summarize`; it still
requires a connected chat backend to read channel history. Omit `mcp_servers` to
use only the local tools.

URLs must use HTTPS. `headers_env` maps HTTP headers to environment variables;
each variable contains the full header value, including `Bearer ` when required.
`tools` restricts the server tools exposed to the agent, and `prefix` distinguishes
tools from different servers. Remote servers enforce their own authorization;
local chat access policies do not apply to external tools.

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
