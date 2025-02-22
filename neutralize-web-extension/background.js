chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendURL") {
        fetch("http://127.0.0.1:5000/scrape", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: message.url })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json(); // Parse the JSON from the response
        })
        .then(data => {
            console.log("Scraped Data:", data);

            if (!data.text) {
                throw new Error("Scraped data does not contain 'text' field.");
            }

            // Store the scraped text
            chrome.storage.local.set({ ScrapedText: data.text }, () => {
                if (chrome.runtime.lastError) {
                    console.error("Error setting ScrapedText:", chrome.runtime.lastError);
                    return;
                }
                console.log("Scraped text saved.");

                // Proceed to send the text to the Next API
                const nextApiUrl = "https://0641-89-101-154-45.ngrok-free.app/api/analyze/";
                console.log("Sending data to Next API at:", nextApiUrl);
                fetch(nextApiUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text: data.text })
                })
                .then(res => {
                    if (!res.ok) {
                        throw new Error(`HTTP error! Status: ${res.status}`);
                    }
                    return res.json();
                })
                .then(response => {
                    console.log("Response from Next API:", response);
                    chrome.storage.local.set({ biasAnalysis: response }, () => {
                        if (chrome.runtime.lastError) {
                            console.error("Error setting biasAnalysis:", chrome.runtime.lastError);
                            return;
                        }
                        console.log("Bias analysis data saved.");
                    });
                })
                .catch(error => console.error("Error during Next API fetch:", error));
            });
        })
        .catch(error => console.error("Error during scraping fetch:", error));
    }
});
