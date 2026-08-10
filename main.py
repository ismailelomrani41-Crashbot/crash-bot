from flask import Flask, request, jsonify, render_template_string
import statistics
import math

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="en">
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
            background: #090d25;
            color: white;
        }

        .header {
            background: linear-gradient(135deg, #172b55, #273f73);
            padding: 20px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }

        .header p {
            margin: 8px 0 0;
            color: #cbd5ff;
        }

        .container {
            max-width: 700px;
            margin: 25px auto;
            padding: 15px;
        }

        .card {
            background: #111735;
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }

        textarea {
            width: 100%;
            min-height: 130px;
            resize: vertical;
            border: 2px solid #303b78;
            background: #080d25;
            color: white;
            border-radius: 12px;
            padding: 15px;
            font-size: 16px;
            outline: none;
        }

        textarea:focus {
            border-color: #6c5ce7;
        }

        button {
            width: 100%;
            margin-top: 15px;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(90deg, #ff6b00, #ff304f);
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }

        button:active {
            transform: scale(0.98);
        }

        .result {
            display: none;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .stat {
            background: #1b2247;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }

        .stat-title {
            color: #aeb8e8;
            font-size: 13px;
        }

        .stat-value {
            margin-top: 7px;
            font-size: 22px;
            font-weight: bold;
        }

        .analysis {
            background: #181f42;
            border-radius: 12px;
            padding: 16px;
            line-height: 1.7;
        }

        .warning {
            color: #ffcc66;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 15px;
        }

        .error {
            background: #491b2a;
            color: #ff9eae;
            padding: 14px;
            border-radius: 10px;
            display: none;
            margin-top: 15px;
        }

        @media (max-width: 500px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<div class="header">
    <h1>🚀 Crash Analyzer</h1>
    <p>Historical statistics & analysis</p>
</div>

<div class="container">

    <div class="card">

        <label>
            أدخل نتائج الجولات السابقة
        </label>

        <textarea id="history"
            placeholder="مثال:
1.25
2.10
1.04
3.50
1.18
7.20
1.02
2.80
4.10"></textarea>

        <button onclick="analyze()">
            🔎 ANALYZE
        </button>

        <div id="error" class="error"></div>

        <div class="warning">
            ⚠️ التحليل إحصائي للنتائج السابقة فقط، ولا يمكنه ضمان نتيجة الجولة القادمة.
        </div>

    </div>


    <div id="result" class="result">

        <div class="card">

            <h2>📊 Statistics</h2>

            <div class="grid">

                <div class="stat">
                    <div class="stat-title">Rounds</div>
                    <div class="stat-value" id="count">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Average</div>
                    <div class="stat-value" id="average">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Minimum</div>
                    <div class="stat-value" id="minimum">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Maximum</div>
                    <div class="stat-value" id="maximum">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Below 2x</div>
                    <div class="stat-value" id="low">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">2x - 5x</div>
                    <div class="stat-value" id="medium">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Above 5x</div>
                    <div class="stat-value" id="high">-</div>
                </div>

                <div class="stat">
                    <div class="stat-title">Median</div>
                    <div class="stat-value" id="median">-</div>
                </div>

            </div>

        </div>


        <div class="card">

            <h2>🧠 Analysis</h2>

            <div class="analysis" id="analysis">
            </div>

        </div>


        <div class="card">

            <h2>📈 Recent Results</h2>

            <div class="analysis" id="recent">
            </div>

        </div>

    </div>

</div>


<script>

async function analyze() {

    const history = document.getElementById("history").value;

    const errorBox = document.getElementById("error");
    const resultBox = document.getElementById("result");

    errorBox.style.display = "none";
    resultBox.style.display = "none";

    try {

        const response = await fetch("/api/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                history: history
            })

        });

        const data = await response.json();

        if (!response.ok || data.status === "error") {
            throw new Error(data.message || "Analysis error");
        }

        document.getElementById("count").innerText =
            data.count;

        document.getElementById("average").innerText =
            data.average + "x";

        document.getElementById("minimum").innerText =
            data.minimum + "x";

        document.getElementById("maximum").innerText =
            data.maximum + "x";

        document.getElementById("median").innerText =
            data.median + "x";

        document.getElementById("low").innerText =
            data.below_2x + "%";

        document.getElementById("medium").innerText =
            data.between_2x_5x + "%";

        document.getElementById("high").innerText =
            data.above_5x + "%";

        document.getElementById("analysis").innerHTML =
            data.analysis;

        document.getElementById("recent").innerHTML =
            data.recent.join(" &nbsp; • &nbsp; ");

        resultBox.style.display = "block";

    } catch (error) {

        errorBox.innerText = error.message;
        errorBox.style.display = "block";

    }
}

</script>

</body>
</html>
"""


def parse_history(raw):

    if not raw:
        return []

    raw = raw.replace(",", "\n")
    raw = raw.replace(";", "\n")
    raw = raw.replace("x", "")
    raw = raw.replace("X", "")

    values = []

    for item in raw.splitlines():

        item = item.strip()

        if not item:
            continue

        try:

            value = float(item)

            if math.isfinite(value) and value >= 1:
                values.append(value)

        except ValueError:
            continue

    return values


def percentage(part, total):

    if total == 0:
        return 0

    return round((part / total) * 100, 1)


def build_analysis(values):

    count = len(values)

    low = sum(1 for x in values if x < 2)
    medium = sum(1 for x in values if 2 <= x < 5)
    high = sum(1 for x in values if x >= 5)

    average = statistics.mean(values)
    median = statistics.median(values)

    messages = []

    low_percent = percentage(low, count)
    medium_percent = percentage(medium, count)
    high_percent = percentage(high, count)

    if low_percent >= 60:
        messages.append(
            "عدد كبير من النتائج الموجودة في العينة كان أقل من 2x."
        )
    elif low_percent >= 40:
        messages.append(
            "النتائج الأقل من 2x تمثل نسبة مهمة من العينة."
        )
    else:
        messages.append(
            "النتائج الأقل من 2x ليست الأغلبية في هذه العينة."
        )

    if high_percent >= 15:
        messages.append(
            "العينة تحتوي على عدد ملحوظ من النتائج فوق 5x."
        )
    else:
        messages.append(
            "النتائج فوق 5x قليلة نسبياً داخل هذه العينة."
        )

    if average > median * 1.25:
        messages.append(
            "المتوسط أعلى من الوسيط بشكل واضح، وهذا قد يكون بسبب بعض النتائج المرتفعة."
        )

    if average < median * 0.85:
        messages.append(
            "الوسيط أعلى من المتوسط، ما يشير إلى تأثير بعض النتائج المنخفضة."
        )

    recent = values[-10:]

    if len(recent) >= 5:

        recent_average = statistics.mean(recent)

        if recent_average > average:
            messages.append(
                "متوسط آخر الجولات أعلى من متوسط العينة الكاملة."
            )

        elif recent_average < average:
            messages.append(
                "متوسط آخر الجولات أقل من متوسط العينة الكاملة."
            )

        else:
            messages.append(
                "متوسط آخر الجولات قريب من متوسط العينة."
            )

    messages.append(
        "<b>ملاحظة:</b> هذه المؤشرات تصف البيانات السابقة فقط، "
        "ولا تعني أن الجولة القادمة ستصل إلى مستوى معين."
    )

    return "<br><br>".join(messages)


@app.route("/")
def home():

    return render_template_string(HTML)


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "Crash Analyzer"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "لم يتم إرسال البيانات."
            }), 400

        raw_history = data.get("history", "")

        values = parse_history(raw_history)

        if len(values) < 3:

            return jsonify({
                "status": "error",
                "message": "أدخل على الأقل 3 نتائج، مثل: 1.25, 2.10, 3.40"
            }), 400

        count = len(values)

        low = sum(1 for x in values if x < 2)
        medium = sum(1 for x in values if 2 <= x < 5)
        high = sum(1 for x in values if x >= 5)

        average = statistics.mean(values)
        median = statistics.median(values)

        recent = values[-10:]

        recent_formatted = [
            f"{x:.2f}x"
            for x in recent
        ]

        result = {

            "status": "success",

            "count": count,

            "average": round(average, 2),

            "median": round(median, 2),

            "minimum": round(min(values), 2),

            "maximum": round(max(values), 2),

            "below_2x": percentage(low, count),

            "between_2x_5x": percentage(medium, count),

            "above_5x": percentage(high, count),

            "recent": recent_formatted,

            "analysis": build_analysis(values)
        }

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
# Railway deployment test
