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
# (4) قسم الأوامر - هنا تضع كل أمر جديد تحت الآخر
# ==========================================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! السرعة: {round(bot.latency * 1000)}ms")

# مثال: هنا ستضع أمر !register القادم أو أمر !p 
# @bot.command()
# async def command_name(ctx):
#     ...
@bot.command(aliases=['profile'])
async def p(ctx, member: discord.Member = None):
    member = member or ctx.author
    players = load_data()
    data = players.get(str(member.id), {})

    # جلب التواريخ تلقائياً من نظام ديسكورد
    joined_srv = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg_discord = member.created_at.strftime("%b %d, %Y")

    embed = discord.Embed(
        title=f"👤 {member.display_name}'s profile",
        color=discord.Color.blue()
    )

    # 👥 قسم المعلومات الشخصية
    profile_info = (
        f"**PSN**: {data.get('psn', '-')}\n"
        f"**Country**: {data.get('country', '-')}\n"
        f"**NAT Type**: {data.get('nat', '-')}\n"
        f"**Joined**: {joined_srv}\n"
        f"**Registered**: {reg_discord}"
    )
    embed.add_field(name="👥 Profile", value=profile_info, inline=False)

    # 🎮 قسم بيانات اللعبة
    game_info = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    
    # يظهر Verified Player ✅ فقط إذا تم توثيقه
    if data.get("verified"):
        game_info += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_info, inline=False)
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"!profile help • id: {member.id}")
    
    await ctx.send(embed=embed)

    # إضافة بيانات اللعبة
    game_info = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if data.get("verified"): game_info += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_info, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    
    await ctx.send(embed=embed)

    # حالة التوثيق (Verified)
    status = "Verified Player ✅" if data.get('verified') else "Not Verified ❌"
    embed.add_field(name="🛡️ Status", value=status, inline=False)
    
    # وضع صورة اللاعب في الزاوية
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    embed.set_footer(text="CTR Ranked System 🏎️")
    
    await ctx.send(embed=embed)
@bot.command()
async def verify(ctx, member: discord.Member):
    # 1. التحقق من رتبة المشرف (لازم يكون عنده رول اسمه mod)
    if not any(role.name == 'mod' for role in ctx.author.roles):
        await ctx.send("❌ هذا الأمر مخصص للمشرفين فقط (رول mod)!")
        return

    # 2. جلب رتبة التوثيق (تأكد أن اسمها في سيرفرك Verified Player)
    verify_role = discord.utils.get(ctx.guild.roles, name="Verified Player")
    
    if not verify_role:
        await ctx.send("❌ لم أجد رتبة باسم `Verified Player` في السيرفر، يرجى إنشاؤها!")
        return

    # 3. إعطاء الرتبة للاعب وتحديث بياناته
    await member.add_roles(verify_role)
    
    players = load_data()
    user_id = str(member.id)
    
    if user_id in players:
        players[user_id]["verified"] = True
        save_data(players)
    
    # 4. إرسال رسالة "Success" في نفس الروم
    success_embed = discord.Embed(
        title="✅ Success!",
        description=f"لقد تم توثيق {member.mention} بنجاح وإعطاؤه رتبة التوثيق.",
        color=discord.Color.green()
    )
    await ctx.send(embed=success_embed)

    # 5. إرسال رسالة "How to play" في روم اللوبيات (ranked-lobbies)
    # ملاحظة: البوت بيبحث عن الروم بالاسم تلقائياً
    lobby_channel = discord.utils.get(ctx.guild.text_channels, name="ranked-lobbies")
    
    if lobby_channel:
        how_to_play = discord.Embed(
            title="🎮 How to play ranked matchmaking",
            description=(
                "Press the ✅ **Join** button to join a lobby queue, and wait for it to become full.\n"
                "Press the ❌ **Leave** button to leave the lobby queue.\n\n"
                "⚠️ Do not join team based lobbies if you can't/aren't willing to communicate in **voice chat**.\n"
                "Once a lobby has started you will be pinged in a dedicated **lobby-room** channel.\n\n"
                "The **scorekeeper** and **host** will be decided. Do not press ✅ to volunteer for scorekeeping if you don't know how.\n"
                "Find out the **PSN** of the host and join their lobby, or ask for an invite.\n\n"
                "**Active lobbies are shown below**"
            ),
            color=discord.Color.blue()
        )
        await lobby_channel.send(content=member.mention, embed=how_to_play)
# --- (1) أمر البروفايل المطور (بدون رسائل خطأ) ---
@bot.command(aliases=['profile'])
async def p(ctx, member: discord.Member = None):
    member = member or ctx.author
    players = load_data()
    data = players.get(str(member.id), {})

    # جلب التواريخ تلقائياً من نظام ديسكورد
    joined_srv = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "Unknown"
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

    game_data = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if data.get("verified"):
        game_data += "\n**Verified Player** ✅"
    
    embed.add_field(name="🎮 Game Data", value=game_data, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# --- (2) أوامر تعبئة البيانات (Set Commands) ---

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
        await ctx.send("❌ خطأ: اسم الرانك يجب أن يكون بدون مسافات أو رموز.")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["ranked_name"] = name
    save_data(players)
    await ctx.send(f"✅ تم تحديث اسم الرانك")

@bot.command()
async def set_consoles(ctx, console: str):
    console = console.upper()
    if console not in ["PS4", "PS5"]:
        await ctx.send("❌ اختر `PS4` أو `PS5`.")
        return
    players = load_data()
    user_id = str(ctx.author.id)
    if user_id not in players: players[user_id] = {}
    players[user_id]["consoles"] = console
    save_data(players)
    await ctx.send(f"✅ تم تحديث المنصة")

# ==========================================
# (5) سطر التشغيل النهائي - لا تضع شيئاً تحته
# ==========================================
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي
    bot.run(os.getenv("TOKEN")) # تشغيل البوت
