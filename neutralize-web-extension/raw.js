document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.local.get('ScrapedText', (result) => {
        if (result.ScrapedText) {
            document.getElementById('title').textContent = result.ScrapedText.title || "Raw Text";
            document.getElementById('text').textContent = result.ScrapedText.text || "No content available.";
        } else {
            document.getElementById('text').textContent = "No scraped text found.";
        }
    });
});
