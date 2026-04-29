# Klaviyo Customer Support Agent

AI-powered customer support chatbot with web UI and feedback system.

## Features

✅ **Modern Chat Interface** - Clean, ChatGPT-style UI with Klaviyo branding
✅ **Real-time Responses** - Powered by Claude AI (Anthropic)
✅ **Feedback System** - Thumbs up/down on each response
✅ **Responsive Design** - Works on desktop and mobile
✅ **Typing Indicators** - Visual feedback while agent is thinking

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run the Application

#### Web UI (Recommended)

```bash
python app.py
```

Then open your browser to: http://localhost:5000

#### CLI Version

```bash
python main.py
```

## Usage

### Web Interface

1. Start the server: `python app.py`
2. Open http://localhost:5000 in your browser
3. Type your question and press Enter (or click the send button)
4. View the agent's response
5. Provide feedback with 👍 or 👎 buttons

### Features

- **Klaviyo Branding**: Teal/green color scheme (#1DB393)
- **Smart Formatting**: Supports line breaks and basic markdown
- **Auto-resize**: Text input grows as you type
- **Keyboard Shortcuts**:
  - Enter to send
  - Shift+Enter for new line

## Architecture

```
├── app.py              # Flask web server
├── main.py             # CLI version
├── agent/              # Agent orchestrator logic
├── subagents/          # Specialized agent modules
├── tools/              # Tool implementations
├── templates/          # HTML templates
│   └── index.html      # Main chat UI
└── static/             # Static assets
    ├── style.css       # Klaviyo-branded styles
    └── script.js       # Chat functionality
```

## API Endpoints

### POST /api/chat

Send a message to the agent.

**Request:**
```json
{
  "message": "How do I create a campaign?"
}
```

**Response:**
```json
{
  "response": "To create a campaign...",
  "status": "success"
}
```

### POST /api/feedback

Submit feedback on a response.

**Request:**
```json
{
  "message_id": "msg-1",
  "feedback": "up",
  "message": "User's question",
  "response": "Agent's response"
}
```

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development
python app.py
```

## Tech Stack

- **Backend**: Flask (Python web framework)
- **AI**: Anthropic Claude API
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Custom CSS with Klaviyo branding

## License

Internal use only - Klaviyo organization
