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

    // Show progress indicator
    const progressId = showProgressIndicator();

    try {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split('\n\n');
            buffer = parts.pop();

            for (const part of parts) {
                if (!part.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(part.slice(6));
                    if (data.type === 'step') {
                        updateProgressStep(progressId, data.text);
                    } else if (data.type === 'response') {
                        removeProgressIndicator(progressId);
                        addMessage(data.text, 'agent', message);
                    } else if (data.type === 'error') {
                        removeProgressIndicator(progressId);
                        addMessage('I apologize, but I encountered an error. Please try again or contact support@klaviyo.com.', 'agent');
                    }
                } catch (e) {
                    // Ignore malformed SSE chunks
                }
            }
        }
    } catch (error) {
        removeProgressIndicator(progressId);
        addMessage('I apologize, but I encountered a connection error. Please check your internet connection and try again.', 'agent');
    }

    // Re-enable input
    setInputState(true);
    userInput.focus();
}

// Show progress indicator with agent avatar
function showProgressIndicator() {
    const progressId = `progress-${Date.now()}`;
    const progressDiv = document.createElement('div');
    progressDiv.className = 'message agent';
    progressDiv.id = progressId;
    progressDiv.innerHTML = `
        <div class="agent-avatar">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="20" fill="#1DB393"/>
                <text x="20" y="27" font-size="20" fill="white" text-anchor="middle" font-family="Arial">K</text>
            </svg>
        </div>
        <div class="message-wrapper">
            <div class="progress-indicator">
                <div class="progress-steps"></div>
            </div>
        </div>
    `;
    chatContainer.appendChild(progressDiv);
    scrollToBottom();
    return progressId;
}

// Update or add the current step, marking previous ones as completed
function updateProgressStep(progressId, stepText) {
    const progressDiv = document.getElementById(progressId);
    if (!progressDiv) return;

    const stepsContainer = progressDiv.querySelector('.progress-steps');

    // Mark the previous active step as completed
    const activeStep = stepsContainer.querySelector('.progress-step.active');
    if (activeStep) {
        activeStep.classList.remove('active');
        activeStep.classList.add('completed');
        const icon = activeStep.querySelector('.step-icon');
        if (icon) {
            icon.innerHTML = `<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 7L5.5 10.5L12 3.5" stroke="#1DB393" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>`;
        }
    }

    // Add new active step
    const stepDiv = document.createElement('div');
    stepDiv.className = 'progress-step active';
    stepDiv.innerHTML = `
        <span class="step-icon"><div class="step-spinner"></div></span>
        <span class="step-text">${escapeHtml(stepText)}</span>
    `;
    stepsContainer.appendChild(stepDiv);
    scrollToBottom();
}

// Remove progress indicator
function removeProgressIndicator(progressId) {
    const el = document.getElementById(progressId);
    if (el) el.remove();
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
