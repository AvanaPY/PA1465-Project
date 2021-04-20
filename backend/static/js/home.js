const testDataInput = document.getElementById("testDataInput");
const resultSpan = document.getElementById("result");

const ctx = document.getElementById('myChart').getContext('2d')
var chart;

const data = []
const labels= []
const classification = []

const updateChart = (value) => {
    data.push(value);
    labels.push(labels.length);
    chart.update();
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
    const file = document.getElementById("image-file").files[0];
    if (file !== undefined){
        const formData = new FormData()
        formData.append("file", file);
        fetch('/upload/dataset', {
            method: 'POST',
            body: formData
        }).then((response) => 
            response.json()
        ).then((response) => {
            console.log(response);
        });
    }
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
    const retrainResult = document.getElementById('retrainModelErrorPlaceholder');

    let receivedResponse = false;
    let message;
    let loopFunction = (n) => {
        if(receivedResponse) {
            retrainResult.innerText = message;
            btn.innerHTML = tmp;
        } else {
            btn.innerHTML = "Waiting" + ".".repeat(n);
            setTimeout(() => loopFunction(1 + n % 4), 500);
        }
    }

    loopFunction(0)
    btn.innerText = "Waiting..."
    const response = await fetch("/api/retrain", {
        method: 'POST'
    }).then((response) => response.json()
    ).then((response) => {
        message = response["message"];
        receivedResponse = true;
    });
}

const bulkClassify = () => {
    console.log("Not yet implemented!");
}

chartIt();
