let messageCounter = 0;

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Send message on Enter (Shift+Enter for new line)
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendButton.addEventListener('click', sendMessage);

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();

    if (!message) return;

    // Disable input while processing
    setInputState(false);

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        // Send to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.status === 'success') {
            // Add agent response with feedback buttons
            addMessage(data.response, 'agent', message);
        } else {
            addMessage('I apologize, but I encountered an error. Please try again or contact support@klaviyo.com.', 'agent');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('I apologize, but I encountered a connection error. Please check your internet connection and try again.', 'agent');
    }

    // Re-enable input
    setInputState(true);
    userInput.focus();
}

// Add message to chat
function addMessage(text, sender, userMessage = null) {
    messageCounter++;
    const messageId = `msg-${messageCounter}`;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.id = messageId;

    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="avatar user-avatar">U</div>
            <div class="message-wrapper">
                <div class="message-content">${escapeHtml(text)}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="agent-avatar">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="20" fill="#1DB393"/>
                    <text x="20" y="27" font-size="20" fill="white" text-anchor="middle" font-family="Arial">K</text>
                </svg>
            </div>
            <div class="message-wrapper">
                <div class="message-content">${formatMessage(text)}</div>
                <div class="feedback-buttons">
                    <button class="feedback-btn thumbs-up" onclick="sendFeedback('${messageId}', 'up', '${escapeHtml(userMessage)}', '${escapeHtml(text)}')">
                        👍 Helpful
                    </button>
                    <button class="feedback-btn thumbs-down" onclick="sendFeedback('${messageId}', 'down', '${escapeHtml(userMessage)}', '${escapeHtml(text)}')">
                        👎 Not helpful
                    </button>
                </div>
            </div>
        `;
    }

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Format message (preserve line breaks, etc.)
function formatMessage(text) {
    return escapeHtml(text)
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTypingIndicator() {
    const typingId = `typing-${Date.now()}`;
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message agent';
    typingDiv.id = typingId;
    typingDiv.innerHTML = `
        <div class="agent-avatar">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="20" fill="#1DB393"/>
                <text x="20" y="27" font-size="20" fill="white" text-anchor="middle" font-family="Arial">K</text>
            </svg>
        </div>
        <div class="message-wrapper">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    scrollToBottom();
    return typingId;
}

// Remove typing indicator
function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Send feedback
async function sendFeedback(messageId, feedbackType, userMessage, agentResponse) {
    const messageElement = document.getElementById(messageId);
    const buttons = messageElement.querySelectorAll('.feedback-btn');

    // Update button states
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if ((feedbackType === 'up' && btn.classList.contains('thumbs-up')) ||
            (feedbackType === 'down' && btn.classList.contains('thumbs-down'))) {
            btn.classList.add('active');
        }
    });

    try {
        await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message_id: messageId,
                feedback: feedbackType,
                message: userMessage,
                response: agentResponse
            }),
        });
    } catch (error) {
        console.error('Error sending feedback:', error);
    }
}

// Set input state (enabled/disabled)
function setInputState(enabled) {
    userInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

// Scroll to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Initial focus
userInput.focus();
