from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os

app = Flask(__name__)
CORS(app)

# ── Load API key from environment (never hardcode) ──────────────────
# Before running, set in terminal:
#   Windows : set GEMINI_API_KEY=your_key_here
#   Mac/Linux: export GEMINI_API_KEY=your_key_here
# OR create a .env file and use python-dotenv (see bottom of file)

API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDO4nhg8w0XGyA6dWl3Lq4Ce60sRkhnENc")  # fallback for local dev only
client = genai.Client(api_key=API_KEY)

# ── Optional: keep conversation history per session ──────────────────
# For now we use stateless (single-turn). Easy to upgrade to multi-turn.

@app.route("/", methods=["GET"])
def health():
    """Simple health check — visit http://localhost:10000/ to confirm server is running."""
    return jsonify({"status": "ok", "message": "Chatbot backend is running."})


@app.route("/chat", methods=["POST"])
def chat():
    # 1. Validate incoming request
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"reply": "Invalid JSON body."}), 400

    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Message cannot be empty."}), 400

    if len(user_input) > 4000:
        return jsonify({"reply": "Message is too long. Please keep it under 4000 characters."}), 400

    # 2. Call Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # ← correct model name
            contents=user_input,
        )

        reply = response.text
        if not reply:
            return jsonify({"reply": "I didn't get a response. Please try again."}), 502

        return jsonify({"reply": reply})

    except Exception as e:
        # Log the real error to your console, send safe message to client
        print(f"[Gemini Error] {type(e).__name__}: {e}")
        return jsonify({"reply": "Something went wrong on my end. Please try again shortly."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"🚀 Server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)