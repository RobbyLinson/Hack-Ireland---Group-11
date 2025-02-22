document.addEventListener('DOMContentLoaded', () => {
    // Retrieve the bias analysis data from storage
    chrome.storage.local.get('biasAnalysis', (result) => {
        if (result.biasAnalysis) {
            console.log("Bias Analysis", result.biasAnalysis);
            updatePopupContent(result.biasAnalysis);
        } else {
            console.log("No bias analysis data found.");
        }
    });
    document.getElementById("button1").addEventListener("click", async () => {
        console.log("Button 1 Pressed")
        try {
            // Retrieve the bias analysis data from storage
            const result = await chrome.storage.local.get('biasAnalysis');
            if (result.biasAnalysis) {
                const biasData = result.biasAnalysis;

                // Construct the payload
                const payload = {
                    text: biasData.text, // Ensure 'text' is stored in biasAnalysis
                    bias_level: biasData.bias_analysis
                };

                // Make the POST request
                const response = await fetch('https://0641-89-101-154-45.ngrok-free.app/api/gpt_analyze/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const responseData = await response.json();
                console.log('API Response:', responseData);

            } else {
                console.error('No bias analysis data found.');
            }
        } catch (error) {
            console.error('Error during API call:', error);
        }
    });


    document.getElementById("button2").addEventListener("click", () => {
        console.log("Button 2 clicked");
        // Add button 2 functionality here
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

