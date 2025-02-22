// popup.js

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "biasAnalysis" && message.data) {
        // Update the popup with the received data
        updatePopupContent(message.data);
    }
});

// Function to update the popup content
function updatePopupContent(biasData) {
    document.getElementById("center-score").textContent = (biasData.Center * 100).toFixed(2) + "%";
    document.getElementById("left-score").textContent = (biasData.Left * 100).toFixed(2) + "%";
    document.getElementById("right-score").textContent = (biasData.Right * 100).toFixed(2) + "%";

    // Update the progress bars
    document.getElementById("center-bar").style.width = (biasData.Center * 100) + "%";
    document.getElementById("left-bar").style.width = (biasData.Left * 100) + "%";
    document.getElementById("right-bar").style.width = (biasData.Right * 100) + "%";
}


document.addEventListener('DOMContentLoaded', () => {
    // Request the latest bias analysis data from the background script
    chrome.runtime.sendMessage({ action: "getLatestBiasAnalysis" }, (response) => {
        if (response && response.data) {
            updatePopupContent(response.data);
        }
    });
});
