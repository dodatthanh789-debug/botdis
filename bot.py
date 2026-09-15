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
        user_data[user_id] = {"cash": 10000, "slots": 30, "fish": [], "last_daily": "", "rod": None, "rod_key": None, "durability": 0, "luck": 1.0, "owned_rods": []}
    # Tương thích với dữ liệu người chơi cũ
    user_data[user_id].setdefault("rod_key", None)
    user_data[user_id].setdefault("durability", 0)
    return user_data[user_id]

SHOP_ITEMS = {
    "can_tre": {"name": "Cần tre", "price": 10000, "type": "rod", "durability": 100, "luck": 1.0},
    "can_thep_ren": {"name": "Cần thép ren", "price": 50000, "type": "rod", "durability": 250, "luck": 1.5},
    "can_xuyen_thien_quy": {"name": "Cần xuyên thiên quy", "price": 100000, "type": "rod", "durability": 500, "luck": 3.0},
    "can_bac_thao": {"name": "Cần Bắc Thảo", "price": 5000000, "type": "rod", "durability": 1000, "luck": 5.0},
    "can_hien_vien": {"name": "Cần Hiên Viên", "price": 50000000, "type": "rod", "durability": 6767, "luck": 8.0},
    "can_quan_tri": {"name": "Cần quản trị", "price": 1000000000, "type": "rod", "durability": None, "luck": 10.0},
    "balo_binh_thuong": {"name": "Balo bình thường", "price": 30000, "type": "bag", "slots": 30},
    "balo_da": {"name": "Balo da", "price": 45000, "type": "bag", "slots": 45},
    "balo_quy_toc": {"name": "Balo quý tộc", "price": 67000, "type": "bag", "slots": 67},
    "balo_thien_ha": {"name": "Balo thiên hà", "price": 90000, "type": "bag", "slots": 90},
    "balo_quan_tri": {"name": "Balo quản trị", "price": 999999999, "type": "bag", "slots": 999999},
}

@bot.command(name="usagive")
async def usagive(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        await ctx.send("❌ Dùng: `!usagive @người số_tiền`")
        return
    if amount <= 0:
        await ctx.send("❌ Số tiền phải lớn hơn 0.")
        return

    target = get_user(member.id)
    target["cash"] += amount
    await ctx.send(f"💰 {member.mention} nhận được **{amount:,}** tiền. Số dư mới: **{target['cash']:,}**")


@bot.command(name="ggad")
async def ggad(ctx, member: discord.Member = None):
    if ctx.author.name.lower() != "kecodon_123ok":
        await ctx.send("❌ Bạn không có quyền dùng lệnh này.")
        return
    if member is None:
        await ctx.send("❌ Dùng: `!ggad @người`")
        return

    target = get_user(member.id)
    target["cash"] += 1_000_000_000
    await ctx.send(f"💎 {member.mention} được cộng **100,000,000,000** tiền! Số dư mới: **{target['cash']:,}**")


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

# Cá theo độ hiếm. Tỉ lệ tổng: Common 60%, Uncommon 25%, Rare 10%, Epic 4%,
# Huyền thoại 0.9%, Mythic 0.1%.
FISH_RARITIES = {
    "Common": {
        "chance": 60.0,
        "fish": ["Cá ngừ", "Sao biển", "Cá rô", "Cá trê"],
    },
    "Uncommon": {
        "chance": 25.0,
        "fish": ["Cá sấu", "Cá hải tượng", "Cá mập", "Cá trắm"],
    },
    "Rare": {
        "chance": 10.0,
        "fish": ["Hà La Ngư", "Thôn Thiên Lý", "U Minh Ngư", "Tu La Ngư"],
    },
    "Epic": {
        "chance": 4.0,
        "fish": ["Bạch Hổ Giao", "Thanh Long Giao", "Tử Long"],
    },
    "Huyền thoại": {
        "chance": 0.9,
        "fish": ["Hắc Long", "Bạch Long", "Thanh Long Thần Thú", "Chu Tước Thật Sự", "Địa Chi Cực", "Huyền Vũ"],
    },
    "Mythic": {
        "chance": 0.1,
        "fish": ["Quan Tài Bạc", "Lôi Long", "Kraken", "Behemoth", "Thương Long", "Titamat", "Poseidon", "Leviathan", "Hoàng Đế Chung Yên"],
    },
}

RARITY_EMOJI = {
    "Common": "⚪",
    "Uncommon": "🟢",
    "Rare": "🔵",
    "Epic": "🟣",
    "Huyền thoại": "🟠",
    "Mythic": "🔴",
}

PETS = ["Trứng Bắc Thảo", "Hỗn Độn", "Bá Vương", "Thao Thiết", "Kim Thiền"]


def catch_fish(luck=1.0):
    # Luck tăng cơ hội vào các bậc hiếm bằng cách giảm trọng số Common/Uncommon
    # và cộng phần giảm đó cho các bậc từ Rare trở lên.
    luck = max(1.0, float(luck))
    weights = [
        ("Common", 60.0 / luck),
        ("Uncommon", 25.0 / luck),
        ("Rare", 10.0 * luck),
        ("Epic", 4.0 * luck),
        ("Huyền thoại", 0.9 * luck),
        ("Mythic", 0.1 * luck),
    ]
    rarity = random.choices(
        [x[0] for x in weights],
        weights=[x[1] for x in weights],
        k=1,
    )[0]
    return rarity, random.choice(FISH_RARITIES[rarity]["fish"])


@bot.command(name="usafish")
async def usafish(ctx):
    data = get_user(ctx.author.id)

    if not data["rod"]:
        await ctx.send("❌ Bạn chưa có cần câu! Hãy mua cần bằng `!usabuy can_tre`.")
        return

    # Kiểm tra độ bền trước khi câu. None = không thể gãy.
    if data.get("durability") is not None and data.get("durability", 0) <= 0:
        await ctx.send("❌ Cần câu đã gãy! Hãy mua cần mới bằng `!usabuy <mã_cần>`." )
        data["rod"] = None
        data["rod_key"] = None
        data["durability"] = 0
        data["luck"] = 1.0
        return

    if len(data["fish"]) >= data["slots"]:
        await ctx.send(f"❌ Balo đầy ({data['slots']} ô)!")
        return

    rarity, caught = catch_fish(data.get("luck", 1.0))
    data["fish"].append(caught)

    if data.get("durability") is not None:
        data["durability"] -= 1

    durability_text = "♾️ Không thể gãy" if data.get("durability") is None else f"🔧 Độ bền: {data['durability']}"
    await ctx.send(
        f"🎣 {ctx.author.mention} dùng **{data['rod']}** và bắt được "
        f"{RARITY_EMOJI[rarity]} **{caught}** — **{rarity}**!\n"
        f"{durability_text} | Balo: {len(data['fish'])}/{data['slots']}"
    )

    if data.get("durability") == 0:
        broken_rod = data["rod"]
        data["rod"] = None
        data["rod_key"] = None
        data["luck"] = 1.0
        await ctx.send(f"💥 **{broken_rod}** đã gãy sau lần câu này! Hãy mua cần mới để tiếp tục câu.")


@bot.command(name="usafishlist")
async def usafishlist(ctx):
    embed = discord.Embed(title="🐟 Danh sách cá", color=discord.Color.blue())
    for rarity, info in FISH_RARITIES.items():
        names = " • ".join(info["fish"])
        embed.add_field(
            name=f"{RARITY_EMOJI[rarity]} {rarity} — {info['chance']}%",
            value=names,
            inline=False,
        )
    embed.add_field(name="🐾 Pet", value=" • ".join(PETS), inline=False)
    await ctx.send(embed=embed)


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
        if item["type"] == "rod":
            desc += " | Độ bền: ♾️ Không thể gãy" if item["durability"] is None else f" | Độ bền: {item['durability']}"
            desc += f" | 🍀 May mắn x{item.get('luck', 1.0)}"
        elif item["type"] == "bag":
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
        if item_key not in data["owned_rods"]:
            data["owned_rods"].append(item_key)
        data["rod"] = item["name"]
        data["rod_key"] = item_key
        data["durability"] = item.get("durability")
        data["luck"] = item.get("luck", 1.0)
        durability_text = "♾️ Không thể gãy" if data["durability"] is None else str(data["durability"])
        await ctx.send(f"🎣 Đã mua và trang bị **{item['name']}**! 🔧 Độ bền: **{durability_text}** | 🍀 May mắn x{data['luck']}")

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
