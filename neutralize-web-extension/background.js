// background.js
let latestBiasAnalysis = null;
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendURL") {
        fetch("http://127.0.0.1:5000/scrape", {  // Python API for scraping
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: message.url })
        })
        .then(response =>{ 
            console.log("Response: ",response)
            return response.json()
        })
        .then(data => {
            console.log("Scraped Data:", data); // Log the scraped data

            // Now send the data elsewhere
            const nextApiUrl = "https://0641-89-101-154-45.ngrok-free.app/api/analyze/"; // Update this URL as needed
            console.log("Sending data to Next API at:", nextApiUrl); // Log the Next API URL
            fetch(nextApiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: data.text })
            })
            .then(res => res.json())
            .then(response => {
                console.log("Response from Next API:", response); // Log the response from the Next API
                chrome.runtime.sendMessage({
                    action: "biasAnalysis",
                    data: analysis
                });
            })
            .catch(error => console.error("Error sending data to Next API:", error));

        })
        .catch(error => console.error("Error fetching scraped data:", error));
        
    }
});