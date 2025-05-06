from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

import json, os

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    full_name = update.effective_user.full_name
    username = update.effective_user.username or "بدون معرف"
    users = load_users()

    if user_id not in users:
        users[user_id] = {"name": full_name, "points": 0}
        save_users(users)

    keyboard = ReplyKeyboardMarkup(
        [["💰 معرفة الرصيد", "💳 شحن الرصيد"], ["📲 طلب رقم"]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "مرحبًا بك في بوت طلبات 👋\n\nاستخدم الأزرار بالأسفل للتحكم:\n💰 معرفة الرصيد\n💳 شحن الرصيد\n📲 طلب رقم\n\n📞 لو عندك أي استفسار، تقدر ترجع للإدارة.",
        reply_markup=keyboard
    )

    for admin_id in get_admin_ids(context):
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"🚀 مستخدم جديد بدأ استخدام البوت:\n👤 الاسم: {full_name}\n🔗 يوزر: @{username}\n🆔 ID: {user_id}"
        )

async def check_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    points = users.get(user_id, {}).get("points", 0)

    if points == 0:
        keyboard = ReplyKeyboardMarkup(
            [["💳 شحن الرصيد", "📲 طلب رقم"], ["🔙 رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("رصيدك الحالي هو 0 نقطة ❗", reply_markup=keyboard)
    else:
        await update.message.reply_text(f"رصيدك الحالي: {points} نقطة 💰")

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["💰 معرفة الرصيد", "💳 شحن الرصيد"], ["📲 طلب رقم"]],
        resize_keyboard=True
    )
    await update.message.reply_text("رجعناك للقائمة الرئيسية 👇", reply_markup=keyboard)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "بدون معرف"
    full_name = update.effective_user.full_name or "بدون اسم"
    users = load_users()
    points = users.get(user_id, {}).get("points", 0)

    if points < 5:
        keyboard = ReplyKeyboardMarkup(
            [["💳 شحن الرصيد", "🔙 رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("رصيدك أقل من 5 نقاط ❗", reply_markup=keyboard)
        return

    users[user_id]["points"] -= 5
    save_users(users)

    for admin_id in get_admin_ids(context):
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"📥 طلب رقم جديد من العميل:\n👤 الاسم: {full_name}\n"
                f"🔗 يوزر: @{username}\n🆔 ID: {user_id}\n💰 بعد الخصم: {users[user_id]['points']} نقطة\n\n"
                f"/send @{username} الرقم\n/code @{username} الكود"
            )
        )

    keyboard = ReplyKeyboardMarkup([["🔐 إرسال الكود", "🔙 رجوع"]], resize_keyboard=True)
    await update.message.reply_text(
        f"✅ تم خصم 5 نقاط.\n💰 رصيدك الحالي: {users[user_id]['points']} نقطة\n📦 سيتم إرسال الرقم لك قريبًا.",
        reply_markup=keyboard
    )

async def handle_send_code_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "بدون معرف"
    full_name = update.effective_user.full_name or "بدون اسم"

    for admin_id in get_admin_ids(context):
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"📩 العميل @{username} يطلب إرسال كود التفعيل الآن.\n👤 الاسم: {full_name}\n🆔 ID: {user_id}\n\n/code @{username} الكود"
        )

    await update.message.reply_text("📬 تم إخطار الإدارة لإرسال كود التفعيل.\nانتظر لحظات.")

async def handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([["🔙 رجوع"]], resize_keyboard=True)
    await update.message.reply_text(
        " سعر النقطة 5 جنية 💸",
        reply_markup=keyboard
    )
    await update.message.reply_text(
        "💳 لشحن رصيدك:\n\nقم بتحويل المبلغ على رقم فودافون كاش التالي:\n📱 010xxxxxxxx\n\nثم أرسل صورة التحويل + رقم التحويل هنا.\n📌 سيتم تأكيده من الإدارة وتحويل النقاط لك.",
        reply_markup=keyboard
    )

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "بدون معرف"
    full_name = user.full_name or "بدون اسم"

    if update.message.photo:
        photo = update.message.photo[-1]
        for admin_id in get_admin_ids(context):
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=f"🧾 صورة تحويل من: {full_name}\n🔗 @{username}\n🆔 ID: {user_id}"
            )
        await update.message.reply_text("✅ تم استلام التحويل.\n📌 سيتم تأكيده من الإدارة وتحويل النقاط إلى حسابك خلال وقت قصير.")
    else:
        text = update.message.text
        for admin_id in get_admin_ids(context):
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💬 رسالة تحويل من: {full_name}\n🔗 @{username}\n🆔 ID: {user_id}\n\n{text}"
            )
        await update.message.reply_text("✅ تم استلام التحويل.\n📌 سيتم تأكيده من الإدارة وتحويل النقاط إلى حسابك خلال وقت قصير.")

def register_user_commands(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💰 معرفة الرصيد$"), check_points))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 رجوع$"), back_to_main))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📲 طلب رقم$"), handle_request))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💳 شحن الرصيد$"), handle_subscribe))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔐 إرسال الكود$"), handle_send_code_request))
    app.add_handler(MessageHandler((filters.PHOTO | (filters.TEXT & ~filters.COMMAND)), handle_payment_proof))

