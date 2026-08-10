import os
import statistics
import logging
import telebot

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in Railway Variables")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.info("Bot is starting...")


# =========================
# HELP
# =========================

HELP_TEXT = """
<b>🚀 Crash Analyzer</b>

أرسل النتائج السابقة بهذا الشكل:

<code>3.59 2.10 1.24 5.80 1.05 2.60 8.97</code>

أو:

<code>/analyze 3.59 2.10 1.24 5.80 1.05 2.60</code>

البوت يعطيك:

📊 المتوسط
📈 أعلى نتيجة
📉 أقل نتيجة
🎯 نسبة النتائج فوق 2x
🔥 نسبة النتائج فوق 3x
📋 آخر النتائج

⚠️ التحليل إحصائي للنتائج السابقة فقط، ولا يمكنه ضمان أو معرفة نتيجة الجولة القادمة.
"""


# =========================
# PARSE NUMBERS
# =========================

def parse_numbers(text):
    """
    Converts user input into a list of multipliers.
    Accepts:
    2.50 1.20 3.40
    2.50,1.20,3.40
    2,50 1,20 3,40
    """

    text = text.replace(",", " ")

    parts = text.split()

    values = []

    for part in parts:
        try:
            value = float(part)

            if value >= 1:
                values.append(value)

        except ValueError:
            continue

    return values


# =========================
# ANALYSIS
# =========================

def analyze(values):

    if not values:
        return "❌ ما لقيتش أرقام صحيحة."

    count = len(values)

    average = statistics.mean(values)

    minimum = min(values)
    maximum = max(values)

    median = statistics.median(values)

    over_2 = sum(1 for x in values if x >= 2)
    over_3 = sum(1 for x in values if x >= 3)
    over_5 = sum(1 for x in values if x >= 5)
    over_10 = sum(1 for x in values if x >= 10)

    pct_2 = (over_2 / count) * 100
    pct_3 = (over_3 / count) * 100
    pct_5 = (over_5 / count) * 100
    pct_10 = (over_10 / count) * 100

    recent = values[-10:]

    recent_text = " • ".join(
        f"{x:.2f}x" for x in reversed(recent)
    )

    # Last result
    last = values[-1]

    if last < 1.50:
        last_zone = "🔴 منخفضة"
    elif last < 2:
        last_zone = "🟠 متوسطة"
    elif last < 5:
        last_zone = "🟡 مرتفعة"
    else:
        last_zone = "🟢 عالية"

    result = f"""
<b>🚀 CRASH ANALYZER</b>

━━━━━━━━━━━━━━━━━━

<b>📊 الإحصائيات</b>

عدد الجولات:
<b>{count}</b>

المتوسط:
<b>{average:.2f}x</b>

الوسيط:
<b>{median:.2f}x</b>

أعلى نتيجة:
<b>🔥 {maximum:.2f}x</b>

أدنى نتيجة:
<b>📉 {minimum:.2f}x</b>

━━━━━━━━━━━━━━━━━━

<b>🎯 التوزيع</b>

≥ 2x:
<b>{over_2}/{count}</b> — {pct_2:.1f}%

≥ 3x:
<b>{over_3}/{count}</b> — {pct_3:.1f}%

≥ 5x:
<b>{over_5}/{count}</b> — {pct_5:.1f}%

≥ 10x:
<b>{over_10}/{count}</b> — {pct_10:.1f}%

━━━━━━━━━━━━━━━━━━

<b>📋 آخر النتائج</b>

{recent_text}

━━━━━━━━━━━━━━━━━━

آخر نتيجة:
<b>{last:.2f}x</b>

الحالة الإحصائية:
<b>{last_zone}</b>

━━━━━━━━━━━━━━━━━━

⚠️ <b>ملاحظة:</b>

هذه إحصائيات للنتائج السابقة فقط.
لا يمكن اعتبارها توقعاً مضموناً للجولة القادمة، لأن نتائج Crash لا يمكن استنتاجها بشكل موثوق من النتائج السابقة.

"""


    return result


# =========================
# /START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    text = """
<b>🚀 أهلاً بك في Crash Analyzer</b>

البوت كيقرا النتائج السابقة وكيعطيك تحليل إحصائي سريع.

مثال:

<code>3.59 2.10 1.24 5.80 1.05 2.60 8.97</code>

ثم صيفطهم للبوت.

استعمل:
<code>/help</code>

باش تشوف طريقة الاستعمال.
"""

    bot.reply_to(message, text)


# =========================
# /HELP
# =========================

@bot.message_handler(commands=["help"])
def help_command(message):

    bot.reply_to(message, HELP_TEXT)


# =========================
# /ANALYZE
# =========================

@bot.message_handler(commands=["analyze"])
def analyze_command(message):

    try:

        text = message.text.replace("/analyze", "", 1).strip()

        if not text:
            bot.reply_to(
                message,
                "❌ أرسل النتائج بعد الأمر.\n\n"
                "مثال:\n"
                "<code>/analyze 3.59 2.10 1.24 5.80</code>"
            )
            return

        values = parse_numbers(text)

        if len(values) < 3:
            bot.reply_to(
                message,
                "❌ خاصني على الأقل 3 نتائج للتحليل."
            )
            return

        result = analyze(values)

        bot.reply_to(message, result)

    except Exception as e:

        logging.exception("Analyze error")

        bot.reply_to(
            message,
            "❌ وقع خطأ أثناء التحليل."
        )


# =========================
# NORMAL TEXT
# =========================

@bot.message_handler(
    func=lambda message: True,
    content_types=["text"]
)
def normal_message(message):

    try:

        values = parse_numbers(message.text)

        if len(values) >= 3:

            result = analyze(values)

            bot.reply_to(message, result)

        else:

            bot.reply_to(
                message,
                "👋 صيفط ليا النتائج السابقة مثلاً:\n\n"
                "<code>3.59 2.10 1.24 5.80 1.05 2.60</code>\n\n"
                "أو استعمل /help"
            )

    except Exception:

        logging.exception("Message error")

        bot.reply_to(
            message,
            "❌ وقع خطأ. جرب ترسل الأرقام فقط."
        )


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":

    logging.info("================================")
    logging.info("Crash Analyzer Bot is starting")
    logging.info("================================")

    try:

        bot.remove_webhook()

        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=30,
            skip_pending=True
        )

    except Exception as e:

        logging.exception("Bot stopped")

        raise
