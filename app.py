from flask import Flask, render_template, jsonify, request
from statistics import mean, median
import os

app = Flask(__name__)

# بيانات تجريبية مؤقتة
history = [
    2.60, 3.49, 1.42, 1.08,
    4.21, 1.76, 2.02, 1.15,
    5.63, 1.31, 2.88, 1.04,
    3.10, 1.67, 2.25, 7.20
]


def analyze(values):

    if not values:
        return {
            "average": 0,
            "median": 0,
            "under2": 0,
            "over2": 0,
            "low_streak": 0,
            "risk": "غير متوفر"
        }

    under2 = sum(x < 2 for x in values)
    over2 = len(values) - under2

    streak = 0

    for x in values:
        if x < 2:
            streak += 1
        else:
            break

    under_percent = under2 / len(values)

    if under_percent >= 0.65:
        risk = "مرتفع"

    elif under_percent >= 0.50:
        risk = "متوسط"

    else:
        risk = "منخفض"

    return {
        "average": round(mean(values), 2),
        "median": round(median(values), 2),
        "under2": round(under_percent * 100, 1),
        "over2": round(over2 / len(values) * 100, 1),
        "low_streak": streak,
        "risk": risk
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/history")
def api_history():

    return jsonify({
        "history": history,
        "analysis": analyze(history)
    })


@app.route("/api/add", methods=["POST"])
def add_result():

    data = request.get_json(silent=True) or {}

    try:
        value = float(data["value"])

        if value < 1:
            raise ValueError

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "قيمة غير صحيحة"
        }), 400

    history.insert(0, round(value, 2))

    # الاحتفاظ بآخر 100 نتيجة
    del history[100:]

    return jsonify({
        "history": history,
        "analysis": analyze(history)
    })


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
