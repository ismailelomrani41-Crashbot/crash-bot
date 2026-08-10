# Railway deployment
import os
import time
import threading
import statistics
from collections import deque

import requests
from flask import Flask, jsonify, render_template_string

# =========================================================
# CONFIG
# =========================================================

PORT = int(os.getenv("PORT", "8080"))

# اختياري: Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# =========================================================
# FLASK WEBSITE
# =========================================================

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Crash Analyzer</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #090b16;
            color: white;
        }

        .container {
            max-width: 700px;
            margin: auto;
            padding: 25px 15px;
        }

        .header {
            text-align: center;
            margin-bottom: 25px;
        }

        .header h1 {
            margin-bottom: 8px;
            font-size: 32px;
        }

        .header p {
            color: #aaa;
        }

        .card {
            background: #121625;
            border: 1px solid #242a40;
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 18px;
        }

        textarea {
            width: 100%;
            min-height: 120px;
            resize: vertical;
            background: #080b14;
            color: white;
            border: 1px solid #30374f;
            border-radius: 12px;
            padding: 15px;
            font-size: 16px;
            outline: none;
        }

        button {
            width: 100%;
            margin-top: 12px;
            padding: 15px;
            border: 0;
            border-radius: 12px;
            background: #ff7a00;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            opacity: .9;
        }

        .result {
            margin-top: 18px;
        }

        .item {
            display: flex;
            justify-content: space-between;
            padding: 13px 0;
            border-bottom: 1px solid #252b3d;
        }

        .item:last-child {
            border-bottom: none;
        }

        .value {
            font-weight: bold;
            color: #ff9d3d;
        }

        .warning {
            color: #ffb4b4;
            background: #32191d;
            padding: 12px;
            border-radius: 10px;
            margin-top: 15px;
            line-height: 1.6;
        }

        .status {
            text-align: center;
            color: #55e38a;
            margin-top: 15px;
        }

        .example {
            color: #888;
            font-size: 13px;
            margin-top: 8px;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>🎯 Crash Analyzer</h1>
        <p>تحليل إحصائي للجولات السابقة</p>
    </div>

    <div class="card">

        <h3>أدخل النتائج السابقة</h3>

        <textarea id="data"
        placeholder="مثال:
1.25
2.40
1.08
5.70
1.45
3.20
1.12
8.90"></textarea>

        <div class="example">
            دخل الأرقام مفصولة بسطر أو فاصلة.
        </div>

        <button onclick="analyze()">
            🔎 تحليل
        </button>

        <div id="result"></div>

    </div>

</div>

<script>

async function analyze() {

    const data = document.getElementById("data").value;

    const result = document.getElementById("result");

    result.innerHTML = "⏳ جاري التحليل...";

    try {

        const response = await fetch("/analyze", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                rounds: data
            })
        });

        const json = await response.json();

        if (json.status !== "success") {
            result.innerHTML =
                "<div class='warning'>" +
                json.message +
                "</div>";
            return;
        }

        const a = json.analysis;

        result.innerHTML = `

            <div class="card result">

                <div class="item">
                    <span>عدد الجولات</span>
                    <span class="value">${a.count}</span>
                </div>

                <div class="item">
                    <span>المتوسط</span>
                    <span class="value">${a.average}x</span>
                </div>

                <div class="item">
                    <span>أقل نتيجة</span>
                    <span class="value">${a.minimum}x</span>
                </div>

                <div class="item">
                    <span>أعلى نتيجة</span>
                    <span class="value">${a.maximum}x</span>
                </div>

                <div class="item">
                    <span>نتائج أقل من 2x</span>
                    <span class="value">${a.below_2} (${a.below_2_percent}%)</span>
                </div>

                <div class="item">
                    <span>نتائج 2x أو أكثر</span>
                    <span class="value">${a.above_2} (${a.above_2_percent}%)</span>
                </div>

                <div class="item">
                    <span>نتائج 5x أو أكثر</span>
                    <span class="value">${a.above_5}</span>
                </div>

                <div class="item">
                    <span>الوسيط</span>
                    <span class="value">${a.median}x</span>
                </div>

            </div>

            <div class="warning">
                ⚠️ هذا تحليل إحصائي للجولات السابقة فقط.
                لا يمكن ضمان أو معرفة نتيجة الجولة القادمة، لأن نتائج Crash قد تكون عشوائية.
            </div>
        `;

    } catch (error) {

        result.innerHTML =
            "<div class='warning'>وقع خطأ في الاتصال بالسيرفر.</div>";
    }
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "Crash Analyzer"
    })


@app.route("/analyze", methods=["POST"])
def analyze():

    from flask import request

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "لم يتم إرسال البيانات."
        }), 400

    raw = data.get("rounds", "")

    if not raw:
        return jsonify({
            "status": "error",
            "message": "دخل نتائج الجولات السابقة."
        }), 400

    # تحويل الفواصل والأسطر إلى أرقام
    raw = raw.replace(",", " ")
    raw = raw.replace("x", " ")
    raw = raw.replace("X", " ")

    values = []

    for item in raw.split():

        try:
            number = float(item)

            if number > 0:
                values.append(number)

        except ValueError:
            continue

    if len(values) < 3:
        return jsonify({
            "status": "error",
            "message": "خاص على الأقل 3 نتائج صحيحة."
        }), 400

    average = statistics.mean(values)
    median = statistics.median(values)

    below_2 = sum(1 for x in values if x < 2)
    above_2 = sum(1 for x in values if x >= 2)
    above_5 = sum(1 for x in values if x >= 5)

    result = {
        "count": len(values),

        "average": round(average, 2),

        "median": round(median, 2),

        "minimum": round(min(values), 2),

        "maximum": round(max(values), 2),

        "below_2": below_2,

        "below_2_percent": round(
            (below_2 / len(values)) * 100,
            1
        ),

        "above_2": above_2,

        "above_2_percent": round(
            (above_2 / len(values)) * 100,
            1
        ),

        "above_5": above_5
    }

    return jsonify({
        "status": "success",
        "analysis": result
    })


# =========================================================
# TELEGRAM BOT - OPTIONAL
# =========================================================

def telegram_bot():

    if not BOT_TOKEN:
        print("BOT_TOKEN غير موجود. Telegram bot متوقف.")
        return

    try:
        import telebot

        bot = telebot.TeleBot(BOT_TOKEN)

        @bot.message_handler(commands=["start"])
        def start(message):

            bot.reply_to(
                message,
                "🎯 مرحبا بك في Crash Analyzer\n\n"
                "أرسل لي نتائج الجولات السابقة، مثلا:\n\n"
                "1.20\n"
                "2.30\n"
                "1.05\n"
                "4.50\n"
                "3.10\n\n"
                "وسأعطيك التحليل الإحصائي."
            )

        @bot.message_handler(func=lambda message: True)
        def analyze_message(message):

            text = message.text or ""

            text = text.replace(",", " ")
            text = text.replace("x", " ")
            text = text.replace("X", " ")

            values = []

            for item in text.split():

                try:
                    number = float(item)

                    if number > 0:
                        values.append(number)

                except ValueError:
                    continue

            if len(values) < 3:

                bot.reply_to(
                    message,
                    "❌ أرسل على الأقل 3 نتائج.\n\n"
                    "مثال:\n"
                    "1.20\n"
                    "2.50\n"
                    "1.10\n"
                    "4.30"
                )

                return

            average = statistics.mean(values)
            median = statistics.median(values)

            below_2 = sum(
                1 for x in values if x < 2
            )

            above_2 = sum(
                1 for x in values if x >= 2
            )

            above_5 = sum(
                1 for x in values if x >= 5
            )

            response = (
                "🎯 CRASH ANALYZER\n\n"

                f"📊 عدد الجولات: {len(values)}\n"

                f"📈 المتوسط: {average:.2f}x\n"

                f"📌 الوسيط: {median:.2f}x\n"

                f"⬇️ أقل نتيجة: {min(values):.2f}x\n"

                f"⬆️ أعلى نتيجة: {max(values):.2f}x\n\n"

                f"🔻 أقل من 2x: "
                f"{below_2} "
                f"({below_2 / len(values) * 100:.1f}%)\n"

                f"🔺 2x أو أكثر: "
                f"{above_2} "
                f"({above_2 / len(values) * 100:.1f}%)\n"

                f"🔥 5x أو أكثر: {above_5}\n\n"

                "⚠️ التحليل مبني على النتائج السابقة فقط، "
                "ولا يضمن نتيجة الجولة القادمة."
            )

            bot.reply_to(
                message,
                response
            )

        print("Telegram bot started.")

        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=30
        )

    except Exception as e:

        print(
            "Telegram error:",
            str(e)
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("CRASH ANALYZER STARTING")
    print("=" * 50)

    # تشغيل Telegram في Thread
    if BOT_TOKEN:

        thread = threading.Thread(
            target=telegram_bot,
            daemon=True
        )

        thread.start()

    # تشغيل الموقع
    app.run(
        host="0.0.0.0",
        port=PORT
    )
