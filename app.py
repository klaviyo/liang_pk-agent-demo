import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from anthropic import Anthropic
from agent.orchestrator import Orchestrator

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize Anthropic client and orchestrator
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = Anthropic(api_key=api_key)
orchestrator = Orchestrator(client)

# Store feedback data
feedback_data = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get response from orchestrator
        response = orchestrator.handle_message(user_message)

        return jsonify({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        message_id = data.get('message_id')
        feedback_type = data.get('feedback')  # 'up' or 'down'
        message = data.get('message')
        response = data.get('response')

        feedback_data.append({
            'message_id': message_id,
            'feedback': feedback_type,
            'user_message': message,
            'agent_response': response
        })

        return jsonify({
            'status': 'success',
            'message': 'Feedback recorded'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
