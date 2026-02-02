import discord
from discord.ext import commands, tasks
import random
import asyncio
import os
from datetime import datetime, timedelta

# إعدادات البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# معرف قناة الإشعارات (استبدل الرقم بالـ ID الحقيقي لقناتك)
NOTIF_CHANNEL_ID = 123456789012345678 

TRACKS = [
    "Crash Cove", "Roo's Tubes", "Mystery Caves", "Sewer Speedway", "Coco Park",
    "Tiger Temple", "Papu's Pyramid", "Dingo Canyon", "Blizzard Bluff", "Dragon Mines",
    "Polar Pass", "Tiny Arena", "N. Gin Labs", "Cortex Castle", "Hot Air Skyway",
    "Oxide Station", "Slide Coliseum", "Turbo Track", "Inferno Island", "Jungle Boogie",
    "Tiny Temple", "Meteor Gorge", "Barin Ruins", "Deep Sea Driving", "Out of Time",
    "Assembly Lane", "Android Alley", "Electron Avenue", "Thunder Struck", "Clockwork Wumpa",
    "Twilight Tour", "Prehistoric Playground", "Spyro Circuit", "Nina's Nightmare",
    "Koala Kong Circus", "Gingerbread Joyride", "Megamix Mania", "Drive-Thru Danger", "Retro Stadium"
]

class LobbyView(discord.ui.View):
    def __init__(self, limit, mode, creator):
        super().__init__(timeout=3600) # ساعة كاملة
        self.limit = limit
        self.mode = mode
        self.creator = creator
        self.participants = []
        self.lobby_id = f"{random.getrandbits(64):x}"[:20]
        self.warning_sent = False

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="✅")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.participants:
            if len(self.participants) < self.limit:
                self.participants.append(interaction.user)
                await self.update_message(interaction)
                if len(self.participants) == self.limit:
                    await self.start_lobby(interaction)
            else:
                await interaction.response.send_message("Lobby is full!", ephemeral=True)
        else:
            await interaction.response.send_message("You are already in!", ephemeral=True)

    async def update_message(self, interaction):
        player_list = "\n".join([f"{i+1}. {p.mention}" for i, p in enumerate(self.participants)])
        embed = discord.Embed(
            title=f"Gathering Ranked {self.mode.upper()} Lobby",
            description=f"**Ruleset:** Standard\n**Players ({len(self.participants)} / {self.limit})**\n\n**Players:**\n{player_list}",
            color=0xff00ff
        )
        embed.set_footer(text=f"id: {self.lobby_id}")
        await interaction.response.edit_message(embed=embed, view=self)

    async def start_lobby(self, interaction):
        self.stop()
        selected_tracks = random.sample(TRACKS, 8)
        tracks_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(selected_tracks)])
        score_temp = "\n".join([f"{p.name} [0|0|0|0|0|0|0|0]" for p in self.participants])
        
        embed = discord.Embed(
            title=f"The Ranked {self.mode.upper()} Lobby has started",
            description=f"**Tracks:**\n{tracks_text}\n\n**Score Template:**\n```\nLobby #{random.randint(100,999)}\n{score_temp}```",
            color=0x2ecc71
        )
        await interaction.channel.send(content=f"Attention: {', '.join([p.mention for p in self.participants])}", embed=embed)

@bot.command(name="l")
async def lobby(ctx, mode="ffa"):
    modes = {"ffa": 8, "duo": 8, "3v3": 6, "4v4": 8, "itemless": 4}
    limit = modes.get(mode.lower(), 8)
    
    view = LobbyView(limit, mode, ctx.author)
    await ctx.send(f"Ranked {mode.upper()} Lobby [Full RNG Tracks] has been created. Don't forget to click on the ✅ button!")
    
    embed = discord.Embed(
        title=f"Gathering Ranked {mode.upper()} Lobby",
        description=f"**Ruleset:** Standard\n**Players (0 / {limit})**\n\nWaiting for players...",
        color=0xff00ff
    )
    embed.set_footer(text=f"id: {view.lobby_id}")
    lobby_msg = await ctx.send(embed=embed, view=view)

    # نظام التنبيه والحذف (55 دقيقة للتحذير، 60 دقيقة للحذف)
    await asyncio.sleep(3300) # 55 دقيقة
    if len(view.participants) < limit:
        notif_channel = bot.get_channel(NOTIF_CHANNEL_ID)
        mentions = ", ".join([p.mention for p in view.participants])
        
        # رسالة Warning
        warn_embed = discord.Embed(title="⚠️ Warning!", 
            description=f"Your lobby `{view.lobby_id}` will be deleted in 5 minutes if it will not be started.", color=0xf1c40f)
        await notif_channel.send(content=mentions, embed=warn_embed)
        
        await asyncio.sleep(300) # 5 دقائق إضافية
        if len(view.participants) < limit:
            # رسالة Delete
            del_embed = discord.Embed(title="ℹ️ Info", 
                description=f"Your lobby `{view.lobby_id}` has been deleted because it wasn't started in an hour.", color=0x3498db)
            await notif_channel.send(content=mentions, embed=del_embed)
            await lobby_msg.delete()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction("⚠️")

bot.run(os.getenv("TOKEN"))
