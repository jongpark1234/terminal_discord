import discord
import sys
import os
from typing import Union
from discord.ext import commands
from dpyConsole import Console

from datetime import timedelta

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

        self.curGuild: discord.guild.Guild = None
        self.curChannel: discord.channel.TextChannel = None
        self.isSilent: bool = False

    async def on_ready(self):
        activity = discord.Game('')
        await self.change_presence(status=discord.Status.online, activity=activity)
        os.system('cls')
        print('Bot is ready.')
    
    async def on_message(self, message: discord.Message) -> None:
        if message.channel.id == self.curChannel.id:
            await printChannelHistory(message.channel)

client = DavidChoi()
console = Console(client)

@console.command()
async def help():
    print(f'''Commands -----
            help - print this message.
                        
            show guilds - Show list that all guilds.            
            show channels - Shows all the channels for a selected guild.
            
            select guild [guild id] - select the guild to send message.         
            select channel [channel id] - select the channel to send message.
            
            send [message] - send message to selected channel.

            status - print status of now selected guild and channel.
            cls - clear the command screen.

            chat - gets the last 50 messages for current channel.

            silent - if it is on, clear the terminal immediately when sending a chat.

            search [name] - Locate the emoji of the searched name.
    ''')

@console.command()
async def show(target_name):
    if 'guild' in target_name or target_name in 'guild':
        for idx, guild in enumerate(client.guilds):
            print(f'{idx + 1}. {guild.name} ( {guild.id} )')

    elif 'channel' in target_name or target_name in 'channel':
        for idx, channel in enumerate(client.curGuild.text_channels):
            print(f'{idx + 1}. {channel.name} ( {channel.id} )')

    else:
        print('Invalid Command.')

@console.command()
async def select(target_name, target_id):
    target_id = int(target_id)
    if 'guild' in target_name or target_name in 'guild':
        guilds = client.guilds
        if target_id < len(guilds): # index expression
            client.curGuild = guilds[max(0, target_id - 1)]
            client.curChannel = None
            print(f'Guild Selected. {client.curGuild.name}')
        else:
            print('Guild Not Found.')

    elif 'channel' in target_name or target_name in 'channel':
        channels = client.curGuild.text_channels
        if target_id < len(channels): # index expression
            client.curChannel = channels[max(0, target_id - 1)]
            print(f'Channel Selected. {client.curChannel.name}')
        else:
            print('Channel Not Found.')

    else:
        print('Invalid Command.')

@console.command()
async def send(*message): 
    if client.curChannel:
        await client.curChannel.send(' '.join(message))
    else:
        print('Channel Do Not Selected.')

@console.command()
async def status():
    print(f'''Status ----
          Selected Guild : {client.curGuild.name if client.curGuild else '---'}
          Selected Channel : {client.curChannel.name if client.curChannel else '---'}
    ''')

@console.command()
async def cls():
    os.system('cls')

@console.command()
async def chat():
    if client.curChannel:
        await printChannelHistory(client.curChannel)
    else:
        print('Select the channel.')

@console.command()
async def silent():
    client.isSilent = not client.isSilent
    print(f'Silent Mode = {client.isSilent}')

@console.command()
async def search(name):
    try:
        if len(name) < 2:
            print('Please enter at least two letters.')
            return
        
        emoji_dict = { x.name.lower(): f'<:{x.name}:{x.id}>' for x in client.emojis }
        filtered_emoji_list = list(filter(lambda x: name in x, emoji_dict.keys()))

        if len(filtered_emoji_list) == 0:
            print('No search results found.')
            return

        for emoji in filtered_emoji_list:
            print(emoji_dict[emoji])
    except Exception as e:
        print(e)

async def printChannelHistory(channel):
    for message in [message async for message in channel.history(limit=50)][::-1]:
        print(formatMessage(message))

def formatMessage(message: discord.Message) -> str:
    return f'ㆍ{message.guild.name} #{message.channel.name} {message.author.name}: {message.content} ( {(message.created_at + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")} ) {list(map(lambda x: x.url, message.attachments)) if message.attachments else ""} {message.stickers}'
    

if __name__ == '__main__':
    console.start()
    client.run(token=TOKEN)
