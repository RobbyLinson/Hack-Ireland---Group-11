// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//     if (message.action === "requestBiasData") {
//         // Simulate API response (replace with real API call)
//         const biasData = {
//             Left: 0.1135561540722847,
//             Center: 0.02761225588619709,
//             Right: 0.858831524848938
//         };

//         sendResponse({ bias: biasData });
//     }
// });
let globalUrl
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendURL") {
        fetch("http://127.0.0.1:5000/scrape", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: message.url })
        })
        .then(response => response.json())
        .then(data => {
            chrome.storage.local.set({ scrapedData: data });
        })
        .catch(error => console.error("Error fetching bias data:", error));
        globalUrl = url
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "requestBiasData") {
        chrome.storage.local.get("scrapedData", (data) => {
            sendResponse(data.scrapedData || { error: globalUrl });
        });
        return true; // Required to use `sendResponse` asynchronously
    }
});

