import discord
from discord.ext import commands
import os
import json
from threading import Thread
from flask import Flask

# --- (1) محرك الصحصحة (عشان UptimeRobot يخلي البوت Healthy) ---
app = Flask('')
@app.route('/')
def home():
    return "البوت شغال وبكامل قواه العقلية! 🏎️"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- (2) إعدادات البوت الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- (3) نظام حفظ وقراءة بيانات اللاعبين ---
def save_data(data):
    with open('players.json', 'w') as f:
        json.dump(data, f)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f:
            return json.load(f)
    return {}

# ==========================================
# (4) قسم الأوامر - هنا تضع كل أمر جديد تحت الآخر
# ==========================================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! السرعة: {round(bot.latency * 1000)}ms")

# مثال: هنا ستضع أمر !register القادم أو أمر !p 
# @bot.command()
# async def command_name(ctx):
#     ...
@bot.command()
async def p(ctx):
    players = load_data()
    user_id = str(ctx.author.id)
    
    # التحقق إذا كان اللاعب مسجل أم لا
    if user_id not in players:
        embed_error = discord.Embed(
            title="❌ ملف غير موجود",
            description="أنت غير مسجل في النظام. استخدم أمر `!register [PSN ID]` أولاً.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    data = players[user_id]
    
    # إنشاء المربع (Embed) الخاص بالبروفايل
    embed = discord.Embed(
        title=f"👤 {ctx.author.display_name}'s profile",
        description="Check out the PSN profile below.",
        color=discord.Color.blue()
    )
    
    # إضافة المعلومات (مثل الصورة اللي أرسلتها)
    embed.add_field(name="🎮 PSN ID", value=f"`{data.get('psn', 'N/A')}`", inline=True)
    embed.add_field(name="🏆 Rank", value=data.get('rank', 'Bronze'), inline=True)
    embed.add_field(name="✨ Points", value=str(data.get('points', 0)), inline=True)
    
    # حالة التوثيق (Verified)
    status = "Verified Player ✅" if data.get('verified') else "Not Verified ❌"
    embed.add_field(name="🛡️ Status", value=status, inline=False)
    
    # وضع صورة اللاعب في الزاوية
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    embed.set_footer(text="CTR Ranked System 🏎️")
    
    await ctx.send(embed=embed)

# ==========================================
# (5) سطر التشغيل النهائي - لا تضع شيئاً تحته
# ==========================================
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي
    bot.run(os.getenv("TOKEN")) # تشغيل البوت
