(() => {
    window.addEventListener("load", () => {
        let pageUrl = window.location.href; 
        chrome.runtime.sendMessage({ action: "sendURL", url: pageUrl });
    });
})();
