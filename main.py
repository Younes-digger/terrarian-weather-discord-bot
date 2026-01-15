import discord
from discord.ext import commands
from discord import app_commands
import sys,requests
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
api_key = os.getenv("API_KEY")

if not token:
    raise RuntimeError("DISCORD_TOKEN not found in .env")


handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["/","!"], intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has gone online')



def fetch_weather(city_name):
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["cod"]==200:
            temp_k = data["main"]["temp"]
            temp_c = int(temp_k - 273)
            icon = data["weather"][0]["icon"]
            description = data["weather"][0]["description"]
            icon_map = {
                "01d": "☀️", "01n": "🌕",
                "02d": "🌤️", "02n": "🌤️",
                "03d": "☁️", "03n": "☁️",
                "04d": "🌥️", "04n": "🌥️",
                "09d": "🌧️", "09n": "🌧️",
                "10d": "🌦️", "10n": "🌧️",
                "11d": "⛈️", "11n": "⛈️",
                "13d": "🌨️", "13n": "🌨️",
                "50d": "🌫️", "50n": "🌫️",
            }
            emoji = icon_map.get(icon, "❓")
        return {
         "temperature": temp_c,
         "emoji": emoji,
         "description": description
      }


    except requests.exceptions.HTTPError as httperror:
            match response.status_code:
                case 400:
                    return "Bad Requests\nPlease check your input❌"
                case 401:
                    return "Unauthorized\nInvalid API key❌"
                case 403:
                    return "Forbidden\nAccess ia denied❌"
                case 404:
                    return "Not Found\nCity not found❌"
                case 500:
                    return "Internal Server Error\nPlease try again later❌"
                case 502:
                    return "Bad Getway\nInvalid response from the server❌"
                case 503:
                    return "Server Unavailable\nServer is down❌"
                case 504:
                    return "Getaway Timeout\nNo response from the server❌"
                case _:
                    return f"HTTPErorr has occurred \n{httperror}❌"

    except requests.exceptions.ConnectionError:
            return "Connection Error\nCheck your internet connection❌"

    except requests.exceptions.TooManyRedirects:
            return "Too Many Redirects\nCheck your URL❌"

    except requests.exceptions.Timeout:
            return "Timeout Error\nThe request timed out❌"

    except requests.exceptions.RequestException as re_error:
            return f"Request Error\n{re_error}❌"
    
@bot.command()
async def weather(ctx, *, city):
    info = fetch_weather(city)
    embed = discord.Embed()
    if isinstance(info, dict):
        embed.title = f"Weather in {city.title()} {info['emoji']}"
        embed.add_field(name="Temperature", value=f"{info['temperature']}°C", inline=False)
        embed.add_field(name="Condition", value=f"{info['description'].capitalize()} {info['emoji']}", inline=False)
        embed.color = 0x00BFFF  
    else:
        embed.description = f"❌ {info}"
        embed.color = 0xFF0000  

    await ctx.send(embed=embed)
    
@bot.tree.command(name="weather",description="get the weather in the selected city")
@app_commands.describe(
    city="Enter a city name"
)
async def weather_slash(interaction, city: str):
    info = fetch_weather(city)
    embed = discord.Embed()
    if isinstance(info, dict):
        embed.title = f"Weather in {city.title()} {info['emoji']}"
        embed.add_field(name="Temperature", value=f"{info['temperature']}°C", inline=False)
        embed.add_field(name="Condition", value=f"{info['description'].capitalize()} {info['emoji']}", inline=False)
        embed.color = 0x00BFFF
    else:
        embed.description = f"❌ {info}"
        embed.color = 0xFF0000

    await interaction.response.send_message(embed=embed)






bot.run(token, log_handler=handler, log_level=logging.DEBUG)
