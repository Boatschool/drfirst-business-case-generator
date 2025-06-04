// Browser extension popup script
document.addEventListener('DOMContentLoaded', function() {
  // Get references to buttons
  const openAppBtn = document.getElementById('openApp');
  const generateCaseBtn = document.getElementById('generateCase');
  const viewHistoryBtn = document.getElementById('viewHistory');

  // Open main application
  openAppBtn.addEventListener('click', function() {
    chrome.tabs.create({
      url: 'http://localhost:4000' // Development URL
    });
  });

  // Generate business case from current page
  generateCaseBtn.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      // TODO: Extract content from current page and send to backend
      chrome.scripting.executeScript({
        target: {tabId: tabs[0].id},
        function: extractPageContent
      }, function(results) {
        if (results && results[0]) {
          // TODO: Send extracted content to backend API
          console.log('Extracted content:', results[0].result);
        }
      });
    });
  });

  // View generation history
  viewHistoryBtn.addEventListener('click', function() {
    chrome.tabs.create({
      url: 'http://localhost:4000/history' // Development URL
    });
  });
});

// Function to extract relevant content from the current page
function extractPageContent() {
  // TODO: Implement intelligent content extraction
  return {
    title: document.title,
    url: window.location.href,
    content: document.body.innerText.substring(0, 1000), // First 1000 chars
    timestamp: new Date().toISOString()
  };
} 