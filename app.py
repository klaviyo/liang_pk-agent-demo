import json
import os
import queue
import threading
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
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


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        q = queue.Queue()

        def progress_callback(step_text):
            q.put(json.dumps({"type": "step", "text": step_text}))

        def run_agent():
            try:
                response = orchestrator.handle_message(user_message)
                q.put(json.dumps({"type": "response", "text": response}))
            except Exception as e:
                import traceback
                error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                app.logger.error(f"Agent error: {error_details}")
                q.put(json.dumps({"type": "error", "text": str(e)}))
            finally:
                q.put(None)

        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

        def generate():
            while True:
                item = q.get()
                if item is None:
                    break
                yield f"data: {item}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
        )
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        'anthropic_key_set': bool(os.getenv('ANTHROPIC_API_KEY')),
        'klaviyo_key_set': bool(os.getenv('KLAVIYO_API_KEY')),
        'klaviyo_key_prefix': os.getenv('KLAVIYO_API_KEY', '')[:8] if os.getenv('KLAVIYO_API_KEY') else 'NOT_SET'
    })


@app.route('/api/debug/klaviyo', methods=['GET'])
def debug_klaviyo():
    """Debug endpoint to test Klaviyo API directly"""
    try:
        from tools import account_lookup
        result = account_lookup.handle({})
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
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
    app.run(debug=True, host='0.0.0.0', port=3000)
