import re
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
# (4) قسم الأوامر - نسخة نظيفة بدون تكرار
# ==========================================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! السرعة: {round(bot.latency * 1000)}ms")

# --- أمر البروفايل المطور (يعرض الشرطات تلقائياً) ---
@bot.command(aliases=['profile'])
async def p(ctx, member: discord.Member = None):
    member = member or ctx.author
    players = load_data()
    data = players.get(str(member.id), {})

    joined_srv = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg_discord = member.created_at.strftime("%b %d, %Y")

    embed = discord.Embed(title=f"👤 {member.display_name}'s profile", color=discord.Color.blue())
    
    profile_info = (
        f"**PSN**: {data.get('psn', '-')}\n"
        f"**Country**: {data.get('country', '-')}\n"
        f"**NAT Type**: {data.get('nat', '-')}\n"
        f"**Joined**: {joined_srv}\n"
        f"**Registered**: {reg_discord}"
    )
    embed.add_field(name="👥 Profile", value=profile_info, inline=False)

    game_info = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if data.get("verified"):
        game_info += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_info, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"ID: {member.id} • !p help")
    await ctx.send(embed=embed)

# --- أوامر تعبئة البيانات ---

@bot.command()
async def set_psn(ctx, psn_id: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", psn_id):
        await ctx.send("❌ خطأ: الـ PSN لا يسمح بالمسافات (مسموح فقط بـ _ و -).")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["psn"] = psn_id
    save_data(players)
    await ctx.send(f"✅ تم تحديث الـ PSN")

@bot.command()
async def set_flag(ctx, emoji: str):
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["country"] = emoji
    save_data(players)
    await ctx.send(f"✅ تم تعيين العلم")

@bot.command()
async def set_nat(ctx, *, nat_type: str):
    valid_types = ["NAT 1", "NAT 2 Close", "NAT 2 Open", "NAT 3"]
    if nat_type not in valid_types:
        await ctx.send(f"❌ اختر: `NAT 1`, `NAT 2 Close`, `NAT 2 Open`, `NAT 3`")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["nat"] = nat_type
    save_data(players)
    await ctx.send(f"✅ تم تحديث الـ NAT")

@bot.command()
async def set_ranked_name(ctx, name: str):
    if not name.isalnum():
        await ctx.send("❌ خطأ: اسم الرانك يجب أن
