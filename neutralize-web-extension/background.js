chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "analyzeText") {
        console.log("Received text:", message.text);
        // Here you can send it to your bias detection API
    }
});
