
const canvas =
    document.getElementById("chart");

const ctx =
    canvas.getContext("2d");



function drawChart(values) {

    const dpr =
        window.devicePixelRatio || 1;

    const w =
        canvas.clientWidth;

    const h =
        canvas.clientHeight;


    canvas.width = w * dpr;

    canvas.height = h * dpr;


    ctx.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
    );


    ctx.clearRect(
        0,
        0,
        w,
        h
    );


    if (!values.length) {
        return;
    }


    const max =
        Math.max(...values, 2);


    const padding = 15;


    const step =
        (w - padding * 2) /
        Math.max(values.length - 1, 1);


    ctx.beginPath();


    values
        .slice()
        .reverse()
        .forEach((value, index) => {

            const x =
                padding +
                index * step;


            const y =
                h -
                padding -
                (
                    Math.min(value, max) /
                    max
                ) *
                (h - padding * 2);


            if (index === 0) {

                ctx.moveTo(x, y);

            } else {

                ctx.lineTo(x, y);

            }

        });


    ctx.strokeStyle =
        "#ffd027";

    ctx.lineWidth = 3;

    ctx.stroke();
}




function render(data) {

    const analysis =
        data.analysis;


    document.getElementById(
        "live"
    ).textContent =
        data.history[0]
            ? data.history[0].toFixed(2) + "x"
            : "—";


    document.getElementById(
        "avg"
    ).textContent =
        analysis.average;


    document.getElementById(
        "med"
    ).textContent =
        analysis.median;


    document.getElementById(
        "under"
    ).textContent =
        analysis.under2;


    document.getElementById(
        "over"
    ).textContent =
        analysis.over2;


    document.getElementById(
        "risk"
    ).textContent =
        "مستوى المخاطرة: " +
        analysis.risk;



    const container =
        document.getElementById(
            "history"
        );


    container.innerHTML = "";


    data.history.forEach(
        value => {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "pill " +
                (
                    value < 2
                        ? "low"
                        : "high"
                );


            div.textContent =
                value.toFixed(2) + "x";


            container.appendChild(
                div
            );

        }
    );


    drawChart(
        data.history
    );
}




async function load() {

    const response =
        await fetch(
            "/api/history"
        );


    const data =
        await response.json();


    render(data);
}




async function addResult() {

    const input =
        document.getElementById(
            "value"
        );


    const value =
        input.value;


    if (!value) {
        return;
    }


    const response =
        await fetch(
            "/api/add",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    value: value
                })
            }
        );


    if (response.ok) {

        const data =
            await response.json();


        render(data);


        input.value = "";

    }

}


window.addEventListener(
    "resize",
    load
);


load();
