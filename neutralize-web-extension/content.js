(() => {
    window.addEventListener("load", () => {
        let url = window.location.href;
        console.log("URL Acquired: ", url)
        chrome.runtime.sendMessage({ action: "sendURL", url });
    });
})();
