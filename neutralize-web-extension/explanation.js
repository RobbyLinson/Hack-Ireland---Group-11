document.addEventListener('DOMContentLoaded', () => {
    // Retrieve the explanation data from chrome.storage.local
    chrome.storage.local.get('explanation', (result) => {
        if (result.explanation) {
            const explanationText = result.explanation;
            // Use Marked.js to convert markdown to HTML
            document.getElementById('content').innerHTML = marked.parse(explanationText);
        } else {
            console.error('No explanation found in storage.');
            document.getElementById('content').textContent = 'No explanation available.';
        }
    });
});
