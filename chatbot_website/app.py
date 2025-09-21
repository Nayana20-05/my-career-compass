from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from nlp_model import get_response

# --- 1. APP SETUP ---
app = Flask(__name__)
# This enables Cross-Origin Resource Sharing, which is important for security
# and allows your frontend to talk to your backend.
CORS(app) 


# --- 2. DEFINE APP ROUTES (URLS) ---

@app.route("/")
def home():
    """
    This route serves the main HTML page of the chat application.
    When you go to http://127.0.0.1:5000/, this function runs.
    """
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    This is the API endpoint that the frontend JavaScript will call.
    It receives the user's message and a unique user_id,
    then sends them to the chatbot brain (nlp_model.py) to get a response.
    """
    user_message = request.json.get("message")
    user_id = request.json.get("user_id")

    # Basic error checking
    if not user_message or not user_id:
        return jsonify({"error": "A 'message' or 'user_id' is missing from the request."}), 400

    # Get the response from our chatbot brain
    bot_response = get_response(user_message, user_id)
    
    # Send the response back to the frontend
    return jsonify({"response": bot_response})


# --- 3. RUN THE APP ---
if __name__ == "__main__":
    # This makes the server run when you execute `python app.py`
    app.run(debug=True)
