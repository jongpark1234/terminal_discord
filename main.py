import discord
import sys
import os
from discord.ext import commands
from dpyConsole import Console

from config import APPID, TOKEN

intents = discord.Intents.default()
intents.message_content = True

class DavidChoi(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='JongPark',
            intents=intents,
            sync_command=True,
            application_id=APPID
        )

        self.curGuild = None
        self.curChannel = None

    async def on_ready(self):
        activity = discord.Game('개뻘짓')
        await self.change_presence(status=discord.Status.online, activity=activity)
        print('Bot is ready.')
    
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
           return
        if message.channel.id == self.curChannel:
            printChannelHistory(formatMessage(message))

client = DavidChoi()
console = Console(client)
historyList = []

@console.command()
async def help():
    print(f'''Commands -----
            help - print this message.
                        
            show guilds - Show list that all guilds.            
            show channels - Shows all the channels for a selected guild. {'' if client.curGuild else '( Now Unavailable )'}
            
            select guild [guild id] - select the guild to send message.         
            select channel [channel id] - select the channel to send message.
            
            send [message] - send message to selected channel. {'' if client.curChannel else '( Now Unavailable )'}

            status - print status of now selected guild and channel.
            cls - clear the command screen.

            chat - gets the last 50 messages for current channel.
    ''')
    historyList.append(0)

@console.command()
async def show(target):
    if 'guild' in target or target in 'guild':
        for idx, guild in enumerate(client.guilds):
            print(f'{idx + 1}. {guild.name} ( {guild.id} )')
        historyList.append(1)

    elif 'channel' in target or target in 'channel':
        for idx, channel in enumerate(client.get_guild(client.curGuild).text_channels):
            print(f'{idx + 1}. {channel.name} ( {channel.id} )')
        historyList.append(2)

    else:
        print('Invalid Command.')

@console.command()
async def select(target, target_id):
    target_id = int(target_id)
    if 'guild' in target or target in 'guild':
        guilds = client.guilds

        if target_id in map(lambda x: x.id, guilds): # exact id
            client.curGuild = target_id
            client.curChannel = None
            historyList.append(3)
            print(f'Guild Selected.')
        elif target_id < len(guilds): # index expression
            client.curGuild = guilds[max(0, target_id - 1)].id
            client.curChannel = None
            historyList.append(3)
            print(f'Guild Selected.')
        else:
            print('Guild Not Found.')

    elif 'channel' in target or target in 'channel':
        channels = client.get_guild(client.curGuild).text_channels

        if target_id in channels:
            client.curChannel = target_id # exact id
            historyList.append(4)
            print('Channel Selected.')
        elif target_id < len(channels): # index expression
            client.curChannel = channels[max(0, target_id - 1)].id
            historyList.append(4)
            print('Channel Selected.')
        else:
            print('Channel Not Found.')

    else:
        print('Invalid Command.')

@console.command()
async def send(*message): 
    if client.curChannel:
        message = ' '.join(message)
        channel = client.get_channel(client.curChannel)

        await channel.send(message)
        await printChannelHistory(formatMessage(channel))
        historyList.append(5)

    else:
        print('Channel Do Not Selected.')

@console.command()
async def status():
    print(f'''Status ----
          Selected Guild : {client.get_guild(client.curGuild).name if client.curGuild else '---'} ( {client.curGuild} )
          Selected Channel : {client.get_channel(client.curChannel).name if client.curChannel else '---'} ( {client.curChannel} )
    ''')
    historyList.append(6)

@console.command()
async def cls():
    os.system('cls')
    historyList.append(7)

@console.command()
async def chat():
    if client.curChannel:
        await printChannelHistory(client.get_channel(client.curChannel))
    else:
        print('Select the channel.')






async def printChannelHistory(channel):
    for message in [message async for message in channel.history(limit=50)][::-1]:
        print(formatMessage(message))

def formatMessage(message: discord.Message) -> str:
    return f'ㆍ{message.guild.name} #{message.channel.name} {message.author.name}: {message.content} ( {message.created_at.strftime("%Y/%m/%d %H:%M:%S")} )'
    

if __name__ == '__main__':
    console.start()
    client.run(token=TOKEN)
