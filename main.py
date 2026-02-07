import re
import discord
from discord.ext import commands
import os
import json
from threading import Thread
from flask import Flask

# --- (1) نظام الـ Uptime ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online 🚀"
def run(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run).start()

# --- (2) الإعدادات وقاعدة البيانات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_FLAGS = ["🇦🇫", "🇩🇿", "🇦🇸", "🇦🇩", "🇦🇴", "🇦🇮", "🇦🇬", "🇦🇷", "🇦🇲", "🇦🇼", "🇦🇺", "🇦🇹", "🇦🇿", "🇧🇸", "🇧🇭", "🇧🇩", "🇧🇧", "🇧🇾", "🇧🇪", "🇧🇿", "🇧🇯", "🇧🇲", "🇧🇹", "🇧🇴", "🇧🇦", "🇧🇼", "🇧🇷", "🇮🇨", "🇨🇻", "🇨🇦", "🇨🇱", "🇨🇳", "🇨🇴", "🇰🇲", "🇨🇬", "🇨🇩", "🇨🇷", "🇨🇮", "🇭🇷", "🇨🇺", "🇨🇼", "🇨🇾", "🇨🇿", "🇩🇰", "🇩🇯", "🇩🇲", "🇩🇴", "🇪🇨", "🇪🇬", "🇸🇻", "🇬🇶", "🇪🇷", "🇪🇪", "🇪🇹", "🇫🇯", "🇫🇮", "🇫🇷", "🇬🇦", "🇬🇲", "🇬🇪", "🇩🇪", "🇬🇭", "🇬🇮", "🇬🇷", "🇬🇱", "🇬🇩", "🇬🇵", "🇬🇺", "🇬🇹", "🇬🇳", "🇬🇼", "🇬🇾", "🇭🇹", "🇭🇳", "🇭🇰", "🇭🇺", "🇮🇸", "🇮🇳", "🇮🇩", "🇮🇷", "🇮🇶", "🇮🇪", "🇮🇹", "🇯🇲", "🇯🇵", "🇯🇴", "🇰🇿", "🇰🇪", "🇰🇼", "🇰🇬", "🇱🇦", "🇱🇻", "🇱🇧", "🇱🇸", "🇱🇷", "🇱🇾", "🇱🇮", "🇱🇹", "🇱🇺", "🇲🇴", "🇲🇰", "🇲🇬", "🇲🇼", "🇲🇾", "🇲🇻", "🇲🇱", "🇲🇹", "🇲🇽", "🇲🇩", "🇲🇨", "🇲🇳", "🇲🇪", "🇲🇦", "🇲🇿", "🇲🇲", "🇳🇦", "🇳🇵", "🇳🇱", "🇳🇿", "🇳🇮", "🇳🇪", "🇳🇬", "🇰🇵", "🇳🇴", "🇴🇲", "🇵🇰", "🇵🇼", "🇵🇸", "🇵🇦", "🇵🇬", "🇵🇾", "🇵🇪", "🇵🇭", "🇵🇱", "🇵🇹", "🇵🇷", "🇶🇦", "🇷🇴", "🇷🇺", "🇷🇼", "🇸🇲", "🇸🇦", "🇸🇳", "🇷🇸", "🇸🇨", "🇸🇱", "🇸🇬", "🇸🇰", "🇸🇮", "🇸🇧", "🇸🇴", "🇿🇦", "🇰🇷", "🇸🇸", "🇪🇸", "🇱🇰", "🇸🇩", "🇸🇷", "🇸🇿", "🇸🇪", "🇨🇭", "🇸🇾", "🇹🇼", "🇹🇯", "🇹🇿", "🇹🇭", "🇹🇱", "🇹🇬", "🇹🇴", "🇹🇹", "🇹🇳", "🇹🇷", "🇹🇲", "🇹🇻", "🇺🇬", "🇺🇦", "🇦🇪", "🇬🇧", "🇺🇳", "🇺🇸", "🇺🇾", "🇺🇿", "🇻🇺", "🇻🇦", "🇻🇪", "🇻🇳", "🇾🇪", "🇿🇲", "🇿🇼"]

def save_data(data):
    with open('players.json', 'w') as f: json.dump(data, f, indent=4)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f: return json.load(f)
    return {}

# دالة مساعدة للردود الموحدة (Embed)
async def send_success_embed(ctx, title, message):
    embed = discord.Embed(title=f"✅ {title}", description=message, color=discord.Color.blue())
    await ctx.send(embed=embed)

# --- (3) نظام القوائم المنسدلة (Selection Menus) ---
class DropdownMenu(discord.ui.View):
    def __init__(self, author, field, options):
        super().__init__(timeout=60)
        self.author = author
        self.field = field
        select = discord.ui.Select(placeholder=f"Choose {field}...", options=[discord.SelectOption(label=opt, value=opt) for opt in options])
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author: return
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data: data[uid] = {}
        data[uid][self.field] = interaction.data['values'][0]
        save_data(data)
        embed = discord.Embed(title="✅ Success!", description=f"Your {self.field} has been set to **{interaction.data['values'][0]}**.", color=discord.Color.blue())
        await interaction.response.edit_message(embed=embed, view=None)

# --- (4) الأوامر الأساسية للاعبين ---

@bot.command(aliases=['p'])
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data().get(str(member.id), {})
    has_verify_role = discord.utils.get(member.roles, name="Verified Player")
    joined = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg = member.created_at.strftime("%b %d, %Y")
    embed = discord.Embed(title=f"👤 {member.display_name}'s profile", color=discord.Color.blue())
    embed.add_field(name="👥 Profile", value=f"**PSN**: {data.get('psn', '-')}\n**Country**: {data.get('country', '-')}\n**NAT Type**: {data.get('nat', '-')}\n**Joined**: {joined}\n**Registered**: {reg}", inline=False)
    game_data = f"**Ranked Name**: {data.get('ranked_name', '-')}\n**Consoles**: {data.get('consoles', '-')}"
    if has_verify_role: game_data += "\n**Verified Player** ✅"
    embed.add_field(name="🎮 Game Data", value=game_data, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def set_psn(ctx, psn_id: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", psn_id):
        await ctx.send("❌ Error: PSN can only contain letters, numbers, (_) and (-).")
        return
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data: data[uid] = {}
    data[uid]["psn"] = psn_id
    save_data(data)
    await send_success_embed(ctx, "PSN Updated", f"Your PSN has been set to `{psn_id}`")

@bot.command()
async def set_flag(ctx, emoji: str):
    data = load_data()
    uid = str(ctx.author.id)
    if uid in data and "country" in data[uid] and not any(r.name == 'Mod' for r in ctx.author.roles):
        await ctx.send("⚠️ You cannot change your flag. Contact a Mod.")
        return
    if emoji not in ALLOWED_FLAGS:
        await ctx.send("❌ Error: Please use a valid country flag emoji.")
        return
    if uid not in data: data[uid] = {}
    data[uid]["country"] = emoji
    save_data(data)
    await send_success_embed(ctx, "Country Updated", f"Your flag has been set to {emoji}")

@bot.command()
async def set_nat(ctx):
    view = DropdownMenu(ctx.author, "nat", ["NAT 1", "NAT 2 Open", "NAT 2 Closed", "NAT 3"])
    await ctx.send(embed=discord.Embed(title="ℹ️ Info", description="Please select NAT type.", color=discord.Color.blue()), view=view)

@bot.command()
async def set_consoles(ctx):
    view = DropdownMenu(ctx.author, "consoles", ["PS4", "PS5"])
    await ctx.send(embed=discord.Embed(title="ℹ️ Info", description="Please select your console.", color=discord.Color.blue()), view=view)

@bot.command()
async def set_ranked_name(ctx, name: str):
    if not name.isalnum():
        await ctx.send("❌ Error: Ranked Name must be without spaces or special symbols.")
        return
    data = load_data()
    uid = str(ctx.author.id)
    if uid in data and "ranked_name" in data[uid]:
        await ctx.send("⚠️ You cannot change your name. Contact a Mod.")
        return
    if uid not in data: data[uid] = {}
    data[uid]["ranked_name"] = name
    save_data(data)
    await send_success_embed(ctx, "Ranked Name Set", f"Your ranked name is now `{name}`")

# --- (5) أوامر المشرفين (رتبة Mod فقط) ---

@bot.command()
async def verify(ctx, member: discord.Member):
    if not any(role.name == 'Mod' for role in ctx.author.roles):
        await ctx.send("❌ This command is for **Mods** only.")
        return
    role = discord.utils.get(ctx.guild.roles, name="Verified Player")
    if role: 
        await member.add_roles(role)
        await send_success_embed(ctx, "Success!", f"{member.mention} has been verified.")
    else: await ctx.send("❌ Role `Verified Player` not found.")

@bot.command()
async def admin_set(ctx, member: discord.Member, field: str, *, value: str):
    if not any(role.name == 'Mod' for role in ctx.author.roles):
        await ctx.send("❌ For **Mods** only.")
        return
    valid_fields = ["psn", "country", "nat", "consoles", "ranked_name"]
    if field not in valid_fields:
        await ctx.send(f"❌ Field must be one of: {', '.join(valid_fields)}")
        return
    data = load_data()
    uid = str(member.id)
    if uid not in data: data[uid] = {}
    data[uid][field] = value
    save_data(data)
    await send_success_embed(ctx, "Admin Override", f"Updated `{field}` for {member.display_name} to `{value}`")

# ==========================================
# (6) منطقة إضافة الكوماندات الجديدة - أضف هنا مستقبلاً
# ==========================================

# مثال:
# @bot.command()
# async def new_command(ctx):
#     pass

# ==========================================
# (7) معالج الأخطاء والتشغيل
# ==========================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Error: هذا الأمر غير موجود أو مفقود.")
    else: await ctx.send(f"⚠️ Error: {str(error)}")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("TOKEN"))
