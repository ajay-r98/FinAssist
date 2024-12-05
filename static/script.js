async function sendMessage() {
    const inputField = document.getElementById('userInput');
    const userMessage = inputField.value.trim();

    if (userMessage === '') return;

    // Display user message
    addMessageToChat(userMessage, 'user-message');

    // Clear input field
    inputField.value = '';

    // Send message to Flask server
    const response = await fetch('/get_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });

    const data = await response.json();
    const botMessage = data.response;

    // Display bot response
    addMessageToChat(botMessage, 'bot-message');
}

// Function to add a message to the chatbox
function addMessageToChat(message, className) {
    const chatbox = document.getElementById('chatbox');
    const messageBubble = document.createElement('div');
    messageBubble.className = className;
    messageBubble.textContent = message;
    chatbox.appendChild(messageBubble);
    chatbox.scrollTop = chatbox.scrollHeight;  // Scroll to the bottom
}

// Function to send message on Enter key press
function checkEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}
