import discord
from discord.ext import commands
import os
import urllib.parse

# --- الإعدادات الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# قاعدة بيانات مؤقتة في الرام (تصفر عند إعادة تشغيل البوت)
user_profiles = {}
lobby_counter = 1

def get_blank_profile():
    return {
        'psn': '-', 'country': '🌐', 'region': '-', 'languages': '-',
        'birthday': '-', 'nat': '-', 'timezone': '-', 'ranked_name': '-',
        'consoles': '-', 'character': '-', 'track': '-', 'arena': '-',
        'engine': '-', 'verified': False
    }

@bot.event
async def on_ready():
    print(f'✅ Connected as {bot.user}')

# --- معالجة الأخطاء (إذا الأمر غير موجود) ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ **Sorry {ctx.author.mention}, I couldn't find that command.** Please check your spelling.")
    else:
        raise error

# --- نظام البروفايل ---
@bot.command(name="p")
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    p = user_profiles.get(member.id, get_blank_profile())
    
    embed = discord.Embed(title=f"{member.name}'s profile", color=0x3498db)
    embed.set_thumbnail(url=member.display_avatar.url)
    
    profile_info = (
        f"**PSN:** {p['psn']}\n**Country:** {p['country']}\n**Region:** {p['region']}\n"
        f"**Languages:** {p['languages']}\n**Birthday:** {p['birthday']}\n"
        f"**NAT Type:** {p['nat']}\n**Time Zone:** {p['timezone']}"
    )
    embed.add_field(name="👤 Profile", value=profile_info, inline=False)
    
    game_data = (
        f"**Ranked Name:** {p['ranked_name']}\n**Consoles:** {p['consoles']}\n"
        f"**Fav. Character:** {p['character']}\n**Fav. Track:** {p['track']}\n"
        f"**Fav. Arena:** {p['arena']}\n**Engine Style:** {p['engine']}\n"
        f"**Verified Player:** {'✅' if p['verified'] else '❌'}"
    )
    embed.add_field(name="🎮 Game Data", value=game_data, inline=False)
    
    if member == ctx.author:
        embed.set_footer(text="Use !set_[field] to customize your profile.")
    
    await ctx.send(embed=embed)

# --- أوامر التخصيص (الـ 12 أمر) ---
def update_field(user_id, field, value):
    if user_id not in user_profiles:
        user_profiles[user_id] = get_blank_profile()
    user_profiles[user_id][field] = value

@bot.command()
async def set_psn(ctx, *, val): update_field(ctx.author.id, 'psn', val); await ctx.send(f"✅ PSN updated.")

@bot.command()
async def set_ranked_name(ctx, *, val): update_field(ctx.author.id, 'ranked_name', val); await ctx.send(f"✅ Ranked Name updated.")

@bot.command()
async def set_country(ctx, *, val): update_field(ctx.author.id, 'country', val); await ctx.send(f"✅ Country updated.")

@bot.command()
async def set_region(ctx, *, val): update_field(ctx.author.id, 'region', val); await ctx.send(f"✅ Region updated.")

@bot.command()
async def set_languages(ctx, *, val): update_field(ctx.author.id, 'languages', val); await ctx.send(f"✅ Languages updated.")

@bot.command()
async def set_birthday(ctx, *, val): update_field(ctx.author.id, 'birthday', val); await ctx.send(f"✅ Birthday updated.")

@bot.command()
async def set_nat(ctx, *, val): update_field(ctx.author.id, 'nat', val); await ctx.send(f"✅ NAT Type updated.")

@bot.command()
async def set_time_zone(ctx, *, val): update_field(ctx.author.id, 'timezone', val); await ctx.send(f"✅ Time Zone updated.")

@bot.command()
async def set_consoles(ctx, *, val): update_field(ctx.author.id, 'consoles', val); await ctx.send(f"✅ Consoles updated.")

@bot.command()
async def set_track(ctx, *, val): update_field(ctx.author.id, 'track', val); await ctx.send(f"✅ Fav. Track updated.")

@bot.command()
async def set_character(ctx, *, val): update_field(ctx.author.id, 'character', val); await ctx.send(f"✅ Fav. Character updated.")

@bot.command()
async def set_arena(ctx, *, val): update_field(ctx.author.id, 'arena', val); await ctx.send(f"✅ Fav. Arena updated.")

@bot.command()
async def set_engine(ctx, *, val): update_field(ctx.author.id, 'engine', val); await ctx.send(f"✅ Engine Style updated.")

# --- تشغيل البوت ---
bot.run(os.getenv("TOKEN"))

