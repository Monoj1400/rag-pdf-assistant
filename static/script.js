// 1. Handle PDF Upload
async function uploadPDF() {
    const fileInput = document.getElementById('pdf-upload');
    const statusDiv = document.getElementById('upload-status');
    const uploadBtn = document.getElementById('upload-btn');

    if (fileInput.files.length === 0) {
        alert("Please select a PDF file first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled = true;
    statusDiv.innerText = "Processing PDF... (this may take a moment)";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (response.ok) {
            statusDiv.innerText = `✅ ${data.message}`;
            addMessage("bot", `I have read ${data.filename}. What would you like to know?`);
        } else {
            statusDiv.innerText = `❌ Error: ${data.error}`;
        }
    } catch (error) {
        statusDiv.innerText = "❌ Server error during upload.";
    } finally {
        uploadBtn.disabled = false;
    }
}

// 2. Handle Asking Questions
async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const question = inputField.value.trim();
    const sendBtn = document.getElementById('send-btn');

    if (!question) return;

    // Add user message to UI
    addMessage("user", question);
    inputField.value = '';
    
    // Show loading state
    sendBtn.disabled = true;
    const loadingDiv = addMessage("bot", "Thinking...");

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        const data = await response.json();

        // Remove loading message
        loadingDiv.remove();

        if (response.ok) {
            let botText = data.answer;
            if (data.sources && data.sources.length > 0) {
                botText += `<span class="sources">Sources: Page(s) ${data.sources.join(', ')}</span>`;
            }
            addMessage("bot", botText, true);
        } else {
            addMessage("bot", `Error: ${data.error}`);
        }
    } catch (error) {
        loadingDiv.remove();
        addMessage("bot", "Server error. Is Flask running?");
    } finally {
        sendBtn.disabled = false;
    }
}

// 3. UI Helper Functions
function addMessage(sender, text, isHTML = false) {
    const chatContainer = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    
    if (isHTML) {
        msgDiv.innerHTML = text;
    } else {
        msgDiv.innerText = text;
    }
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv; // Return so we can remove loading message later
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}