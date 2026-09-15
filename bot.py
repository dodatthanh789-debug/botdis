import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"cash": 10000, "slots": 30, "fish": [], "last_daily": ""}
    return user_data[user_id]

SHOP_ITEMS = {
    "can_tre": {"name": "Cần tre", "price": 10000, "type": "rod"},
    "can_thep_ren": {"name": "Cần thép ren", "price": 50000, "type": "rod"},
    "can_xuyen_thien_quy": {"name": "Cần xuyên thiên quy", "price": 100000, "type": "rod"},
    "can_quan_tri": {"name": "Cần quản trị", "price": 5000000, "type": "rod"},
    "balo_binh_thuong": {"name": "Balo bình thường", "price": 30000, "type": "bag", "slots": 30},
    "balo_da": {"name": "Balo da", "price": 45000, "type": "bag", "slots": 45},
    "balo_quy_toc": {"name": "Balo quý tộc", "price": 67000, "type": "bag", "slots": 67},
    "balo_thien_ha": {"name": "Balo thiên hà", "price": 90000, "type": "bag", "slots": 90},
    "balo_quan_tri": {"name": "Balo quản trị", "price": 99999999999, "type": "bag", "slots": 999999},
}

@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng hoạt động!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu tham số. Dùng `!help` để xem lệnh.")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Tham số không hợp lệ.")
        return
    print(f"Lỗi: {error}")

@bot.command(name="usecash")
async def usecash(ctx):
    data = get_user(ctx.author.id)
    await ctx.send(f"💵 **{ctx.author.name}**, số dư: **{data['cash']:,} VNĐ**")

@bot.command(name="usadaily")
async def usadaily(ctx):
    data = get_user(ctx.author.id)
    reward = 50000
    data["cash"] += reward
    await ctx.send(f"🎉 {ctx.author.mention} nhận **{reward:,} VNĐ**!")

@bot.command(name="usafish")
async def usafish(ctx):
    data = get_user(ctx.author.id)
    if len(data["fish"]) >= data["slots"]:
        await ctx.send(f"❌ Balo đầy ({data['slots']} ô)!")
        return
    caught = random.choice(["Cá rô phi", "Cá chép vàng", "Cá mập con", "Tôm hùm", "Cá voi xanh"])
    data["fish"].append(caught)
    await ctx.send(f"🎣 {ctx.author.mention} bắt được **{caught}**! Balo: {len(data['fish'])}/{data['slots']}")

@bot.command(name="usafinv")
async def usafinv(ctx):
    data = get_user(ctx.author.id)
    fish_list = ", ".join(data["fish"]) if data["fish"] else "Trống rỗng"
    embed = discord.Embed(title=f"🎒 Balo của {ctx.author.name}", color=discord.Color.blue())
    embed.add_field(name="Sức chứa", value=f"{len(data['fish'])} / {data['slots']} ô", inline=False)
    embed.add_field(name="Cá đã câu", value=fish_list[:1024], inline=False)
    await ctx.send(embed=embed)

@bot.command(name="usashop")
async def usashop(ctx):
    embed = discord.Embed(title="🛒 Cửa hàng", description="Dùng `!usabuy <mã_item>` để mua.", color=discord.Color.gold())
    for key, item in SHOP_ITEMS.items():
        desc = f"Giá: {item['price']:,} VNĐ"
        if item["type"] == "bag":
            desc += f" | Sức chứa: {item['slots']} ô"
        embed.add_field(name=f"{item['name']} (`{key}`)", value=desc, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="usabuy")
async def usabuy(ctx, item_key: str = None):
    if not item_key or item_key.lower() not in SHOP_ITEMS:
        await ctx.send("❌ Mã vật phẩm không đúng. Dùng `!usashop`.")
        return
    item_key = item_key.lower()
    data = get_user(ctx.author.id)
    item = SHOP_ITEMS[item_key]
    if data["cash"] < item["price"]:
        await ctx.send(f"❌ Không đủ tiền. Bạn có **{data['cash']:,} VNĐ**, cần **{item['price']:,} VNĐ**.")
        return
    data["cash"] -= item["price"]
    if item["type"] == "bag":
        data["slots"] = item["slots"]
        await ctx.send(f"🎉 Đã mua **{item['name']}**! Balo: **{item['slots']} ô**.")
    else:
        await ctx.send(f"🎉 Đã sở hữu **{item['name']}**!")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="🎮 BOTDIS - LỆNH", color=discord.Color.green())
    embed.add_field(name="💰 Tiền", value="`!usecash`\n`!usadaily`", inline=False)
    embed.add_field(name="🎣 Câu cá", value="`!usafish`\n`!usafinv`", inline=False)
    embed.add_field(name="🛒 Shop", value="`!usashop`\n`!usabuy <mã>`", inline=False)
    await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Chưa có DISCORD_TOKEN. Hãy đặt token bot vào biến môi trường DISCORD_TOKEN.")

bot.run(TOKEN)
