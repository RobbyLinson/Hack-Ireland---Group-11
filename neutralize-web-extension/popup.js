document.addEventListener('DOMContentLoaded', () => {
    // Retrieve the bias analysis data from storage
    chrome.storage.local.get(['ScrapedText', 'biasAnalysis'], (result) => {
        if (result.ScrapedText && result.biasAnalysis) {
            console.log("ScrapedText:", result.ScrapedText);
            console.log("Bias Analysis:", result.biasAnalysis);

            // Store ScrapedText in a variable
            const scrapedText = result.ScrapedText;  // Fix here

            console.log("Claimed Text Data: ", scrapedText); // Now defined
            console.log("Claimed Bias Data: ", result.biasAnalysis.bias_analysis);
        } else {
            console.log("Required data not found in storage.");
        }
    });


    chrome.storage.local.get('biasAnalysis', (result) => {
        if (result.biasAnalysis) {
            console.log("Bias Analysis", result.biasAnalysis);
            updatePopupContent(result.biasAnalysis);
        } else {
            console.log("No bias analysis data found.");
        }
    });
    document.getElementById("button1").addEventListener("click", async () => {
        console.log("Button 1 Pressed");
        try {
            const result = await chrome.storage.local.get(['ScrapedText', 'biasAnalysis']);
            if (result.ScrapedText && result.biasAnalysis) {
                const biasData = result.biasAnalysis;
                const scrapedText = result.ScrapedText; // Correct retrieval
    
                console.log("All Bias Data: ", biasData);
                console.log("Claimed Text Data: ", scrapedText); // Fixed usage
                console.log("Claimed Bias Data: ", biasData.bias_analysis);
    
                const payload = {
                    text: scrapedText, // Use the correct variable
                    bias_level: biasData.bias_analysis
                };
    
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
    // Update text content with validated values
    document.getElementById("center-score").textContent = getValidPercentage(biasData.bias_analysis.Middle);
    document.getElementById("left-score").textContent = getValidPercentage(biasData.bias_analysis.Left);
    document.getElementById("right-score").textContent = getValidPercentage(biasData.bias_analysis.Right);

    // Update progress bars with validated widths
    document.getElementById("center-bar").style.width = getValidPercentage(biasData.bias_analysis.Middle);
    document.getElementById("left-bar").style.width = getValidPercentage(biasData.bias_analysis.Left);
    document.getElementById("right-bar").style.width = getValidPercentage(biasData.bias_analysis.Right);
}

