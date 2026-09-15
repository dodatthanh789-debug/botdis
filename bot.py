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
        user_data[user_id] = {"cash": 10000, "slots": 30, "fish": [], "last_daily": 0, "rod": None, "rod_key": None, "durability": 0, "luck": 1.0, "owned_rods": [], "pets": []}
    # Tương thích với dữ liệu người chơi cũ
    user_data[user_id].setdefault("rod_key", None)
    user_data[user_id].setdefault("durability", 0)
    user_data[user_id].setdefault("pets", [])
    user_data[user_id].setdefault("owned_rods", [])
    user_data[user_id].setdefault("cash", 10000)
    user_data[user_id].setdefault("slots", 30)
    user_data[user_id].setdefault("fish", [])
    user_data[user_id].setdefault("last_daily", 0)
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
    "balo_quan_tri": {"name": "Balo quản trị", "price": 99999999999, "type": "bag", "slots": 999999},
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
    await ctx.send(f"💎 {member.mention} được cộng **1,000,000,000** tiền! Số dư mới: **{target['cash']:,}**")


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
    import time
    data = get_user(ctx.author.id)
    now = time.time()
    last = data.get("last_daily", 0)

    # Chỉ nhận 1 lần trong mỗi 24 giờ
    if isinstance(last, str):
        try:
            last = float(last)
        except (ValueError, TypeError):
            last = 0

    cooldown = 24 * 60 * 60
    remaining = cooldown - (now - last)

    if remaining > 0:
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await ctx.send(
            f"⏳ {ctx.author.mention}, bạn đã nhận điểm danh rồi! "
            f"Hãy quay lại sau **{hours} giờ {minutes} phút**."
        )
        return

    reward = 50000
    data["cash"] += reward
    data["last_daily"] = now
    await ctx.send(
        f"🎉 {ctx.author.mention} nhận **{reward:,} VNĐ**! "
        f"⏰ Lần nhận tiếp theo sau 24 giờ."
    )

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



# Giá bán cá theo độ hiếm
FISH_SELL_PRICES = {
    "Common": 500,
    "Uncommon": 2000,
    "Rare": 10000,
    "Epic": 50000,
    "Huyền thoại": 250000,
    "Mythic": 1000000,
}

FISH_TO_RARITY = {
    fish_name: rarity
    for rarity, info in FISH_RARITIES.items()
    for fish_name in info["fish"]
}

@bot.command(name="usaban")
async def usaban(ctx, fish_name: str = None):
    """Bán cá. Dùng !usaban <tên cá> hoặc !usaban all để bán toàn bộ."""
    data = get_user(ctx.author.id)

    if not data["fish"]:
        await ctx.send("❌ Balo cá đang trống, không có cá để bán.")
        return

    if fish_name is None:
        await ctx.send("❌ Dùng: `!usaban <tên cá>` hoặc `!usaban all`.")
        return

    # Hỗ trợ bán toàn bộ
    if fish_name.lower() == "all":
        total = 0
        sold = 0
        for fish in data["fish"]:
            rarity = FISH_TO_RARITY.get(fish)
            if rarity:
                total += FISH_SELL_PRICES.get(rarity, 0)
                sold += 1

        data["fish"].clear()
        data["cash"] += total
        await ctx.send(
            f"💰 {ctx.author.mention} đã bán **{sold} con cá** và nhận "
            f"**{total:,} VNĐ**!\n💵 Số dư: **{data['cash']:,} VNĐ**"
        )
        return

    # Tìm tên cá không phân biệt hoa/thường
    wanted = fish_name.strip().lower()
    found_index = next(
        (i for i, fish in enumerate(data["fish"]) if fish.lower() == wanted),
        None
    )

    if found_index is None:
        await ctx.send(f"❌ Bạn không có cá **{fish_name}** trong balo.")
        return

    caught = data["fish"].pop(found_index)
    rarity = FISH_TO_RARITY.get(caught)

    if rarity is None:
        await ctx.send("❌ Loại cá này chưa có giá bán.")
        data["fish"].append(caught)
        return

    price = FISH_SELL_PRICES[rarity]
    data["cash"] += price

    await ctx.send(
        f"💰 {ctx.author.mention} đã bán **{caught}** "
        f"({RARITY_EMOJI[rarity]} {rarity}) được **{price:,} VNĐ**!\n"
        f"🎒 Balo: **{len(data['fish'])}/{data['slots']}** ô | "
        f"💵 Số dư: **{data['cash']:,} VNĐ**"
    )

@bot.command(name="usabangia")
async def usabangia(ctx):
    """Xem bảng giá bán cá."""
    embed = discord.Embed(
        title="💰 BẢNG GIÁ BÁN CÁ",
        description="Dùng `!usaban <tên cá>` hoặc `!usaban all`.",
        color=discord.Color.gold()
    )
    for rarity, info in FISH_RARITIES.items():
        price = FISH_SELL_PRICES[rarity]
        embed.add_field(
            name=f"{RARITY_EMOJI[rarity]} {rarity}",
            value=f"**{price:,} VNĐ/con**\n" + " • ".join(info["fish"]),
            inline=False
        )
    await ctx.send(embed=embed)


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


class SellFishSelect(discord.ui.Select):
    def __init__(self, owner_id, fish_options):
        self.owner_id=owner_id
        options=[]
        for fish_name,count in fish_options[:25]:
            rarity=FISH_TO_RARITY.get(fish_name,"Common")
            price=FISH_SELL_PRICES.get(rarity,0)
            options.append(discord.SelectOption(label=fish_name[:100], description=f"{count} con | {price:,} VNĐ/con", value=fish_name))
        super().__init__(placeholder="🐟 Chọn cá muốn bán...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Đây không phải balo của bạn.", ephemeral=True)
        data=get_user(self.owner_id); fish=self.values[0]; count=data["fish"].count(fish)
        if count<=0: return await interaction.response.send_message("❌ Cá này không còn trong balo.", ephemeral=True)
        rarity=FISH_TO_RARITY.get(fish,"Common"); price=FISH_SELL_PRICES[rarity]
        view=SellQuantityView(self.owner_id,fish,count,price)
        await interaction.response.send_message(f"🐟 **{fish}** — đang có **{count} con**.\n💰 Giá: **{price:,} VNĐ/con**\n\nChọn số lượng muốn bán:",view=view,ephemeral=True)

class SellQuantitySelect(discord.ui.Select):
    def __init__(self, owner_id, fish, max_count, price):
        self.owner_id=owner_id; self.fish=fish; self.max_count=max_count; self.price=price
        opts=[discord.SelectOption(label=f"{n} con",description=f"Nhận {n*price:,} VNĐ",value=str(n)) for n in range(1,min(max_count,25)+1)]
        super().__init__(placeholder="🔢 Chọn số lượng...",min_values=1,max_values=1,options=opts)
    async def callback(self, interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Đây không phải balo của bạn.",ephemeral=True)
        data=get_user(self.owner_id); actual=data["fish"].count(self.fish); qty=min(int(self.values[0]),actual)
        for _ in range(qty): data["fish"].remove(self.fish)
        total=qty*self.price; data["cash"]+=total
        await interaction.response.edit_message(content=f"✅ Đã bán **{qty} con {self.fish}**!\n💰 Nhận: **{total:,} VNĐ**\n🎒 Còn: **{data['fish'].count(self.fish)} con**\n💵 Số dư: **{data['cash']:,} VNĐ**",view=None)

class SellQuantityModal(discord.ui.Modal, title="💰 Bán cá"):
    quantity = discord.ui.TextInput(
        label="Số lượng muốn bán",
        placeholder="Nhập số lượng, ví dụ: 37",
        required=True,
        min_length=1,
        max_length=10
    )

    def __init__(self, owner_id, fish_name, max_count, price):
        super().__init__()
        self.owner_id = owner_id
        self.fish_name = fish_name
        self.max_count = max_count
        self.price = price

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )
            return

        try:
            quantity = int(str(self.quantity.value).strip())
        except ValueError:
            await interaction.response.send_message(
                "❌ Số lượng phải là số nguyên.", ephemeral=True
            )
            return

        if quantity <= 0:
            await interaction.response.send_message(
                "❌ Số lượng phải lớn hơn 0.", ephemeral=True
            )
            return

        data = get_user(self.owner_id)
        actual_count = data["fish"].count(self.fish_name)

        if actual_count <= 0:
            await interaction.response.send_message(
                "❌ Cá này không còn trong balo.", ephemeral=True
            )
            return

        if quantity > actual_count:
            await interaction.response.send_message(
                f"❌ Bạn chỉ có **{actual_count} con {self.fish_name}** trong balo.",
                ephemeral=True
            )
            return

        for _ in range(quantity):
            data["fish"].remove(self.fish_name)

        total = quantity * self.price
        data["cash"] += total

        await interaction.response.send_message(
            f"✅ Đã bán **{quantity} con {self.fish_name}**!\n"
            f"💰 Nhận được: **{total:,} VNĐ**\n"
            f"🎒 Còn lại: **{data['fish'].count(self.fish_name)} con**\n"
            f"💵 Số dư: **{data['cash']:,} VNĐ**"
        )


class SellQuantityView(discord.ui.View):
    def __init__(self, owner_id, fish_name, max_count, price):
        super().__init__(timeout=120)
        self.owner_id = owner_id
        self.fish_name = fish_name
        self.max_count = max_count
        self.price = price

    @discord.ui.button(label="🔢 Nhập số lượng", style=discord.ButtonStyle.blurple)
    async def quantity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            SellQuantityModal(
                self.owner_id,
                self.fish_name,
                self.max_count,
                self.price
            )
        )

class SellFishView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=120); self.owner_id=owner_id
    @discord.ui.button(label="💰 Bán cá", style=discord.ButtonStyle.green)
    async def sell_button(self, interaction, button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Đây không phải balo của bạn.",ephemeral=True)
        data=get_user(self.owner_id)
        if not data["fish"]: return await interaction.response.send_message("❌ Balo cá đang trống.",ephemeral=True)
        counts={}
        for fish in data["fish"]: counts[fish]=counts.get(fish,0)+1
        view=discord.ui.View(timeout=120); view.add_item(SellFishSelect(self.owner_id,list(counts.items())))
        await interaction.response.send_message("🐟 **CHỌN CÁ MUỐN BÁN**\nChọn loại cá, sau đó chọn số lượng.",view=view,ephemeral=True)

@bot.command(name="usafinv")
async def usafinv(ctx):
    data = get_user(ctx.author.id)

    fish_list = ", ".join(data["fish"]) if data["fish"] else "Trống rỗng"

    # Thông tin cần câu
    if data.get("rod"):
        rod_name = data["rod"]
        durability = data.get("durability")
        rod_luck = data.get("luck", 1.0)
        durability_text = "♾️ Không thể gãy" if durability is None else f"{durability}"
        rod_text = (
            f"🎣 **{rod_name}**\n"
            f"🔧 Độ bền: **{durability_text}**\n"
            f"🍀 May mắn: **x{rod_luck}**"
        )
    else:
        rod_text = "❌ Chưa có cần câu"

    # Thông tin pet
    pets = data.get("pets", [])
    pet_text = ", ".join(pets) if pets else "❌ Chưa có pet"

    embed = discord.Embed(
        title=f"🎒 BALO CỦA {ctx.author.name}",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🐟 Cá",
        value=f"{len(data['fish'])} / {data['slots']} ô\n{fish_list[:1000]}",
        inline=False
    )
    embed.add_field(name="🎣 Cần đang trang bị", value=rod_text, inline=False)
    embed.add_field(name="🐾 Pet đang có", value=pet_text[:1024], inline=False)
    embed.add_field(name="💵 Tiền", value=f"{data['cash']:,} VNĐ", inline=False)

    await ctx.send(embed=embed, view=SellFishView(ctx.author.id))


@bot.command(name="usapet")
async def usapet(ctx):
    """Xem pet đang sở hữu."""
    data = get_user(ctx.author.id)
    pets = data.get("pets", [])

    embed = discord.Embed(title=f"🐾 PET CỦA {ctx.author.name}", color=discord.Color.purple())
    if pets:
        embed.description = "\n".join(f"🐾 {pet}" for pet in pets)
    else:
        embed.description = "Bạn chưa có pet."
    await ctx.send(embed=embed)

@bot.command(name="usapetadd")
async def usapetadd(ctx, *, pet_name: str = None):
    """Thêm pet để test/admin. Không mở quyền admin cho người dùng thường."""
    if ctx.author.name.lower() != "kecodon_123ok":
        await ctx.send("❌ Bạn không có quyền dùng lệnh này.")
        return
    if not pet_name:
        await ctx.send("❌ Dùng: `!usapetadd <tên pet>`")
        return
    if pet_name not in PETS:
        await ctx.send("❌ Pet không hợp lệ. Dùng `!usapet` để xem danh sách.")
        return

    data = get_user(ctx.author.id)
    data["pets"].append(pet_name)
    await ctx.send(f"🐾 Đã thêm pet **{pet_name}** vào balo của bạn.")


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
    embed.add_field(name="🎣 Câu cá", value="`!usafish`\n`!usafinv` (có nút bán cá)\n`!usaban <tên cá>`\n`!usaban all`\n`!usabangia`\n`!usapet`", inline=False)
    embed.add_field(name="🛒 Shop", value="`!usashop`\n`!usabuy <mã>`", inline=False)
    await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Chưa có DISCORD_TOKEN. Hãy đặt token bot vào biến môi trường DISCORD_TOKEN.")

bot.run(TOKEN)
