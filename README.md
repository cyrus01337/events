# ABANDONED UNTIL FURTHER NOTICE

# Events
...is an extension that allows the creation of checks on top of existing events and listeners for applications that utilise Discord.py - a library for creating Discord bots in Python. This extension was developed with cog-agnosticism in mind, however, this is intended for bots that sub-class `commands.Bot`.

### Requirements
- Discord.py (v1.7.1)

#### Note
This application was tested on v1.6.0, however, `requirements.txt` will force the installation of v1.7.1 - for those that would like to avoid this, installation through a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) is recommended.

### Usage
```py
from discord.ext import commands, events


class Bot(events.Extension, commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


bot = Bot(command_prefix=">>>")


# applies to all events
@bot.events.check
async def event_check(event):
    if event.name == "on_message":
        message = event.args[0]

        return message.content == "foo"
    return True


@bot.event
async def on_message(message):
    if message.author.display_name.startswith("!"):
        await message.author.edit(nick="don't hoist")


@bot.command()
async def test(ctx):
    await ctx.send("Working!")


bot.run("oogily.boogily.tokus.pocus")
```
