import discord
import os
import asyncio

from PIL import ImageGrab
from io import BytesIO
from discord.ext import commands
from dpyConsole import Console

from datetime import timedelta

from config import APPID, TOKEN

ALIGN = '\n'
TAB = '\t'

intents = discord.Intents.default()
intents.message_content = True

class DavidChoi(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='a',
            intents=intents,
            sync_command=True,
            application_id=APPID
        )

        self.curGuild: discord.guild.Guild = None
        self.curChannel: discord.channel.TextChannel = None
        self.isSilent: bool = False
        self.recentMessage: discord.message.Message = None

    async def on_ready(self):
        activity = discord.Game('')
        await self.change_presence(status=discord.Status.online, activity=activity)
        os.system('cls')
        print('Bot is ready.')
    
    async def on_message(self, message: discord.Message) -> None:
        if self.isSilent:
            return
        
        if message.channel == self.curChannel:
            await printChannelHistory(message.channel)
        else:
            print(f'🔔 {message.guild.name} - #{message.channel.name}')
            self.recentMessage = message

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

            chat - gets the last 100 messages for current channel.

            silent - if it is on, clear the terminal immediately when sending a chat.
                                          
            search [name] - Locate the emoji of the searched name.
          
            move - Go to the channel where the alarm went off most recently
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
    if 'guild' in target_name or target_name in 'guild':
        guilds = client.guilds
        if '-' in target_id:
            guild, channel = map(int, target_id.split('-'))
            client.curGuild = guilds[max(0, guild - 1)]
            client.curChannel = client.curGuild.text_channels[max(0, channel - 1)]
            print(f'Guild and Channel Selected. {client.curGuild.name} - #{client.curChannel.name}')
        elif int(target_id) < len(guilds): # index expression
            target_id = int(target_id)
            client.curGuild = guilds[max(0, target_id - 1)]
            client.curChannel = None
            print(f'Guild Selected. {client.curGuild.name}')
        else:
            print('Guild Not Found.')

    elif 'channel' in target_name or target_name in 'channel':
        target_id = int(target_id)
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
    try: 
        if client.curChannel:
            async with client.curChannel.typing():
                await asyncio.sleep(0.5)
            await client.curChannel.send(' '.join(map(lambda x: str(eval(x.replace('[eval]', ''))) if x.startswith('[eval]') else x, message)))
        else:
            print('Channel Do Not Selected.')
    except Exception as e:
        print(e)

@console.command()
async def mention(idx):
    try:
        if client.curChannel:
            try:
                await client.curChannel.send(f'<@{[message async for message in client.curChannel.history()][max(int(idx) - 1, 0)].author.id}>')
            except Exception as e:
                print(e)
                print('Cannot Find Member.')
        else:
            print('Channel Do Not Selected.')
    except Exception as e:
        print(e)

@console.command()
async def reply(idx, *message):
    try:
        await [message async for message in client.curChannel.history()][max(int(idx) - 1, 0)].reply(' '.join(message))
    except Exception as e:
        print(e)

@console.command()
async def react(idx, emoji):
    try:
        await [message async for message in client.curChannel.history()][max(int(idx) - 1, 0)].add_reaction(emoji)
        await printChannelHistory(client.curChannel)
    except Exception as e:
        print(e)

@console.command()
async def sendImage():
    if client.curChannel:
        with BytesIO() as image_binary:
            ImageGrab.grabclipboard().save(image_binary, 'PNG')
            image_binary.seek(0)            
            await client.curChannel.send(file=discord.File(fp=image_binary, filename='image.png'))
    else:
        print('Channel Do Not Selected.')

@console.command()
async def embed(*options):
    try:
        opt = { option.split('=')[0].strip(): option.split('=')[1].strip() for option in options }
        if 'title' not in opt:
            opt['title'] = None
        if 'description' not in opt:
            opt['description'] = None
        if 'url' not in opt:
            opt['url'] = None
        if 'color' not in opt:
            opt['color'] = '#00FF00'

        embed = discord.Embed(title=opt['title'], description=opt['description'], url=opt['url'], color=discord.Color.from_str(opt['color']))
        embed.set_thumbnail(url='https://i.pinimg.com/236x/6e/ca/57/6eca57905edbc43473b909fa2874c9ab.jpg')
        await client.curChannel.send(embed=embed)
    except Exception as e:
        print(e)

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
async def 친():
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
async def execute(*message):
    try:
        exec(' '.join(message))
        print(f'✔️ Command Executed Successfully. ( {" ".join(message)} )')
    except Exception as e:
        print(e)

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

@console.command()
async def move():
    if client.recentMessage:
        client.curChannel = client.recentMessage.channel
        client.recentMessage = None
        await printChannelHistory(client.curChannel)
    else:
        print('Didn\'t get any alarm.')

async def printChannelHistory(channel: discord.channel.TextChannel):
    try:
        for idx, message in reversed(list(enumerate([message async for message in channel.history()]))):
            print(formatMessage(idx, message))
    except Exception as e:
        print(e)

def formatMessage(idx: int, message: discord.Message) -> str:
    return f'{idx + 1} ㆍ{message.guild.name} #{message.channel.name} {message.author.name}: {message.content}{f"<:{message.stickers[0].name}:{message.stickers[0].id}>" if message.stickers else ""} ( {(message.created_at + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")} ) {list(map(lambda x: x.url, message.attachments)) if message.attachments else ""} {ALIGN + TAB + "ㄴ " + ", ".join(map(lambda reaction: (reaction.emoji if type(reaction.emoji) == str else f"<:{reaction.emoji.name}:{reaction.emoji.id}>") + f"x{reaction.count}", message.reactions)) if message.reactions else ""}'
    


if __name__ == '__main__':
    console.start()
    client.run(token=TOKEN)
