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
    - _target_: csp_bot_commands.DelayTestCommandModel
    - _target_: csp_bot_commands.FunCommandModel
    - _target_: csp_bot_commands.MetsCommandModel
    - _target_: csp_bot_commands.ThanksCommandModel
    - _target_: csp_bot_commands.TroutSlapCommandModel
```

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
