document.addEventListener('DOMContentLoaded', () => {
    // Retrieve the bias analysis data from storage
    console.log("IM ALIVE")
    chrome.storage.local.get('biasAnalysis', (result) => {
        if (result.biasAnalysis) {
            console.log("Bias Analysis", result.biasAnalysis);
            updatePopupContent(result.biasAnalysis);
        } else {
            console.log("No bias analysis data found.");
        }
    });
});


function updatePopupContent(biasData) {
    // Helper function to validate and retrieve property values
    function getValidPercentage(value) {
        return (typeof value === 'number' && !isNaN(value)) ? (value * 100).toFixed(0) + "%" : "0.00%";
    }
    console.log("Bias Data: ", biasData)
    console.log("Bias Data: ", biasData.bias_analysis)
    console.log("Bias Data: ", biasData.Middle)
    // Update text content with validated values
    document.getElementById("center-score").textContent = getValidPercentage(biasData.bias_analysis.Middle);
    document.getElementById("left-score").textContent = getValidPercentage(biasData.bias_analysis.Left);
    document.getElementById("right-score").textContent = getValidPercentage(biasData.bias_analysis.Right);

    // Update progress bars with validated widths
    document.getElementById("center-bar").style.width = getValidPercentage(biasData.bias_analysis.Middle);
    document.getElementById("left-bar").style.width = getValidPercentage(biasData.bias_analysis.Left);
    document.getElementById("right-bar").style.width = getValidPercentage(biasData.bias_analysis.Right);
}

