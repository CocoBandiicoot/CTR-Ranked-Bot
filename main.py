import discord
from discord.ext import commands
import os
import json # بنستخدمه لحفظ بيانات اللاعبين
from threading import Thread
from flask import Flask

# --- (1) السيرفر الوهمي (عشان UptimeRobot) ---
app = Flask('')
@app.route('/')
def home():
    return "البوت شغال ومنور!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- (2) إعدادات البوت الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- (3) نظام حفظ البيانات (قاعدة بيانات بسيطة) ---
def save_data(data):
    with open('players.json', 'w') as f:
        json.dump(data, f)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f:
            return json.load(f)
    return {}

# --- (4) حدث تشغيل البوت ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE and ready!')

# ==========================================
# هنا سنبدأ بإضافة الأوامر واحد تلو الآخر
# ==========================================

# (تحت هذا السطر سنضع الكوماندات الجديدة)

# --- سطر التشغيل (دائماً في الأخير) ---
keep_alive()
bot.run(os.getenv("TOKEN"))
