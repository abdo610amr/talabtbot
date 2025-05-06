from telegram.ext import ApplicationBuilder
from user_commands import register_user_commands
from admin_commands import register_admin_commands
import json

# تحميل config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["token"]
ADMIN_IDS = config["admin_ids"]  # ← قراءة قائمة الأدمن

# إنشاء التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()
from keep_alive import keep_alive
keep_alive()

# تسجيل الأوامر
register_user_commands(app)
register_admin_commands(app)


print("🤖 البوت شغّال... ابدأ المراسلة على تيليجرام.")
app.run_polling()
