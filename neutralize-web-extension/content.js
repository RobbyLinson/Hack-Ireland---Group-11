(() => {
    let text = document.body.innerText;
    chrome.runtime.sendMessage({ action: "analyzeText", text });
})();
