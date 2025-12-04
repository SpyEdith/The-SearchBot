import os
from flask import Flask, request, jsonify, send_from_directory # <--- 1. Added send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# <--- 2. UPDATED: Tells Flask where to find your frontend HTML files
# We assume 'frontend' is one folder up from 'backend'
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# <--- 3. ADDED: The Home Page Route
# When user opens the site, serve index.html
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_message}
            ],
            # I switched this back to a standard Groq model to ensure it works
            model="llama3-8b-8192", 
        )
        
        ai_response = chat_completion.choices[0].message.content
        return jsonify({"reply": ai_response})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # KEPT YOUR CONFIGURATION EXACTLY AS REQUESTED
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
