import logging
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
from random import randint
from time import sleep
from typing import Optional, Type, Union

from csp_bot import BaseCommand, BaseCommandModel, BotCommand, Message, ReplyToOtherCommand

log = logging.getLogger(__name__)

__all__ = (
    "DelayTestCommandModel",
    "DelayTestCommand",
)


def _delay_test():
    """A simple function to imitate performing some background work"""
    sleep(16)
    return randint(0, 100)


class DelayTestCommand(ReplyToOtherCommand):
    def __init__(self, *args, **kwargs):
        self._threadpool = ThreadPool()
        self._resultmap = {}

    def command(self) -> str:
        return "_delaytest"

    def name(self) -> str:
        return ""

    def help(self) -> str:
        return ""

    def preexecute(self, command: BotCommand) -> BotCommand:
        """This isn't actually used, but is designed to test a feature of arbitrarily
        delaying a command to execute in the background"""
        log.critical(f"Testing async bot command: {command}")
        self._resultmap[command.id] = self._threadpool.apply_async(_delay_test)
        # set delay to +5s
        command.delay = datetime.now() + timedelta(seconds=5)
        return command

    def execute(self, command: BotCommand) -> Optional[Union[Message, "DelayTestCommand"]]:
        log.critical(f"Delaytest command: {command}")

        if command.id in self._resultmap:
            # it was a delay test, check if ready
            if self._resultmap[command.id].ready():
                # return the random number as a symphony message
                message = f"Delay test result: {self._resultmap[command.id].get()}"
                self._resultmap.pop(command.id)
                return Message(
                    msg=message,
                    channel=command.channel,
                )
            else:
                # reschedule for +5s
                command.delay = datetime.now() + timedelta(seconds=5)
                msg = Message(
                    msg="All bots are currently assisting other customers, please stay on the line...",
                    channel=command.channel,
                    backend=command.backend,
                )
                return [command, msg]


class DelayTestCommandModel(BaseCommandModel):
    command: Type[BaseCommand] = DelayTestCommand
