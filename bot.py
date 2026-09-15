import os
import json
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

USER_DATA_FILE = "user_data.json"

def load_user_data():
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return {int(k): v for k, v in raw.items()}
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        return {}

def save_user_data():
    tmp = USER_DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_data.items()}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USER_DATA_FILE)

user_data = load_user_data()

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
    save_user_data()
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
    save_user_data()
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
    data = get_user(ctx.author.id)
    now = __import__("time").time()
    last = data.get("last_daily", 0) or 0
    try:
        last = float(last)
    except (ValueError, TypeError):
        last = 0

    cooldown = 24 * 60 * 60
    remaining = cooldown - (now - last)
    if remaining > 0:
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await ctx.send(f"⏳ {ctx.author.mention}, bạn đã nhận daily rồi! Còn **{hours} giờ {minutes} phút** nữa.")
        return

    reward = 50000
    data["cash"] += reward
    data["last_daily"] = now
    save_user_data()
    await ctx.send(f"🎉 {ctx.author.mention} nhận **{reward:,} VNĐ**! ⏰ Daily tiếp theo sau 24 giờ.")

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
        save_user_data()
        return

    if len(data["fish"]) >= data["slots"]:
        await ctx.send(f"❌ Balo đầy ({data['slots']} ô)!")
        return

    rarity, caught = catch_fish(data.get("luck", 1.0))
    data["fish"].append(caught)

    if data.get("durability") is not None:
        data["durability"] -= 1

    save_user_data()
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
        save_user_data()
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
        save_user_data()
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
    save_user_data()

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
    def __init__(self, owner_id, fish_options, page=0):
        self.owner_id = owner_id
        self.page = page
        self.all_options = fish_options

        # Discord Select tối đa 25 lựa chọn. Chia trang để không mất cá.
        page_size = 20
        chunk = fish_options[page * page_size:(page + 1) * page_size]
        options = []
        for fish_name, count in chunk:
            rarity = FISH_TO_RARITY.get(fish_name, "Common")
            price = FISH_SELL_PRICES.get(rarity, 0)
            options.append(
                discord.SelectOption(
                    label=fish_name[:100],
                    description=f"{count} con • {price:,}đ/con",
                    value=fish_name
                )
            )

        super().__init__(
            placeholder=f"🐟 Chọn cá muốn bán • Trang {page + 1}/{max(1, (len(fish_options)-1)//page_size+1)}",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )

        data = get_user(self.owner_id)
        fish = self.values[0]
        count = data["fish"].count(fish)

        if count <= 0:
            return await interaction.response.send_message(
                "❌ Cá này không còn trong balo.", ephemeral=True
            )

        rarity = FISH_TO_RARITY.get(fish, "Common")
        price = FISH_SELL_PRICES[rarity]

        await interaction.response.send_message(
            f"🐟 **{fish}**\n"
            f"📦 Đang có: **{count} con**\n"
            f"💰 Giá: **{price:,} VNĐ/con**\n"
            f"💵 Bán hết sẽ nhận: **{count * price:,} VNĐ**\n\n"
            f"Nhấn **🔢 Nhập số lượng** để nhập số bất kỳ.",
            view=SellQuantityView(self.owner_id, fish, count, price),
            ephemeral=True
        )


class SellFishPageView(discord.ui.View):
    def __init__(self, owner_id, fish_options, page=0):
        super().__init__(timeout=180)
        self.owner_id = owner_id
        self.fish_options = fish_options
        self.page = page
        self.page_size = 20

        self.add_item(SellFishSelect(owner_id, fish_options, page))

        total_pages = max(1, (len(fish_options) - 1) // self.page_size + 1)
        if total_pages > 1:
            prev = discord.ui.Button(
                label="◀ Trang trước",
                style=discord.ButtonStyle.secondary,
                disabled=(page == 0)
            )
            nxt = discord.ui.Button(
                label="Trang sau ▶",
                style=discord.ButtonStyle.secondary,
                disabled=(page >= total_pages - 1)
            )
            prev.callback = self.prev_page
            nxt.callback = self.next_page
            self.add_item(prev)
            self.add_item(nxt)

    async def prev_page(self, interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )
        await interaction.response.edit_message(
            content=self.page_text(max(0, self.page - 1)),
            view=SellFishPageView(self.owner_id, self.fish_options, max(0, self.page - 1))
        )

    async def next_page(self, interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )
        total_pages = max(1, (len(self.fish_options) - 1) // self.page_size + 1)
        new_page = min(total_pages - 1, self.page + 1)
        await interaction.response.edit_message(
            content=self.page_text(new_page),
            view=SellFishPageView(self.owner_id, self.fish_options, new_page)
        )

    def page_text(self, page):
        total_pages = max(1, (len(self.fish_options) - 1) // self.page_size + 1)
        return (
            "🐟 **CHỌN CÁ MUỐN BÁN**\n"
            f"📄 Trang **{page + 1}/{total_pages}** • Có **{len(self.fish_options)} loại cá**\n"
            "Chọn cá bên dưới → nhập số lượng muốn bán."
        )


class SellQuantityModal(discord.ui.Modal, title="💰 BÁN CÁ"):
    quantity = discord.ui.TextInput(
        label="Số lượng muốn bán",
        placeholder="Nhập số bất kỳ, ví dụ: 37",
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
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )

        try:
            quantity = int(str(self.quantity.value).strip())
        except ValueError:
            return await interaction.response.send_message(
                "❌ Số lượng phải là số nguyên.", ephemeral=True
            )

        if quantity <= 0:
            return await interaction.response.send_message(
                "❌ Số lượng phải lớn hơn 0.", ephemeral=True
            )

        data = get_user(self.owner_id)
        actual_count = data["fish"].count(self.fish_name)

        if actual_count <= 0:
            return await interaction.response.send_message(
                "❌ Cá này không còn trong balo.", ephemeral=True
            )

        # Không cho bán vượt quá số lượng thật trong balo.
        if quantity > actual_count:
            return await interaction.response.send_message(
                f"❌ **Không đủ cá!** Bạn chỉ có **{actual_count} con {self.fish_name}**.\n"
                f"Bạn vừa nhập **{quantity} con** nên chưa bán con nào.",
                ephemeral=True
            )

        for _ in range(quantity):
            data["fish"].remove(self.fish_name)

        total = quantity * self.price
        data["cash"] += total
        save_user_data()

        await interaction.response.send_message(
            f"✅ Đã bán **{quantity} con {self.fish_name}**!\n"
            f"💰 Nhận được: **{total:,} VNĐ**\n"
            f"🎒 Còn lại: **{data['fish'].count(self.fish_name)} con**\n"
            f"💵 Số dư: **{data['cash']:,} VNĐ**",
            ephemeral=True
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
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )
        await interaction.response.send_modal(
            SellQuantityModal(
                self.owner_id, self.fish_name, self.max_count, self.price
            )
        )


class SellFishView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=180)
        self.owner_id = owner_id

    @discord.ui.button(label="💰 Bán cá", style=discord.ButtonStyle.green, row=0)
    async def sell_button(self, interaction, button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(
                "❌ Đây không phải balo của bạn.", ephemeral=True
            )

        data = get_user(self.owner_id)
        if not data["fish"]:
            return await interaction.response.send_message(
                "❌ Balo cá đang trống.", ephemeral=True
            )

        counts = {}
        for fish in data["fish"]:
            counts[fish] = counts.get(fish, 0) + 1

        options = sorted(
            counts.items(),
            key=lambda x: (
                list(FISH_RARITIES.keys()).index(FISH_TO_RARITY.get(x[0], "Common")),
                x[0]
            )
        )

        view = SellFishPageView(self.owner_id, options, 0)
        await interaction.response.send_message(
            view.page_text(0), view=view, ephemeral=True
        )


def build_inventory_embed(ctx, data):
    # Gộp cá trùng tên để giao diện gọn và dễ nhìn.
    counts = {}
    for fish in data["fish"]:
        counts[fish] = counts.get(fish, 0) + 1

    if counts:
        fish_lines = []
        for fish, count in counts.items():
            rarity = FISH_TO_RARITY.get(fish, "Common")
            emoji = RARITY_EMOJI.get(rarity, "🐟")
            price = FISH_SELL_PRICES.get(rarity, 0)
            fish_lines.append(f"{emoji} **{fish}** × **{count}** • {price:,}đ")
        fish_text = "\n".join(fish_lines)
        if len(fish_text) > 3900:
            fish_text = fish_text[:3890] + "\n…"
    else:
        fish_text = "🈳 Balo cá đang trống."

    if data.get("rod"):
        rod_name = data["rod"]
        durability = data.get("durability")
        luck = data.get("luck", 1.0)
        durability_text = "♾️ Không thể gãy" if durability is None else f"{durability}"
        rod_text = (
            f"🎣 **{rod_name}**\n"
            f"🔧 Độ bền: **{durability_text}**\n"
            f"🍀 May mắn: **x{luck}**"
        )
    else:
        rod_text = "❌ Chưa trang bị cần câu\nMua bằng `!usabuy can_tre`"

    pets = data.get("pets", [])
    pet_text = "\n".join(f"🐾 **{pet}**" for pet in pets) if pets else "🈳 Chưa có pet."

    embed = discord.Embed(
        title=f"🎒 KHO ĐỒ • {ctx.author.display_name}",
        description=(
            f"**┌── 🐟 CÁ ──────────────────┐**\n"
            f"│ Balo: **{len(data['fish'])}/{data['slots']}** ô\n"
            f"└──────────────────────────┘"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🐟 CÁ",
        value=fish_text,
        inline=False
    )
    embed.add_field(
        name="🎣 CẦN",
        value=rod_text,
        inline=True
    )
    embed.add_field(
        name="🐾 PET",
        value=pet_text[:1024],
        inline=True
    )
    embed.add_field(
        name="💰 TIỀN",
        value=f"**{data['cash']:,} VNĐ**",
        inline=True
    )
    embed.set_footer(text="💰 Bán cá → chọn cá → 🔢 Nhập số lượng bất kỳ")
    return embed


@bot.command(name="usafinv")
async def usafinv(ctx):
    data = get_user(ctx.author.id)
    await ctx.send(
        embed=build_inventory_embed(ctx, data),
        view=SellFishView(ctx.author.id)
    )


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
    save_user_data()
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
        save_user_data()
        await ctx.send(f"🎉 Đã mua **{item['name']}**! Balo: **{item['slots']} ô**.")
    else:
        if item_key not in data["owned_rods"]:
            data["owned_rods"].append(item_key)
        data["rod"] = item["name"]
        data["rod_key"] = item_key
        data["durability"] = item.get("durability")
        data["luck"] = item.get("luck", 1.0)
        save_user_data()
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
