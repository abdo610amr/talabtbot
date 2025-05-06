from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.ext import MessageHandler, filters
import json
from telegram import Update
from telegram.ext import ContextTypes

import json, os
CONFIG_FILE = "config.json"

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_admin_ids(context):
    if "admin_ids" in context.bot_data:
        return context.bot_data["admin_ids"]
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        admin_ids = config.get("admin_ids", [])
        context.bot_data["admin_ids"] = admin_ids
        return admin_ids

async def add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ الوصول مرفوض.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ الصيغة: /addpoints @username عدد_النقاط")
        return

    username = "".join(context.args[:-1]).replace("@", "")
    try:
        amount = int(context.args[-1])
    except ValueError:
        await update.message.reply_text("❌ العدد يجب أن يكون رقمًا.")
        return

    users = load_users()
    for user_id, data in users.items():
        if username == user_id or username in data.get("name", "").replace(" ", "") or username == data.get("name", ""):
            users[user_id]["points"] += amount
            save_users(users)
            await update.message.reply_text(f"✅ تم إضافة {amount} نقطة لـ {data['name']}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💰 تم إضافة {amount} نقطة إلى رصيدك.\n📊 رصيدك الجديد: {users[user_id]['points']} نقطة"
            )
            return

    await update.message.reply_text("❌ المستخدم غير موجود.")

async def send_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ الأمر خاص بالأدمن فقط.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ الصيغة: /send @username الرقم")
        return

    username = "".join(context.args[:-1]).replace("@", "")
    number = context.args[-1]

    users = load_users()
    for user_id, data in users.items():
        if username == user_id or username in data.get("name", "").replace(" ", "") or username == data.get("name", ""):
            await context.bot.send_message(chat_id=user_id, text=f"📲 رقم التفعيل الخاص بك:\n{number}")
            await update.message.reply_text(f"✅ تم إرسال الرقم لـ {data['name']}")
            return

    await update.message.reply_text("❌ المستخدم غير موجود.")

async def send_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ الأمر خاص بالأدمن فقط.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ الصيغة: /code @username الكود")
        return

    username = "".join(context.args[:-1]).replace("@", "")
    code = context.args[-1]

    users = load_users()
    for user_id, data in users.items():
        if username == user_id or username in data.get("name", "").replace(" ", "") or username == data.get("name", ""):
            await context.bot.send_message(chat_id=user_id, text=f"🔐 كود التفعيل الخاص بك:\n{code}")
            await update.message.reply_text(f"✅ تم إرسال الكود لـ {data['name']}")
            return

    await update.message.reply_text("❌ المستخدم غير موجود.")

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ غير مصرح لك.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ الصيغة: /balance @username")
        return

    username = "".join(context.args).replace("@", "")
    users = load_users()

    for user_id, data in users.items():
        if username == user_id or username in data.get("name", "").replace(" ", "") or username == data.get("name", ""):
            await update.message.reply_text(f"📊 رصيد {data['name']}: {data['points']} نقطة")
            return

    await update.message.reply_text("❌ المستخدم غير موجود.")

async def count_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ غير مصرح.")
        return

    users = load_users()
    await update.message.reply_text(f"👥 عدد المستخدمين: {len(users)}")
from telegram import ReplyKeyboardMarkup

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = get_admin_ids(context)
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ غير مصرح لك.")
        return

    
    keyboard = ReplyKeyboardMarkup(
    [
        ["/users", "/balance @username"],
        ["/addpoints @username 10"],
        ["/send @username الرقم", "/code @username الكود"],
        ["🔙 رجوع"]
    ],
    resize_keyboard=True
    )


    await update.message.reply_text("🛠 لوحة تحكم الأدمن:", reply_markup=keyboard)
async def back_to_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_admin_panel(update, context)
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = context.bot_data.get("admin_ids", [])
    sender_id = update.effective_user.id

    # التأكد أن المرسل أدمن
    if sender_id not in admin_ids:
        await update.message.reply_text("❌ ليس لديك صلاحية تنفيذ هذا الأمر.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ الصيغة الصحيحة: /addadmin user_id")
        return

    try:
        new_admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ يجب إدخال ID صحيح.")
        return

    if new_admin_id in admin_ids:
        await update.message.reply_text("ℹ️ هذا المستخدم بالفعل أدمن.")
        return

    # تحديث القائمة في الذاكرة
    admin_ids.append(new_admin_id)
    context.bot_data["admin_ids"] = admin_ids

    # تحديث ملف config.json
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["admin_ids"] = admin_ids

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(f"✅ تم إضافة ID {new_admin_id} إلى قائمة الأدمن.")
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = context.bot_data.get("admin_ids", [])
    sender_id = update.effective_user.id

    # التأكد أن المرسل أدمن
    if sender_id not in admin_ids:
        await update.message.reply_text("❌ ليس لديك صلاحية تنفيذ هذا الأمر.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ الصيغة الصحيحة: /removeadmin user_id")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ يجب إدخال ID صحيح.")
        return

    if target_id not in admin_ids:
        await update.message.reply_text("ℹ️ هذا المستخدم ليس ضمن قائمة الأدمن.")
        return

    if target_id == sender_id:
        await update.message.reply_text("❌ لا يمكنك حذف نفسك.")
        return

    # إزالة الأدمن
    admin_ids.remove(target_id)
    context.bot_data["admin_ids"] = admin_ids

    # تحديث ملف config.json
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["admin_ids"] = admin_ids

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(f"🗑️ تم حذف ID {target_id} من قائمة الأدمن.")


def register_admin_commands(app):
    app.add_handler(CommandHandler("addpoints", add_points))
    app.add_handler(CommandHandler("send", send_number))
    app.add_handler(CommandHandler("code", send_code))
    app.add_handler(CommandHandler("balance", check_balance))
    app.add_handler(CommandHandler("users", count_users))
    app.add_handler(CommandHandler("admin", show_admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 رجوع$"), back_to_admin_panel))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))

