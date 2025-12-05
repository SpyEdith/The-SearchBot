import os
import sys
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# 1. Force load the .env file from the backend folder
backend_folder = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_folder, ".env")
load_dotenv(dotenv_path=env_path)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# 2. Debug: Print the API Key status when server starts
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GROQ_API_KEY is missing! Check your .env file.", file=sys.stderr)
else:
    print(f"SUCCESS: GROQ_API_KEY loaded ({api_key[:5]}...)", file=sys.stderr)

client = Groq(api_key=api_key)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # 3. WRAP EVERYTHING in a big Try/Except to catch every crash
    try:
        data = request.json
        # Safety Check: Did we receive data?
        if not data:
            print("ERROR: Received empty JSON data", file=sys.stderr)
            return jsonify({"error": "Invalid JSON received"}), 400
        
        user_message = data.get('message')

        if not user_message:
            print("ERROR: No 'message' field in JSON", file=sys.stderr)
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message: {user_message}", file=sys.stderr)

        # 4. Talk to Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192", 
        )
        
        ai_response = chat_completion.choices[0].message.content
        return jsonify({"reply": ai_response})

    except Exception as e:
        # 5. PRINT THE ACTUAL ERROR TRACEBACK
        print("--------------------------------------------------", file=sys.stderr)
        print("CRASH OCCURRED:", file=sys.stderr)
        traceback.print_exc() # <--- This prints the exact line number of the error
        print("--------------------------------------------------", file=sys.stderr)
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}...", file=sys.stderr)
    app.run(host='0.0.0.0', port=port)
