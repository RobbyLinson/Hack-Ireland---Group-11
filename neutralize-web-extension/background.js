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
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendURL") {
        fetch("https://your-backend-api.com/analyze-url", {  // Replace with your actual backend URL
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: message.url })
        })
        .then(response => response.json())
        .then(data => console.log("Server Response:", data))
        .catch(error => console.error("Error sending URL:", error));
    }
});
