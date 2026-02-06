import re
import discord
from discord.ext import commands
import os
import json
from threading import Thread
from flask import Flask

# --- (1) محرك الصحصحة (عشان UptimeRobot) ---
app = Flask('')
@app.route('/')
def home(): return "البوت شغال! 🏎️"

def run(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run).start()

# --- (2) إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- (3) نظام حفظ البيانات ---
def save_data(data):
    with open('players.json', 'w') as f: json.dump(data, f)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f: return json.load(f)
    return {}

# --- (4) قسم الأوامر (نسخة واحدة فقط) ---

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.command(aliases=['profile'])
async def p(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data().get(str(member.id), {})
    
    joined = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg = member.created_at.strftime("%b %d, %Y")

    embed = discord.Embed(title=f"👤 {member.display_name}'s profile", color=discord.Color.blue())
    embed.add_field(name="👥 Profile", value=f"**PSN**: {data.get('psn', '-')}\n**Country**: {data.get('country', '-')}\n**NAT**: {data.get('nat', '-')}\n**Joined**: {joined}\n**Reg**: {reg}", inline=False)
    
    game_info = f"**Rank**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if data.get("verified"): game_info += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_info, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def set_psn(ctx, psn_id: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", psn_id):
        await ctx.send("❌ خطأ في الـ PSN")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["psn"] = psn_id
    save_data(players)
    await ctx.send("✅ تم تحديث الـ PSN")

@bot.command()
async def verify(ctx, member: discord.Member):
    if not any(role.name == 'mod' for role in ctx.author.roles):
        await ctx.send("❌ للمشرفين فقط")
        return
    role = discord.utils.get(ctx.guild.roles, name="Verified Player")
    if role: await member.add_roles(role)
    players = load_data()
    user_id = str(member.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["verified"] = True
    save_data(players)
    await ctx.send(f"✅ تم توثيق {member.mention}")

# --- (5) سطر التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("TOKEN"))
