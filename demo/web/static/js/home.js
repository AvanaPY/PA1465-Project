const testDataInput = document.getElementById("testDataInput");
const resultSpan = document.getElementById("result");

const ctx = document.getElementById('myChart').getContext('2d')
var chart;

const data = []
const labels= []
const classification = []

const generateTimeLabels = (data) => {
    const labels = []
    var v = 0;
    data.forEach((value, index) => {
        labels.push(String(v));
        v++;
    })
    return labels;
}

const updateChart = (value) => {
    data.push(value);
    labels.push(labels.length);
    chart.update();

    console.log(data, labels);
}

const chartIt = async () => {
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, 
            datasets: [
                {
                    borderColor: 'rgba(255, 100, 100)',
                    fill: false,
                    label: 'AI classification',
                    data: data
                }
            ]
        },
        options: {
            responsive: true,
            hover: {
                mode: 'nearest',
                intersect: true
            },
            
        }
    });
}

const uploadData = () => {
    console.log("Function uploadData() is not yet implemented.");
}

const testData = () => {
    const value = testDataInput.value;
    if(value) {
        fetch("api/predict/" + value)
            .then(response => {
                return response.json();
            }).then(response => {
                const status = response.status
                if (status === "ok") {
                    const confidence = response.confidence;
                    const result = response.result;
                    updateChart(parseFloat(value));
                    resultSpan.innerText = `The value ${value} is considered ${result} with confidence ${confidence}.`
                }
                else {
                    resultSpan.innerText = response.message;
                }
            });
    }
}

const retrainModel = async () => {
    const btn = document.getElementById('retrainModelBtnSpan')
    const tmp = btn.innerText;
    btn.innerText = "Waiting..."
    const response = await fetch("/api/retrain", {
        method: 'POST'
    }).then((response) => 
        response.json()
    ).then((response) => {
        const status = response["status"];
        const message = response["message"]
        const retrainResult = document.getElementById('retrainModelErrorPlaceholder');
        btn.innerText = tmp;
        retrainResult.innerText = message;
    });
}

chartIt();