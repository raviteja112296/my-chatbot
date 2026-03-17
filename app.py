from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from google import genai
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in environment variables")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)


# 🔥 HOME ROUTE (HTML PAGE)
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# 🔥 CHAT API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"reply": "Invalid JSON body."}), 400

    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Message cannot be empty."}), 400

    if len(user_input) > 4000:
        return jsonify({"reply": "Message too long."}), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_input,
        )

        reply = response.text or "No response received."

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"[Gemini Error] {type(e).__name__}: {e}")
        return jsonify({"reply": "Server error. Try again."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run()