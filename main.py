import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask

# --- سيرفر وهمي لإرضاء Koyeb ---
app = Flask('')
@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')

@bot.command()
async def p(ctx):
    await ctx.send(f"🎮 **{ctx.author.name}'s Profile**\nStatus: Active ✅")

# --- التشغيل ---
keep_alive() # تشغيل السيرفر الوهمي قبل البوت
bot.run(os.getenv("TOKEN"))
