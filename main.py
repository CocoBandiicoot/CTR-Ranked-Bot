import discord
from discord.ext import commands
import os, json, re, random, datetime
from threading import Thread
from flask import Flask

# --- (1) Uptime System ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online 🚀"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- (2) الإعدادات والأذونات ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_FLAGS = ["🇦🇫", "🇩🇿", "🇦🇸", "🇦🇩", "🇦🇴", "🇦🇮", "🇦🇬", "🇦🇷", "🇦🇲", "🇦🇼", "🇦🇺", "🇦🇹", "🇦🇿", "🇧🇸", "🇧🇭", "🇧🇩", "🇧🇧", "🇧🇾", "🇧🇪", "🇧🇿", "🇧🇯", "🇧🇲", "🇧🇹", "🇧🇴", "🇧🇦", "🇧🇼", "🇧🇷", "🇮🇨", "🇨🇻", "🇨🇦", "🇨🇱", "🇨🇳", "🇨🇴", "🇰🇲", "🇨🇬", "🇨🇩", "🇨🇷", "🇨🇮", "🇭🇷", "🇨🇺", "🇨🇼", "🇨🇾", "🇨🇿", "🇩🇰", "🇩🇯", "🇩🇲", "🇩🇴", "🇪🇨", "🇪🇬", "🇸🇻", "🇬🇶", "🇪🇷", "🇪🇪", "🇪🇹", "🇫🇯", "🇫🇮", "🇫🇷", "🇬🇦", "🇬🇲", "🇬🇪", "🇩🇪", "🇬🇭", "🇬🇮", "🇬🇷", "🇬🇱", "🇬🇩", "🇬🇵", "🇬🇺", "🇬🇹", "🇬🇳", "🇬🇼", "🇬🇾", "🇭🇹", "🇭🇳", "🇭🇰", "🇭🇺", "🇮🇸", "🇮🇳", "🇮🇩", "🇮🇷", "🇮🇶", "🇮🇪", "🇮🇹", "🇯🇲", "🇯🇵", "🇯🇴", "🇰🇿", "🇰🇪", "🇰🇼", "🇰🇬", "🇱🇦", "🇱🇻", "🇱🇧", "🇱🇸", "🇱🇷", "🇱🇾", "🇱🇮", "🇱🇹", "🇱🇺", "🇲🇴", "🇲🇰", "🇲🇬", "🇲🇼", "🇲🇾", "🇲🇻", "🇲🇱", "🇲🇹", "🇲🇽", "🇲🇩", "🇲🇨", "🇲🇳", "🇲🇪", "🇲🇦", "🇲🇿", "🇲🇲", "🇳🇦", "🇳🇵", "🇳🇱", "🇳🇿", "🇳🇮", "🇳🇪", "🇳🇬", "🇰🇵", "🇳🇴", "🇴🇲", "🇵🇰", "🇵🇼", "🇵🇸", "🇵🇦", "🇵🇬", "🇵🇾", "🇵🇪", "🇵🇭", "🇵🇱", "🇵🇹", "🇵🇷", "🇶🇦", "🇷🇴", "🇷🇺", "🇷🇼", "🇸🇲", "🇸🇦", "🇸🇳", "🇷🇸", "🇸🇨", "🇸🇱", "🇸🇬", "🇸🇰", "🇸🇮", "🇸🇧", "🇸🇴", "🇿🇦", "🇰🇷", "🇸🇸", "🇪🇸", "🇱🇰", "🇸🇩", "🇸🇷", "🇸🇿", "🇸🇪", "🇨🇭", "🇸🇾", "🇹🇼", "🇹🇯", "🇹🇿", "🇹🇭", "🇹🇱", "🇹🇬", "🇹🇴", "🇹🇹", "🇹🇳", "🇹🇷", "🇹🇲", "🇹🇻", "🇺🇬", "🇺🇦", "🇦🇪", "🇬🇧", "🇺🇳", "🇺🇸", "🇺🇾", "🇺🇿", "🇻🇺", "🇻🇦", "🇻🇪", "🇻🇳", "🇾🇪", "🇿🇲", "🇿🇼"]

def save_data(data):
    with open('players.json', 'w') as f: json.dump(data, f, indent=4)

def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f: return json.load(f)
    return {}

async def send_success_embed(ctx, title, message):
    embed = discord.Embed(title=f"✅ {title}", description=message, color=discord.Color.blue())
    await ctx.send(embed=embed)

# --- (3) نظام القوائم المنسدلة ---
class DropdownMenu(discord.ui.View):
    def __init__(self, author, field, options): # تعديل هنا
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
        embed = discord.Embed(title="✅ Success!", description=f"Your {self.field} has been set to {interaction.data['values'][0]}.", color=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=None)

# --- (4) أوامر اللاعبين ---

@bot.command(aliases=['p'])
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    all_data = load_data()
    user_id = str(member.id)
    
    if user_id not in all_data:
        all_data[user_id] = {"points": 1200}
        save_data(all_data)

    data = all_data.get(user_id, {})
    pts = data.get('points', 1200)
    is_banned = any(role.name == "Ranked Banned" for role in member.roles)
    
    joined = member.joined_at.strftime("%b %d, %Y") if member.joined_at else "-"
    reg = member.created_at.strftime("%b %d, %Y") if member.created_at else "-"

    embed = discord.Embed(title=f"👤 {member.display_name}'s profile", color=discord.Color.red() if is_banned else discord.Color.blue())
    profile_val = f"**MMR Points**: {pts}\n**PSN**: {data.get('psn', '-')}\n**Country**: {data.get('country', '-')}\n**NAT Type**: {data.get('nat', '-')}\n**Joined**: {joined}\n**Registered**: {reg}"
    embed.add_field(name="📊 Profile", value=profile_val, inline=False)
    
    status = "❌ **Status: Banned**" if is_banned else "✅ **Status: Active**"
    embed.add_field(name="🎮 Game Data", value=f"{status}\n**Consoles**: {data.get('consoles', '-')}", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def set_psn(ctx, psn_id: str):
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data: data[uid] = {}
    data[uid]["psn"] = psn_id
    save_data(data)
    await send_success_embed(ctx, "PSN Updated", f"Your PSN has been set to **{psn_id}**")

@bot.command()
async def set_flag(ctx, emoji: str):
    if emoji not in ALLOWED_FLAGS: return await ctx.send("❌ Flag not allowed.")
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data: data[uid] = {}
    data[uid]["country"] = emoji
    save_data(data)
    await send_success_embed(ctx, "Flag Updated", f"Your country is now {emoji}")

@bot.command()
async def set_nat(ctx):
    view = DropdownMenu(ctx.author, "nat", ["NAT 1", "NAT 2 Open", "NAT 3"])
    await ctx.send("Select your NAT Type:", view=view)

# --- (5) أوامر المشرفين (رتبة Mod) ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def ranked_ban(ctx, member: discord.Member, duration: str = "forever", *, reason="No reason"):
    role = discord.utils.get(ctx.guild.roles, name="Ranked Banned")
    if not role: return await ctx.send("❌ Create 'Ranked Banned' role first!")
    await member.add_roles(role)
    embed = discord.Embed(title="🚫 Ranked Ban", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Reason", value=reason)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def ranked_unban(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Ranked Banned")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"✅ {member.mention} has been unbanned.")

@bot.command()
async def update_points(ctx, member: discord.Member, amount: int):
    if not any(role.name == 'Mod' for role in ctx.author.roles): return
    data = load_data()
    uid = str(member.id)
    data[uid]['points'] = data.get(uid, {"points": 1200}).get('points', 1200) + amount
    save_data(data)
    await ctx.send(f"✅ Updated! {member.display_name} points: **{data[uid]['points']}**")

# --- (6) التشغيل النهائي ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))

# ==========================================
# (7) منطقة اللوبيات - أضف هنا مستقبلاً
# ==========================================
 # --- (7) إرسال دليل اللوبي تلقائياً ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} 🚀')
    
    # حط هنا آيدي الروم حق اللوبيات
    LOBBY_CHANNEL_ID = 123456789012345678  # <--- غير هذا الرقم للآيدي حقك
    channel = bot.get_channel(LOBBY_CHANNEL_ID)
    
    if channel:
        # مسح الرسائل القديمة عشان ما يتكرر الدليل (اختياري)
        # await channel.purge(limit=10) 
        
        guide_text = (
            "**How to play ranked matchmaking**\n\n"
            "Press the ✅ **Join** button to join a lobby queue, and wait for it to become full.\n"
            "Press the ❌ **Leave** button to leave the lobby queue.\n\n"
            "Do not join team based lobbies if you can't/aren't willing to communicate in **voice chat**.\n"
            "Once a lobby has started you will be pinged in a dedicated **lobby-room** channel.\n"
            "The **scorekeeper** and **host** will be decided. Do not press ✅ to volunteer for scorekeeping if you don't know how.\n"
            "Find out the **PSN** of the host and join their lobby, or ask for an invite.\n\n"
            "**Active lobbies are shown below**\n\n"
            "**كيفية لعب المباريات المصنفة**\n\n"
            "اضغط على زر ✅ **انضمام** للانضمام إلى قائمة انتظار الردهة، وانتظر حتى تكتمل.\n\n"
            "اضغط على زر ❌ **مغادرة** لمغادرة قائمة انتظار الردهة.\n\n"
            "لا تنضم إلى ردهات الفرق إذا لم تكن قادرًا على التواصل عبر **الدردشة الصوتية** أو لم تكن ترغب بذلك.\n\n"
            "بمجرد بدء الردهة، ستتلقى إشعارًا في قناة **غرفة الردهة** المخصصة.\n\n"
            "سيتم تحديد **مسجل النقاط** و**المضيف**. لا تضغط على ✅ للتطوع لتسجيل النقاط إذا كنت لا تعرف كيفية القيام بذلك.\n\n"
            "ابحث عن **معرف PSN** الخاص بالمضيف وانضم إلى ردهته، أو اطلب دعوة.\n\n"
            "**الردهات النشطة معروضة أدناه**"
        )
        
        # البحث إذا كانت الرسالة مرسلة من قبل عشان ما يكررها كل شوي
        async for message in channel.history(limit=20):
            if "**How to play ranked matchmaking**" in message.content:
                print("Guide already exists.")
                return # إذا لقاها يوقف ما يرسل ثانية
        
        await channel.send(guide_text)
        print("Lobby guide sent successfully!")

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة المابات (RNG Tracks)
TRACKS = [
    "Crash Cove", "Mystery Caves", "Sewer Speedway", "Roo's Tubes", "Slide Coliseum", "Turbo Track", 
    "Coco Park", "Tiger Temple", "Papu's Pyramid", "Dingo Canyon", "Polar Pass", "Tiny Arena", 
    "Dragon Mines", "Blizzard Bluff", "Hot Air Skyway", "Cortex Castle", "N.Gin Labs", "Oxide Station", 
    "Inferno Island", "Jungle Boogie", "Clockwork Wumpa", "Android Alley", "Electron Avenue", 
    "Deep Sea Driving", "Thunder Struck", "Tiny Temple", "Meteor Gorge", "Barin Ruins", "Out of Time", 
    "Assembly Lane", "Twilight Tour", "Prehistoric Playground", "Spyro Circuit", "Nina's Nightmare", 
    "Koala Carnival", "Gingerbread Joyride", "Megamix Mania", "Drive-Thru Danger", "Retro Stadium"
]

# قاموس تحويل الأعلام لرموز Lorenzi (sa, kw...)
FLAG_CODES = {
    "🇸🇦": "sa", "🇰🇼": "kw", "🇦🇪": "ae", "🇶🇦": "qa", "🇧🇭": "bh", 
    "🇴🇲": "om", "🇪🇬": "eg", "🇩🇿": "dz", "🇲🇦": "ma", "🇮🇶": "iq", 
    "🇯🇴": "jo", "🇱🇧": "lb", "🇱🇾": "ly", "🇵🇸": "ps", "🇸🇩": "sd", 
    "🇸🇾": "sy", "🇹🇳": "tn", "🇾🇪": "ye", "🇲🇷": "mr", "🇸🇴": "so", 
    "🇩🇯": "dj", "🇰🇲": "km", "🇦🇫": "af", "🇦🇱": "al", "🇦🇩": "ad", 
    "🇦🇴": "ao", "🇦🇬": "ag", "🇦🇷": "ar", "🇦🇲": "am", "🇦🇺": "au", 
    "🇦🇹": "at", "🇦🇿": "az", "🇧🇸": "bs", "🇧🇩": "bd", "🇧🇧": "bb", 
    "🇧🇾": "by", "🇧🇪": "be", "🇧🇿": "bz", "🇧🇯": "bj", "🇧🇹": "bt", 
    "🇧🇴": "bo", "🇧🇦": "ba", "🇧🇼": "bw", "🇧🇷": "br", "🇧🇳": "bn", 
    "🇧🇬": "bg", "🇧🇫": "bf", "🇧🇮": "bi", "🇨🇻": "cv", "🇰🇭": "kh", 
    "🇨🇲": "cm", "🇨🇦": "ca", "🇨🇫": "cf", "🇹🇩": "td", "🇨🇱": "cl", 
    "🇨🇳": "cn", "🇨🇴": "co", "🇨🇬": "cg", "🇨🇷": "cr", "🇨🇮": "ci", 
    "🇭🇷": "hr", "🇨🇺": "cu", "🇨🇾": "cy", "🇨🇿": "cz", "🇩🇰": "dk", 
    "🇩🇲": "dm", "🇩🇴": "do", "🇪🇨": "ec", "🇸🇻": "sv", "🇬🇶": "gq", 
    "🇪🇷": "er", "🇪🇪": "ee", "🇸🇿": "sz", "🇪🇹": "et", "🇫🇯": "fj", 
    "🇫🇮": "fi", "🇫🇷": "fr", "🇬🇦": "ga", "🇬🇲": "gm", "🇬🇪": "ge", 
    "🇩🇪": "de", "🇬🇭": "gh", "🇬🇷": "gr", "🇬🇩": "gd", "🇬🇹": "gt", 
    "🇬🇳": "gn", "🇬🇼": "gw", "🇬🇾": "gy", "🇭🇹": "ht", "🇭🇳": "hn", 
    "🇭🇺": "hu", "🇮🇸": "is", "🇮🇳": "in", "🇮🇩": "id", "🇮🇷": "ir", 
    "🇮🇪": "ie", "🇮🇹": "it", "🇯🇲": "jm", "🇯🇵": "jp", "🇰🇿": "kz", 
    "🇰🇪": "ke", "🇰🇮": "ki", "🇰🇵": "kp", "🇰🇷": "kr", "🇰🇬": "kg", 
    "🇱🇦": "la", "🇱🇻": "lv", "🇱🇸": "ls", "🇱🇷": "lr", "🇱🇮": "li", 
    "🇱🇹": "lt", "🇱🇺": "lu", "🇲🇬": "mg", "🇲🇼": "mw", "🇲🇾": "my", 
    "🇲🇻": "mv", "🇲🇱": "ml", "🇲🇹": "mt", "🇲🇭": "mh", "🇲🇺": "mu", 
    "🇲🇽": "mx", "🇫🇲": "fm", "🇲🇩": "md", "🇲🇨": "mc", "🇲🇳": "mn", 
    "🇲🇪": "me", "🇲🇿": "mz", "🇲🇲": "mm", "🇳🇦": "na", "🇳🇷": "nr", 
    "🇳🇵": "np", "🇳🇱": "nl", "🇳🇿": "nz", "🇳🇮": "ni", "🇳🇪": "ne", 
    "🇳🇬": "ng", "🇲🇰": "mk", "🇳🇴": "no", "🇵🇰": "pk", "🇵🇼": "pw", 
    "🇵🇦": "pa", "🇵🇬": "pg", "🇵🇾": "py", "🇵🇪": "pe", "🇵🇭": "ph", 
    "🇵🇱": "pl", "🇵🇹": "pt", "🇷🇴": "ro", "🇷🇺": "ru", "🇷🇼": "rw", 
    "🇰🇳": "kn", "🇱🇨": "lc", "🇻🇨": "vc", "🇼🇸": "ws", "🇸🇲": "sm", 
    "🇸🇹": "st", "🇸🇳": "sn", "🇷🇸": "rs", "🇸🇨": "sc", "🇸🇱": "sl", 
    "🇸🇬": "sg", "🇸🇰": "sk", "🇸🇮": "si", "🇸🇧": "sb", "🇿🇦": "za", 
    "🇪🇸": "es", "🇱🇰": "lk", "🇸🇷": "sr", "🇸🇪": "se", "🇨🇭": "ch", 
    "🇹🇯": "tj", "🇹🇿": "tz", "🇹🇭": "th", "🇹🇱": "tl", "🇹🇬": "tg", 
    "🇹🇴": "to", "🇹🇹": "tt", "🇹🇷": "tr", "🇹🇲": "tm", "🇹🇻": "tv", 
    "🇺🇬": "ug", "🇺🇦": "ua", "🇬🇧": "gb", "🇺🇸": "us", "🇺🇾": "uy", 
    "🇺🇿": "uz", "🇻🇺": "vu", "🇻🇪": "ve", "🇻🇳": "vn", "🇿🇲": "zm", 
    "🇿🇼": "zw"
}
def load_data():
    if os.path.exists('players.json'):
        with open('players.json', 'r') as f: return json.load(f)
    return {}

def save_data(data):
    with open('players.json', 'w') as f: json.dump(data, f, indent=4)

active_lobbies = {} # لتخزين بيانات اللوبيات
# --- دالة توليد ID عشوائي للوبي ---
# دالة توليد ID عشوائي للوبي
def generate_lobby_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

# دالة اختيار المابات عشوائياً حسب الطور
def get_random_tracks(mode):
    pool = TRACKS.copy()
    random.shuffle(pool)
    if mode == "4v4":
        return pool[:10]
    elif mode == "Itemless":
        return pool[:6]
    else:
        return pool[:8]

# دالة تحويل علم الإيموجي إلى رمز Lorenzi (ISO)
def get_flag_code(emoji):
    return FLAG_CODES.get(emoji, "un") # "un" للغير معروف

# قائمة الأطوار المتاحة
LOBBY_MODES = ["FFA", "Duo", "3v3", "4v4", "Itemless"]

class LobbySelectMenu(discord.ui.Select):
    def __init__(self, author):
        options = [discord.SelectOption(label=m) for m in LOBBY_MODES]
        super().__init__(placeholder="Choose...", options=options)
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author: return
        mode = self.values[0]
        lobby_id = generate_lobby_id()
        
        # تخزين اللوبي في الذاكرة
        active_lobbies[lobby_id] = {
            "host": interaction.user.id,
            "mode": mode,
            "players": [interaction.user.id],
            "created_at": datetime.datetime.now(),
            "channel_id": interaction.channel.id,
            "started": False,
            "warned": False
        }

        embed = discord.Embed(
            title="✅ Lobby Created!",
            description=f"Type: **{mode}**\nID: `{lobby_id}`\n\nاللوبي جاهز الآن في قائمة الانتظار.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class LobbyCreateView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=60)
        self.author = author
        self.add_item(LobbySelectMenu(author))

    async def on_timeout(self):
        # الصورة الثالثة (انتهاء الوقت)
        try:
            embed = discord.Embed(description="❌ **Lobby creation timed out.**", color=discord.Color.red())
            await self.message.edit(content=None, embed=embed, view=None)
        except: pass

@bot.command()
async def l(ctx):
    # 1. فحص الروم
    if ctx.channel.name != "matchmaking-general":
        return await ctx.send("❌ هذا الأمر مخصص لغرفة الماتش ميكنق فقط (#matchmaking-general).")

    # 2. فحص الرتبة
    if not discord.utils.get(ctx.author.roles, name="Verified Player"):
        return await ctx.send("❌ يجب أن تكون لاعب موثق (Verified Player) لتتمكن من إنشاء لوبي.")

    # 3. فحص عدد اللوبيات المنشأة (بحد أقصى 2)
    user_lobbies = [lid for lid, l in active_lobbies.items() if l['host'] == ctx.author.id]
    if len(user_lobbies) >= 2:
        return await ctx.send("❌ Rejected: You already have 2 active lobbies.")

    # 4. إرسال القائمة
    embed = discord.Embed(title="🎮 Select Lobby Category", description="Choose the gamemode below:", color=discord.Color.blue())
    view = LobbyCreateView(ctx.author)
    view.message = await ctx.send(embed=embed, view=view)

# أمر إنهاء اللوبي
@bot.command()
async def l_end(ctx, lobby_id: str = None):
    # التحقق إذا كان الشخص Mod يقدر ينهي أي لوبي بالـ ID
    is_mod = any(r.name == 'Mod' for r in ctx.author.roles)
    
    if is_mod and lobby_id:
        if lobby_id in active_lobbies:
            del active_lobbies[lobby_id]
            return await ctx.send(f"✅ Lobby `{lobby_id}` has been terminated by Mod.")
        else:
            return await ctx.send("❌ Lobby ID not found.")

    # إذا كان لاعب عادي يبي ينهي اللوبي (يحتاج تصويت أو وقت)
    # سيتم إضافة تفاصيل التصويت 6 أشخاص هنا في التحديث القادم
    await ctx.send("⚠️ نظام التصويت قيد البرمجة، حالياً اطلب من Mod الإنهاء.")
# --- دالة فحص اكتمال بيانات اللاعب ---
async def check_player_data(member):
    data = load_data().get(str(member.id), {})
    missing = []
    if not data.get('psn'): missing.append("PSN (!set_psn)")
    if not data.get('country'): missing.append("Country Flag (!set_flag)")
    if not data.get('ranked_name'): missing.append("Ranked Name (!set_ranked_name)")
    return missing

class LobbyJoinView(discord.ui.View):
    def __init__(self, lobby_id):
        super().__init__(timeout=None) # يبقى شغال لين ينتهي اللوبي
        self.lobby_id = lobby_id

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="join_btn")
    async def join(self, interaction: discord.Interaction):
        lobby = active_lobbies.get(self.lobby_id)
        if not lobby: return await interaction.response.send_message("Lobby expired.", ephemeral=True)

        # 1. فحص البيانات الناقصة
        missing = await check_player_data(interaction.user)
        if missing:
            # إرسال تنبيه في روم matchmaking-notifications كما طلبت بالصورة
            notif_channel = discord.utils.get(interaction.guild.channels, name="matchmaking-notifications")
            if notif_channel:
                msg = f"⚠️ {interaction.user.mention}, you can't join. Missing: {', '.join(missing)}"
                await notif_channel.send(msg)
            return await interaction.response.send_message("بياناتك ناقصة! شيك على قسم التنبيهات.", ephemeral=True)

        # 2. فحص إذا كان في فريق أو شريك (لأطوار Duo/3v3/4v4)
        # (هنا يتم التحقق من الـ Partner اللي سويناه في !set_partner)
        if interaction.user.id in lobby['players']:
            return await interaction.response.send_message("أنت موجود بالفعل في اللوبي.", ephemeral=True)

        lobby['players'].append(interaction.user.id)
        await interaction.response.edit_message(content=f"اللاعبين الحاليين: {len(lobby['players'])}")

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, custom_id="leave_btn")
    async def leave(self, interaction: discord.Interaction):
        lobby = active_lobbies.get(self.lobby_id)
        if interaction.user.id in lobby['players']:
            lobby['players'].remove(interaction.user.id)
            await interaction.response.edit_message(content=f"اللاعبين الحاليين: {len(lobby['players'])}")
        else:
            await interaction.response.send_message("أنت لست في اللوبي.", ephemeral=True)
# تعديل بسيط لربط الفرق بالأطوار
@bot.command()
async def set_partner(ctx, partner: discord.Member):
    # فحص إذا كان اللاعب في طور Duo أصلاً
    # (هنا نضع منطق المنشن والرياكشن اللي أرسلته لك فوق)
    # ملاحظة: أضف شرط أن هذا لا يعمل إلا لطور Duo فقط
    pass

@bot.command()
async def set_team(ctx, p1: discord.Member, p2: discord.Member, p3: discord.Member = None):
    # هذا الأمر لا يعمل في Duo
    # يرسل التنبيهات ويطلب ✅ من الجميع خلال دقيقة
    pass
@bot.command()
async def duo(ctx):
    # فحص إذا كان اللاعب متبند
    if any(role.name == "Ranked Banned" for role in ctx.author.roles):
        await ctx.send(f"❌ {ctx.author.mention}, you are banned from Ranked and cannot use this command.")
        return
    
    # هنا كمل كود الـ duo حقك الطبيعي...
    await ctx.send("✅ Duo queue started...")  
    
# ==========================================
# (8) منطقة إضافة الكوماندات الجديدة - أضف هنا مستقبلاً
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
    bot.run(os.getenv("DISCORD_TOKEN"))
