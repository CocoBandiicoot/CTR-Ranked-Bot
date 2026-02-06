import re
import discord
from discord.ext import commands
import os
import json
from threading import Thread
from flask import Flask

# --- (1) محرك التشغيل ---
app = Flask('')
@app.route('/')
def home(): return "البوت شغال! 🏎️"
def run(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run).start()

# --- (2) الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def save_data(data):
    with open('players.json', 'w') as f: json.dump(data, f, indent=4)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f: return json.load(f)
    return {}

# --- (3) فحص صلاحيات المشرفين ---
def is_admin():
    async def predicate(ctx):
        # البوت سيعتبرك مشرفاً إذا كنت صاحب السيرفر أو عندك صلاحية Administrator
        return ctx.author.guild_permissions.administrator or ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)

# --- (4) الأوامر المطورة ---

@bot.command(aliases=['profile'])
async def p(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data().get(str(member.id), {})
    
    # التحقق من رتبة التوثيق فعلياً في السيرفر
    has_verify_role = discord.utils.get(member.roles, name="Verified Player")
    
    joined = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg = member.created_at.strftime("%b %d, %Y")

    embed = discord.Embed(title=f"👤 {member.display_name}'s profile", color=discord.Color.blue())
    
    profile_info = (
        f"**PSN**: {data.get('psn', '-')}\n"
        f"**Country**: {data.get('country', '-')}\n"
        f"**NAT Type**: {data.get('nat', '-')}\n"
        f"**Joined**: {joined}\n"
        f"**Registered**: {reg}"
    )
    embed.add_field(name="👥 Profile", value=profile_info, inline=False)
    
    # تعديل اسم الرانك وظهور علامة التوثيق
    game_data = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if has_verify_role:
        game_data += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_data, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def set_psn(ctx, psn_id: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", psn_id):
        await ctx.send("❌ خطأ: الـ PSN لا يسمح بالمسافات أو الرموز الخاصة عدا (_) و (-).")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["psn"] = psn_id
    save_data(players)
    await ctx.send("✅ تم تحديث الـ PSN")

@bot.command()
async def set_flag(ctx, emoji: str):
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["country"] = emoji
    save_data(players)
    await ctx.send("✅ تم تعيين العلم")

@bot.command()
async def set_nat(ctx):
    options = ["NAT 1", "NAT 2 Close", "NAT 2 Open", "NAT 3"]
    await ctx.send(f"الرجاء اختيار نوع الـ NAT كتابةً: `{', '.join(options)}`")
    
    def check(m): return m.author == ctx.author and m.content in options
    msg = await bot.wait_for('message', check=check)
    
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["nat"] = msg.content
    save_data(players)
    await ctx.send(f"✅ تم اختيار {msg.content}")

@bot.command()
async def set_ranked_name(ctx, name: str):
    if not name.isalnum():
        await ctx.send("❌ خطأ: الاسم يجب أن يكون بدون مسافات أو رموز.")
        return
    
    players = load_data()
    user_id = str(ctx.author.id)
    
    if user_id in players and "ranked_name" in players[user_id]:
        await ctx.send("⚠️ لا يمكنك تغيير اسمك، تواصل مع المشرفين.")
        return
        
    if user_id not in players: players[user_id] = {}
    players[user_id]["ranked_name"] = name
    save_data(players)
    await ctx.send(f"✅ تم تسجيل اسم الرانك: {name}")

@bot.command()
async def set_consoles(ctx):
    options = ["PS4", "PS5"]
    await ctx.send("اختر منصتك كتابةً: `PS4` أو `PS5`")
    
    def check(m): return m.author == ctx.author and m.content.upper() in options
    msg = await bot.wait_for('message', check=check)
    
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["consoles"] = msg.content.upper()
    save_data(players)
    await ctx.send(f"✅ تم تحديث المنصة")

# --- (5) أوامر المشرفين (Admin Only) ---

@bot.command()
@is_admin()
async def admin_set(ctx, member: discord.Member, field: str, *, value: str):
    # يسمح للمشرف بتغيير أي شيء: psn, ranked_name, country, nat, consoles
    players = load_data()
    user_id = str(member.id)
    if user_id not in players: players[user_id] = {}
    players[user_id][field] = value
    save_data(players)
    await ctx.send(f"✅ تم تعديل `{field}` للعضو {member.display_name}")

@bot.command()
@is_admin()
async def verify(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Verified Player")
    if not role:
        await ctx.send("❌ رتبة `Verified Player` غير موجودة!")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ تم توثيق {member.mention} وظهور العلامة في بروفايله.")

# --- (6) التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("TOKEN"))
