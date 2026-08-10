import os
import threading
import time
from collections import deque
from statistics import mean, median

from flask import Flask, jsonify

try:
    import telebot
except ImportError:
    telebot = None


# ============================================================
# 1XBET CRASH STATS BOT
# Descriptive statistics only.
# It does NOT predict the next crash or give betting signals.
# ============================================================

PORT = int(os.getenv("PORT", "8080"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

app = Flask(__name__)

bot = None
if BOT_TOKEN and telebot is not None:
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# Keep the latest 200 manually entered multipliers in memory.
results = deque(maxlen=200)


# ============================================================
# RAILWAY HEALTH
# ============================================================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "1xBet Crash Stats Bot",
        "telegram_bot": bool(bot),
        "results_saved": len(results)
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


# ============================================================
# HELPERS
# ============================================================

def parse_multiplier(value):
    """
    Accepts:
      1.25
      1,25
      x1.25
      1.25x
    """
    value = value.lower().strip()
    value = value.replace("x", "")
    value = value.replace(",", ".")

    number = float(value)

    if number < 1:
        raise ValueError("Multiplier must be >= 1.00")

    if number > 100000:
        raise ValueError("Multiplier is too large.")

    return number


def add_result(value):
    number = parse_multiplier(value)
    results.append(number)
    return number


def stats():
    if not results:
        return None

    values = list(results)

    under_2 = sum(1 for x in values if x < 2)
    from_2_to_5 = sum(1 for x in values if 2 <= x < 5)
    from_5_to_10 = sum(1 for x in values if 5 <= x < 10)
    over_10 = sum(1 for x in values if x >= 10)

    return {
        "count": len(values),
        "last": values[-1],
        "average": mean(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "under_2": under_2,
        "2_to_5": from_2_to_5,
        "5_to_10": from_5_to_10,
        "over_10": over_10,
    }


def stats_message():
    data = stats()

    if not data:
        return (
            "📊 <b>Crash Stats</b>\n\n"
            "مازال ما دخلنا حتى نتيجة.\n\n"
            "دخل مثلاً:\n"
            "<code>/add 1.42</code>"
        )

    total = data["count"]

    def pct(n):
        return f"{(n / total) * 100:.1f}%"

    recent = list(results)[-10:]
    recent_text = " • ".join(f"{x:.2f}x" for x in recent)

    return (
        "📊 <b>1xBet Crash — Statistics</b>\n\n"
        f"🔢 النتائج المسجلة: <b>{total}</b>\n"
        f"🕐 آخر نتيجة: <b>{data['last']:.2f}x</b>\n"
        f"📈 المتوسط: <b>{data['average']:.2f}x</b>\n"
        f"📌 الوسيط: <b>{data['median']:.2f}x</b>\n"
        f"⬇️ أقل نتيجة: <b>{data['min']:.2f}x</b>\n"
        f"⬆️ أعلى نتيجة: <b>{data['max']:.2f}x</b>\n\n"
        "📉 <b>التوزيع:</b>\n"
        f"أقل من 2x: <b>{data['under_2']}</b> ({pct(data['under_2'])})\n"
        f"2x إلى أقل من 5x: <b>{data['2_to_5']}</b> ({pct(data['2_to_5'])})\n"
        f"5x إلى أقل من 10x: <b>{data['5_to_10']}</b> ({pct(data['5_to_10'])})\n"
        f"10x أو أكثر: <b>{data['over_10']}</b> ({pct(data['over_10'])})\n\n"
        f"🧾 آخر 10: <code>{recent_text}</code>\n\n"
        "⚠️ الإحصائيات تصف النتائج السابقة فقط ولا تتنبأ بالنتيجة القادمة."
    )


# ============================================================
# TELEGRAM
# ============================================================

if bot:

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.reply_to(
            message,
            "🎮 <b>1xBet Crash Stats Bot</b>\n\n"
            "هاد البوت كيسجل النتائج اللي كتدخلها وكيعطيك إحصائيات وصفية.\n\n"
            "الأوامر:\n"
            "<code>/add 1.42</code> — إضافة نتيجة\n"
            "<code>/add 2.35x</code> — إضافة نتيجة\n"
            "<code>/stats</code> — الإحصائيات\n"
            "<code>/last</code> — آخر النتائج\n"
            "<code>/clear</code> — مسح النتائج\n"
            "<code>/help</code> — المساعدة\n\n"
            "⚠️ ما كاينش prediction مضمون للـCrash."
        )

    @bot.message_handler(commands=["help"])
    def help_command(message):
        start(message)

    @bot.message_handler(commands=["add"])
    def add_command(message):
        parts = message.text.split(maxsplit=1)

        if len(parts) != 2:
            bot.reply_to(
                message,
                "❌ استعمل:\n<code>/add 1.42</code>"
            )
            return

        try:
            value = add_result(parts[1])
            bot.reply_to(
                message,
                f"✅ تسجلت النتيجة: <b>{value:.2f}x</b>\n\n"
                f"📊 المجموع: <b>{len(results)}</b>\n\n"
                "استعمل /stats للإحصائيات."
            )
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)}")

    @bot.message_handler(commands=["stats"])
    def stats_command(message):
        bot.reply_to(message, stats_message())

    @bot.message_handler(commands=["last"])
    def last_command(message):
        if not results:
            bot.reply_to(message, "مازال ما كايناش نتائج.")
            return

        values = list(results)[-20:]
        text = "🧾 <b>آخر النتائج</b>\n\n"

        for i, value in enumerate(reversed(values), 1):
            text += f"{i}. <b>{value:.2f}x</b>\n"

        bot.reply_to(message, text)

    @bot.message_handler(commands=["clear"])
    def clear_command(message):
        results.clear()
        bot.reply_to(message, "🗑️ تم مسح النتائج المسجلة.")

    @bot.message_handler(content_types=["text"])
    def text_handler(message):
        text = message.text.strip()

        # Allow simply sending "1.42x" without /add.
        try:
            value = add_result(text)
            bot.reply_to(
                message,
                f"✅ تسجلت: <b>{value:.2f}x</b>\n"
                "استعمل /stats باش تشوف الإحصائيات."
            )
        except Exception:
            bot.reply_to(
                message,
                "❌ ما فهمتش القيمة.\n\n"
                "دخل مثلاً: <code>1.42x</code>\n"
                "أو استعمل: <code>/add 1.42</code>"
            )


def run_bot():
    if not bot:
        print("BOT_TOKEN is missing or telebot is unavailable.")
        return

    while True:
        try:
            print("Starting Telegram polling...")
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )
        except Exception as e:
            print("Telegram error:", e)
            time.sleep(5)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    print("1xBet Crash Stats Bot starting...")
    print("PORT:", PORT)
    print("BOT_TOKEN configured:", bool(BOT_TOKEN))

    threading.Thread(target=run_bot, daemon=True).start()

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )
