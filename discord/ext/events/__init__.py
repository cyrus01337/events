import asyncio
from collections import namedtuple
from typing import Callable, Coroutine, Union

import discord
from discord.ext import commands


__title__ = "discord.ext.events"
__author__ = "cyrus01337"
__license__ = "Unlicense"
__version__ = "1.0a"
__all__ = (
    "MaybeCoroutine"
)

MaybeCoroutine = Union[Callable, Coroutine]
EventInfo = namedtuple("EventInfo", "name args kwargs")


class Listener:
    __slots__ = ("_callback", "checks")

    def __init__(self, callback):
        if isinstance(callback, Listener):
            raise TypeError("coroutine is already a listener")
        elif not asyncio.iscoroutinefunction(callback):
            raise TypeError("listeners must be coroutines")

        self._callback = callback
        self.checks = getattr(callback, "__listener_checks__", [])

    async def __call__(self, *args, **kwargs):
        if await self.can_run(*args, **kwargs):
            return await self.callback(*args, **kwargs)

    @property
    def __name__(self):
        return self._callback.__name__

    @property
    def callback(self):
        return self._callback

    async def can_run(self, *args, **kwargs):
        print(self.__name__, self.checks)

        if self.checks:
            return await discord.utils.async_all(
                discord.utils.maybe_coroutine(check, *args, **kwargs)
                for check in self.checks
            )
        return True


class Extension:
    __slots__ = (
        "_event_checks",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._event_checks = []

    def check(self, check: MaybeCoroutine):
        """
        Add a global check that acts as a pre-dispatch hook for events
        """
        self._event_checks.append(check)

        return check

    def add_listener(self,
                     function: Union[Coroutine, Listener],
                     *, name: str = None):
        pass

    def listen(self, name: str = None):
        """

        """

        def predicate(function: Union[Coroutine, Listener]):
            nonlocal name

            name = name or function.__name__

            if not isinstance(name, str):
                raise TypeError("name of a listener must be a string")

            events = self.extra_events.setdefault(name, [])
            listener = Listener(function)

            events.append(listener)

            return listener
        return predicate

    async def can_event_run(self, event, *args, **kwargs):
        if not self._event_checks:
            return True
        info = EventInfo(f"on_{event}", args, kwargs)

        return await discord.utils.async_all(
            discord.utils.maybe_coroutine(check, info)
            for check in self._event_checks
        )

    async def ext_dispatch(self, event, *args, **kwargs):
        if await self.events.can_event_run(event, *args, **kwargs):
            super().dispatch(event, *args, **kwargs)

    def dispatch(self, event, *args, **kwargs):
        self.loop.create_task(self.ext_dispatch(event, *args, **kwargs))


def extend(bot: commands.Bot):
    Extension.__init__(bot)


def check(check: MaybeCoroutine):
    def predicate(function: Union[Coroutine, Listener]):
        if asyncio.iscoroutinefunction(function):
            if not hasattr(function, "__listener_checks__"):
                function.__listener_checks__ = []
            function.__listener_checks__.append(check)
        elif isinstance(function, Listener):
            function.checks.append(check)
        return function
    return predicate
