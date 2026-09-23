# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app)  # Allows the frontend to talk to this server

# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_message = data.get('message')

#     if not user_message:
#         return jsonify({"error": "No message provided"}), 400

#     try:
#         # This is where the Backend talks to Groq securely
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {"role": "user", "content": user_message}
#             ],
#             model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), # You can change models here
#             # model = "llama3-8b-8192"
#         )
        
#         ai_response = chat_completion.choices[0].message.content
#         return jsonify({"reply": ai_response})

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"error": "Internal Server Error"}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Backend is running",
        "message": "SearchBot API is working"
    })


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({
            "error": "No message provided"
        }), 400

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-20b"
            ),
        )

        ai_response = chat_completion.choices[0].message.content

        return jsonify({
            "reply": ai_response
        })

    except Exception as e:
        print(f"Error: {e}")

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000))
    )