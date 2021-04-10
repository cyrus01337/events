import asyncio
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


class EventContext:
    __slots__ = ("_name", "_args", "_kwargs")

    def __init__(self, name, args, kwargs):
        self._name = name
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs


class Listener:
    __slots__ = ("_callback", "checks")

    def __init__(self, callback):
        if isinstance(callback, Listener):
            raise TypeError("coroutine is already a listener")
        elif not asyncio.iscoroutinefunction(callback):
            raise TypeError("listeners must be coroutines")

        self._callback = callback

        try:
            self.checks = self._callback.__listener_checks__
        except AttributeError:
            self.checks = []

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


class EventNamespace:
    __slots__ = ("app", "_event_checks")

    def __init__(self, app: Union[discord.Client, commands.Bot]):
        self.app = app

        self._event_checks = []

    def check(self, check: MaybeCoroutine):
        self._event_checks.append(check)

        return check

    def add_listener(self,
                     function: Union[Coroutine, Listener],
                     *, name: str = None):
        pass

    def listen(self, name: str = None):
        def predicate(function: Union[Coroutine, Listener]):
            nonlocal name

            name = name or function.__name__

            if not isinstance(name, str):
                raise TypeError("name of a listener must be a string")

            events = self.app.extra_events.setdefault(name, [])
            listener = Listener(function)

            events.append(listener)

            return listener
        return predicate

    async def can_event_run(self, event_name, *args, **kwargs):
        if not self._event_checks:
            return True
        event = EventContext(f"on_{event_name}", args, kwargs)

        return await discord.utils.async_all(
            discord.utils.maybe_coroutine(check, event)
            for check in self._event_checks
        )


class Extension:
    __slots__ = (
        "events",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.events = EventNamespace(app=self)

    async def ext_dispatch(self, event, *args, **kwargs):
        if await self.events.can_event_run(event, *args, **kwargs):
            super().dispatch(event, *args, **kwargs)

    def dispatch(self, event, *args, **kwargs):
        self.loop.create_task(self.ext_dispatch(event, *args, **kwargs))


def check(check: MaybeCoroutine):
    def predicate(function: Union[Coroutine, Listener]):
        if asyncio.iscoroutinefunction(function):
            try:
                function.__listener_checks__.append(check)
            except AttributeError:
                function.__listener_checks__ = [check]
        elif isinstance(function, Listener):
            function.checks.append(check)
        return function
    return predicate
