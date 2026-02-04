import discord
from discord.ext import commands
import os
import urllib.parse

# --- الإعدادات الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# قاعدة بيانات مؤقتة (تخزن في الرام)
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
    print(f'✅ {bot.user} is now ONLINE and ready!')

# --- معالجة الأخطاء (إذا كتب أمر خطأ) ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ **Sorry {ctx.author.name}, I couldn't find that command!**")

# --- نظام البروفايل !p ---
@bot.command(name="p")
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    p = user_profiles.get(member.id, get_blank_profile())
    
    embed = discord.Embed(title=f"{member.name}'s profile", color=0x3498db)
    
    profile_info = (
        f"**PSN:** {p['psn']}\n**Country:** {p['country']}\n**Region:** {p['region']}\n"
        f"**NAT Type:** {p['nat']}\n**Time Zone:** {p['timezone']}"
    )
    embed.add_field(name="👤 Profile", value=profile_info, inline=False)
    
    game_data = (
        f"**Ranked Name:** {p['ranked_name']}\n**Consoles:** {p['consoles']}\n"
        f"**Verified Player:** {'✅' if p['verified'] else '❌'}"
    )
    embed.add_field(name="🎮 Game Data", value=game_data, inline=False)
    
    embed.set_footer(text="Use !set_[field] to customize (e.g., !set_psn Name)")
    await ctx.send(embed=embed)

# --- أوامر التعديل الـ 12 ---
def update_p(uid, field, val):
    if uid not in user_profiles: user_profiles[uid] = get_blank_profile()
    user_profiles[uid][field] = val

@bot.command()
async def set_psn(ctx, *, v): update_p(ctx.author.id, 'psn', v); await ctx.send("✅ PSN updated.")
@bot.command()
async def set_ranked_name(ctx, *, v): update_p(ctx.author.id, 'ranked_name', v); await ctx.send("✅ Ranked Name updated.")
@bot.command()
async def set_country(ctx, *, v): update_p(ctx.author.id, 'country', v); await ctx.send("✅ Country updated.")
@bot.command()
async def set_region(ctx, *, v): update_p(ctx.author.id, 'region', v); await ctx.send("✅ Region updated.")
@bot.command()
async def set_languages(ctx, *, v): update_p(ctx.author.id, 'languages', v); await ctx.send("✅ Languages updated.")
@bot.command()
async def set_birthday(ctx, *, v): update_p(ctx.author.id, 'birthday', v); await ctx.send("✅ Birthday updated.")
@bot.command()
async def set_nat(ctx, *, v): update_p(ctx.author.id, 'nat', v); await ctx.send("✅ NAT updated.")
@bot.command()
async def set_timezone(ctx, *, v): update_p(ctx.author.id, 'timezone', v); await ctx.send("✅ Timezone updated.")
@bot.command()
async def set_consoles(ctx, *, v): update_p(ctx.author.id, 'consoles', v); await ctx.send("✅ Consoles updated.")
@bot.command()
async def set_track(ctx, *, v): update_p(ctx.author.id, 'track', v); await ctx.send("✅ Track updated.")
@bot.command()
async def set_character(ctx, *, v): update_p(ctx.author.id, 'character', v); await ctx.send("✅ Character updated.")
@bot.command()
async def set_engine(ctx, *, v): update_p(ctx.author.id, 'engine', v); await ctx.send("✅ Engine updated.")

# --- تشغيل ---
bot.run(os.getenv("TOKEN"))
