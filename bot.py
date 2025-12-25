import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
import asyncio

# ================== تنظیمات ==================
TOKEN = "8496334769:AAFMIbMh9cNI4-UPeonQzBMF7DslB227qBA"

CHANNEL_ID = "@TRFchannel63"
GROUP_ID = "@TRFgameGP"

ADMIN_IDS = [
    5962245820,  # ادمین 1
    1712109362,  # ادمین 2
    7312588451   # ادمین 3
]

DATA_FILE = "xp_data.json"

# ================== دیتابیس ==================
try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
except:
    data = {"users": {}, "invites": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================== ابزارها ==================
def get_level(xp):
    if xp >= 150:
        return "🥇 Gold"
    elif xp >= 50:
        return "🥈 Silver"
    return "🥉 Bronze"

def get_display(user_info, user_id=None):
    if user_info.get("username"):
        return f"@{user_info['username']}"
    if user_info.get("name"):
        return user_info["name"]
    return f"ID:{user_id}" if user_id else "بدون نام"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 درباره TRF", callback_data="about")],
        [InlineKeyboardButton("🎯 لینک دعوت من", callback_data="invite")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="profile")],
        [InlineKeyboardButton("🏆 لیدربورد", callback_data="leaderboard")],
        [InlineKeyboardButton("✉️ ارسال پیشنهاد", callback_data="suggest")]
    ])

def join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 عضویت در چنل", url="https://t.me/TRFchannel63")],
        [InlineKeyboardButton("💬 عضویت در گپ", url="https://t.me/TRFgameGP")],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
    ])

async def is_member(user_id, bot):
    try:
        ch = await bot.get_chat_member(CHANNEL_ID, user_id)
        gp = await bot.get_chat_member(GROUP_ID, user_id)
        return ch.status in ["member", "administrator", "creator"] and gp.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return  # فقط چت خصوصی

    user = update.message.from_user
    user_key = str(user.id)

    # ثبت کاربر جدید
    is_new_user = False
    if user_key not in data["users"]:
        data["users"][user_key] = {
            "xp": 0,
            "username": user.username,
            "name": user.first_name
        }
        is_new_user = True
        save_data()

    # لینک دعوت
    if context.args and is_new_user:
        inviter_key = context.args[0]
        if inviter_key != user_key and inviter_key in data["users"]:
            data["users"][inviter_key]["xp"] += 10
            data["invites"][user_key] = inviter_key
            save_data()
            inviter_display = get_display(data["users"][inviter_key], inviter_key)
            new_user_display = get_display(data["users"][user_key], user_key)
            try:
                await context.bot.send_message(chat_id=int(inviter_key),
                                               text=f"🎉 {new_user_display} توسط شما دعوت شد! +10 XP دریافت کردید.")
            except:
                pass

    # بررسی عضویت
    if not await is_member(user.id, context.bot):
        await update.message.reply_text("⚠️ برای استفاده از ربات باید عضو چنل و گروه باشید:", reply_markup=join_menu())
        return

    await update.message.reply_text("🏠 منوی اصلی:", reply_markup=main_menu())

# ================== دکمه‌ها ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    query = update.callback_query
    user_key = str(query.from_user.id)
    await query.answer()

    if query.data == "check_join":
        if await is_member(query.from_user.id, context.bot):
            await query.edit_message_text("✅ عضویت تأیید شد", reply_markup=main_menu())
        else:
            await query.answer("❌ هنوز عضو نیستید", show_alert=True)

    elif query.data == "about":
        await query.edit_message_text("درحال انجام . . . 🌟",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    elif query.data == "invite":
        link = f"https://t.me/{context.bot.username}?start={user_key}"
        await query.edit_message_text(f"🎯 لینک دعوت شما:\n{link}\nهر کسی با این لینک وارد شود، شما +10 XP می‌گیرید.",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    elif query.data == "profile":
        xp = data["users"][user_key]["xp"]
        level = get_level(xp)
        display = get_display(data["users"][user_key], user_key)
        await query.edit_message_text(f"👤 پروفایل شما:\n⭐ XP: {xp}\n🎖 سطح: {level}\n👤 نام: {display}",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    elif query.data == "leaderboard":
        sorted_users = sorted(data["users"].items(), key=lambda x: x[1]["xp"], reverse=True)
        text = "🏆 لیدربورد:\n\n"
        for i, (uid, info) in enumerate(sorted_users[:10], 1):
            display = get_display(info, uid)
            text += f"{i}. {display} → {info['xp']} XP\n"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    elif query.data == "suggest":
        context.user_data["awaiting_suggestion"] = True
        await query.edit_message_text("✉️ پیشنهاد خود را تایپ و ارسال کنید:",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    elif query.data == "back":
        await query.edit_message_text("🏠 منوی اصلی:", reply_markup=main_menu())

# ================== پیام‌ها ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.message.from_user
    user_key = str(user.id)
    text = update.message.text

    if context.user_data.get("awaiting_suggestion"):
        first_name = user.first_name or "بدون نام"
        username = f"@{user.username}" if user.username else "ندارد"
        user_info = f"{first_name} {username}".strip()
        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=f"📩 پیشنهاد جدید\n👤 نام: {user_info}\n📝 متن پیام:\n{text}")
        context.user_data["awaiting_suggestion"] = False
        await update.message.reply_text("✅ پیشنهاد شما ارسال شد", reply_markup=main_menu())
        return

    if context.user_data.get("awaiting_broadcast") and user.id in ADMIN_IDS:
        for uid, info in data["users"].items():
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
                await asyncio.sleep(0.05)  # جلوگیری از محدودیت تلگرام
            except:
                pass
        context.user_data["awaiting_broadcast"] = False
        await update.message.reply_text("✅ پیام همگانی ارسال شد", reply_markup=main_menu())
        return

    if context.user_data.get("awaiting_modify_xp") and user.id in ADMIN_IDS:
        try:
            parts = text.split()
            target_username = parts[0].replace("@", "")
            amount = int(parts[1])
            target_key = None
            for uid, info in data["users"].items():
                if info.get("username") == target_username:
                    target_key = uid
                    break
            if not target_key:
                await update.message.reply_text("❌ کاربر پیدا نشد", reply_markup=main_menu())
                context.user_data["awaiting_modify_xp"] = False
                return
            data["users"][target_key]["xp"] += amount
            save_data()
            display = get_display(data["users"][target_key], target_key)
            await update.message.reply_text(f"✅ XP کاربر {display} تغییر کرد. (Δ {amount})", reply_markup=main_menu())
        except:
            await update.message.reply_text("❌ فرمت اشتباه است. مثال: @username 10", reply_markup=main_menu())
        context.user_data["awaiting_modify_xp"] = False
        return

# ================== پنل ادمین ==================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    if update.message.from_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ شما ادمین نیستید")
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="broadcast")],
        [InlineKeyboardButton("➕/➖ امتیاز کاربر", callback_data="modify_xp")]
    ])
    await update.message.reply_text("🛠 پنل ادمین", reply_markup=keyboard)

# ================== callback handler ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data in ["about","invite","profile","leaderboard","suggest","back","check_join"]:
        await button(update, context)
        return
    if user_id in ADMIN_IDS and query.data in ["stats","broadcast","modify_xp"]:
        await admin_buttons(update, context)
        return
    if query.data in ["stats","broadcast","modify_xp"]:
        await query.answer("❌ دسترسی ندارید", show_alert=True)

# ================== دکمه‌های ادمین ==================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # ================= آمار کاربران =================
    if query.data == "stats":
        total_users = len(data['users'])
        invited_users_count = len(data['invites'])
        details = ""

        for uid, info in data['users'].items():
            display = f"@{info['username']}" if info.get("username") else f"ID:{uid}"
            invited_list = [
                f"@{data[u]['username']}" if data[u].get("username") else f"ID:{u}"
                for u, inviter in data['invites'].items() if inviter == uid
            ]
            if invited_list:
                details += f"\n👤 {display} → دعوت کرده: {len(invited_list)} نفر: {', '.join(invited_list)}"
            else:
                details += f"\n👤 {display} → دعوت کرده: 0 نفر"

        text = (
            f"📊 آمار ربات:\n"
            f"👤 کل کاربران: {total_users}\n"
            f"🆔 کاربران دعوت شده: {invited_users_count}\n"
            f"{details}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )

    # ================= پیام همگانی =================
    elif query.data == "broadcast":
        context.user_data["awaiting_broadcast"] = True
        await query.edit_message_text(
            "📢 لطفاً پیام همگانی را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )

    # ================= تغییر XP کاربران =================
    elif query.data == "modify_xp":
        context.user_data["awaiting_modify_xp"] = True
        await query.edit_message_text(
            "➕/➖ امتیاز: پیام را با فرمت زیر ارسال کنید:\n"
            "@username amount\n"
            "مثال: @user 10",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )

# ================== اجرا ==================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 ربات TRF اجرا شد")
app.run_polling()