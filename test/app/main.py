import dotenv
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import queue

from .gen import run_chat

app = Flask(__name__)
cors=CORS(app)

chat_status = "ended"  

# Queues for single-user setup
print_queue = queue.Queue()
user_queue = queue.Queue()


@app.route('/api/start_chat', methods=['POST', 'OPTIONS']) 
def start_chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    elif request.method == 'POST':
        global chat_status
        try:
            if chat_status == 'error':
                chat_status = 'ended' 
            with print_queue.mutex:
                print_queue.queue.clear()
            with user_queue.mutex:
                user_queue.queue.clear()
            chat_status = 'Chat ongoing'

            thread = threading.Thread(
                target=run_chat, 
                args=(request.json, print_queue, user_queue),
            )
            thread.start()
            return jsonify({'status': chat_status})
        except Exception as e:
            return jsonify({'status': 'Error occurred', 'error': str(e)})
          
@app.route('/api/send_message', methods=['POST'])
def send_message():
    user_input = request.json['message']
    user_queue.put(user_input)
    return jsonify({'status': 'Message Received'})

@app.route('/api/get_message', methods=['GET'])
def get_messages():
    global chat_status 

    if not print_queue.empty():
        msg = print_queue.get()  
        return jsonify({'message': msg, 'chat_status': chat_status}), 200
    else:
        return jsonify({'message': None, 'chat_status': chat_status}), 200
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5008, debug=True)