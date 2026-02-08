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
    
@bot.command(aliases=['p'])
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    # 1. تحميل البيانات
    data = load_data()
    user_id = str(member.id)
    
    # 2. جلب بيانات اللاعب أو وضع قيم افتراضية إذا كان جديد
    user_data = data.get(user_id, {})
    
    pts = user_data.get('points', 1200) # القيمة الافتراضية 1200
    psn = user_data.get('psn', 'Not Set')
    flag = user_data.get('country', '🏳️')
    r_name = user_data.get('ranked_name', 'Not Set')
    nat = user_data.get('nat_type', 'Unknown')

    # 3. بناء الإمبيد (Embed) بشكل مرتب
    embed = discord.Embed(
        title=f"{flag} {member.display_name}'s Profile", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    embed.add_field(name="📊 MMR Points", value=f"**[{pts}]**", inline=False)
    embed.add_field(name="🎮 PSN ID", value=psn, inline=True)
    embed.add_field(name="📛 Ranked Name", value=r_name, inline=True)
    embed.add_field(name="📡 NAT Type", value=nat, inline=True)
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    
    await ctx.send(embed=embed)

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
@bot.command()
async def update_scores(ctx, member: discord.Member, amount: str):
    # مسموح للـ Mods فقط
    if not any(r.name == 'Mod' for r in ctx.author.roles):
        return await ctx.send("❌ This command is for **Mods** only.")
    
    data = load_data()
    uid = str(member.id)
    if uid not in data: data[uid] = {"points": 1200}
    
    current_pts = data[uid].get('points', 1200)
    
    # حساب النقاط الجديدة (مثال: +60 أو -60)
    try:
        if amount.startswith('+'):
            new_pts = current_pts + int(amount[1:])
        elif amount.startswith('-'):
            new_pts = current_pts - int(amount[1:])
        else:
            new_pts = int(amount)
            
        data[uid]['points'] = max(1, new_pts) # لا ينقص عن 1
        save_data(data)
        await ctx.send(f"✅ Updated {member.display_name}'s score to **[{data[uid]['points']}]**")
    except:
        await ctx.send("❌ Error: Use format like !update_scores @user +60")

# ==========================================
# (7) منطقة اللوبيات - أضف هنا مستقبلاً
# ==========================================
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
    "🇴🇲": "om", "🇪🇬": "eg", "🇩🇿": "dz", "🇲🇦": "ma" # أضف البقية هنا بنفس النمط
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
            color=discord.Color.blue()
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
    bot.run(os.getenv("TOKEN"))
