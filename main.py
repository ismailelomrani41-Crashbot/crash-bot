import os
import logging
from datetime import datetime

import telebot
from telebot import types

from database import init_db, add_result, get_results
from analyzer import analyze_results

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
init_db()


def main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
        types.InlineKeyboardButton("📜 آخر النتائج", callback_data="history"),
    )
    kb.add(
        types.InlineKeyboardButton("➕ إضافة نتيجة", callback_data="add_help"),
        types.InlineKeyboardButton("ℹ️ المساعدة", callback_data="help"),
    )
    return kb


def format_history(results):
    if not results:
        return "📭 لا توجد نتائج مسجلة بعد."

    lines = ["<b>📜 آخر النتائج</b>\n"]
    for i, row in enumerate(results, 1):
        value, created_at = row
        lines.append(f"{i}. <b>{value:.2f}x</b> — {created_at}")
    return "\n".join(lines)


@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "🚀 <b>Crash Analyzer Bot</b>\n\n"
        "هذا البوت مخصص لتسجيل وتحليل النتائج السابقة.\n"
        "لا يقدم توقعات مضمونة ولا ينفذ رهانات تلقائياً.\n\n"
        "استعمل:\n"
        "• <code>/add 3.59</code> لإضافة نتيجة\n"
        "• <code>/history</code> لعرض آخر النتائج\n"
        "• <code>/stats</code> لعرض الإحصائيات"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>طريقة الاستعمال</b>\n\n"
        "<code>/add 3.59</code> — إضافة نتيجة\n"
        "<code>/history</code> — آخر النتائج\n"
        "<code>/stats</code> — تحليل النتائج السابقة\n\n"
        "مثال: <code>/add 8.97</code>"
    )


@bot.message_handler(commands=["add"])
def add_command(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        bot.reply_to(
            message,
            "❌ استعمل الأمر هكذا:\n<code>/add 3.59</code>"
        )
        return

    try:
        value = float(parts[1].replace(",", "."))
    except ValueError:
        bot.reply_to(message, "❌ أدخل رقماً صحيحاً، مثال: <code>/add 3.59</code>")
        return

    if value < 1.0 or value > 100000:
        bot.reply_to(message, "❌ القيمة يجب أن تكون بين 1.00x و 100000x.")
        return

    add_result(
        user_id=message.from_user.id,
        value=value,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    bot.reply_to(message, f"✅ تم تسجيل النتيجة: <b>{value:.2f}x</b>")


@bot.message_handler(commands=["history"])
def history_command(message):
    results = get_results(limit=20)
    bot.send_message(message.chat.id, format_history(results))


@bot.message_handler(commands=["stats"])
def stats_command(message):
    results = get_results(limit=200)
    bot.send_message(message.chat.id, analyze_results(results))


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    try:
        if call.data == "stats":
            results = get_results(limit=200)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, analyze_results(results))

        elif call.data == "history":
            results = get_results(limit=20)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, format_history(results))

        elif call.data == "add_help":
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                "➕ لإضافة نتيجة اكتب:\n\n"
                "<code>/add 3.59</code>\n\n"
                "مثال آخر:\n"
                "<code>/add 8.97</code>"
            )

        elif call.data == "help":
            bot.answer_callback_query(call.id)
            help_command(call.message)

    except Exception:
        logging.exception("Callback error")
        bot.answer_callback_query(call.id, "حدث خطأ.")


@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.reply_to(
        message,
        "👋 ما فهمتش الأمر.\nاستعمل /start باش تشوف القائمة."
    )


if __name__ == "__main__":
    logging.info("Bot is starting...")
    bot.infinity_polling(skip_pending=True)
