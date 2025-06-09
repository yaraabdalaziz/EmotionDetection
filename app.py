from flask import Flask, request, jsonify, g
from Services.EmotionDetectorService import EmotionDetectorService
from Services.AuthService import require_auth, require_quota
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

detector = EmotionDetectorService()
print("Service is ready")


@app.route("/detect-emotion", methods=["POST"])
@require_auth
@require_quota(consume_on_success=True)
def detect_emotion_endpoint():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    text = data["text"]
    user_id = g.current_user_id

    try:
        preprocessed_text, predicted_label, probability = detector.detect_emotion(
            text, user_id
        )
        return (
            jsonify(
                {
                    "preprocessed_text": preprocessed_text,
                    "label": predicted_label,
                    "probability": probability,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app.run(host=host, port=port, debug=debug)
