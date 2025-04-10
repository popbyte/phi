import nextcord
from nextcord.ext import commands
from google import genai
from google.genai import types
import json

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="ph!", intents=intents)
settings = json.load(open("settings.json", "r"))
loading_emoji = settings["loading_emoji"] or "\N{ZERO WIDTH NON-JOINER}"
gemini = genai.Client(api_key=settings["gemini_ai_token"]).aio
gemini_config = types.GenerateContentConfig(
    tools=[
        types.Tool(
        google_search = types.GoogleSearch()
        )
    ],
    response_modalities=["TEXT"],
    temperature = settings.get("temperature", 0.5),
    topP = settings.get("topP", 1),
    topK = settings.get("topK", 0),
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def chat(ctx: commands.Context):
    message = await ctx.send(loading_emoji)
    
    response = await gemini.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[ctx.message.content[8:]],
        config=gemini_config
    )

    response_chunk = ""
    async for chunk in response:
        response_chunk += chunk.text
        response_len = len(response_chunk)
        if response_len > 2000:
            response_chunk = response_chunk[response_len - 2000:]
            message = await ctx.send(response_chunk)
            continue
        await message.edit(response_chunk)

@bot.slash_command(description="Chat with Gemini 2.0 Flash")
async def chat(interaction: nextcord.Interaction, message: str):
    bot_message = await interaction.send(loading_emoji)
    
    response = await gemini.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[message],
        config=gemini_config
    )
    response_chunk = ""
    async for chunk in response:
        response_chunk += chunk.text
        response_len = len(response_chunk)
        if response_len > 2000:
            response_chunk = response_chunk[response_len - 2000:]
            bot_message = await interaction.send(response_chunk)
            continue
        await bot_message.edit(response_chunk)
 
bot.run(settings["bot_token"])
