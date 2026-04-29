import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from anthropic import Anthropic
from agent.orchestrator import Orchestrator
from functools import wraps

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'demo-secret-key-change-in-production')
CORS(app)

# Password protection
APP_PASSWORD = os.getenv('APP_PASSWORD', 'demo8888')

def require_password(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize Anthropic client and orchestrator
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = Anthropic(api_key=api_key)
orchestrator = Orchestrator(client)

# Store feedback data
feedback_data = []


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.json.get('password') if request.is_json else request.form.get('password')
        if password == APP_PASSWORD:
            session['authenticated'] = True
            return jsonify({'success': True}) if request.is_json else redirect(url_for('index'))
        return jsonify({'error': 'Invalid password'}), 401 if request.is_json else redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
@require_password
def index():
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
@require_password
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
@require_password
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
    app.run(debug=True, host='0.0.0.0', port=3000)
