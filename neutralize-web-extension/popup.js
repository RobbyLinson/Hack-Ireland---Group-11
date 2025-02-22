document.getElementById("analyze-btn").addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "requestBiasData" }, (response) => {
        if (response && response.bias) {
            updateBiasResults(response.bias);
        }
    });
});

function updateBiasResults(biasData) {
    const leftScore = Math.round(biasData.Left * 100);
    const centerScore = Math.round(biasData.Center * 100);
    const rightScore = Math.round(biasData.Right * 100);

    document.getElementById("left-bar").style.width = leftScore + "%";
    document.getElementById("center-bar").style.width = centerScore + "%";
    document.getElementById("right-bar").style.width = rightScore + "%";

    document.getElementById("left-score").innerText = leftScore + "%";
    document.getElementById("center-score").innerText = centerScore + "%";
    document.getElementById("right-score").innerText = rightScore + "%";
}
