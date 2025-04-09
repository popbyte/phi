import nextcord
from nextcord.ext import commands
from google import genai
from httpx import Client
import json

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="ph!", intents=intents)
settings = json.load(open("settings.json", "r"))
loading_emoji = settings["loading_emoji"]
gemini = genai.Client(api_key=settings["gemini_ai_token"])
httpx = Client()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def chat(ctx: commands.Context):
    message = await ctx.send(loading_emoji)
    
    response = gemini.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[ctx.message.content[8:]]
    )
    response_chunk = ""
    for chunk in response:
        response_chunk += chunk.text
        await message.edit(response_chunk)

@bot.slash_command(description="Chat with Gemini 2.0 Flash")
async def chat(interaction: nextcord.Interaction, message: str):
    message = await interaction.send(loading_emoji)
    
    response = gemini.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[message]
    )
    response_chunk = ""
    for chunk in response:
        response_chunk += chunk.text
        await message.edit(response_chunk)
 
bot.run(settings["bot_token"])
