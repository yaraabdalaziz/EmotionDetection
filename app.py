from flask import Flask, request, jsonify
from Services.AuthService import  AuthService
from Services.EmotionDetectorService import EmotionDetectorService
app = Flask(__name__)

detector = EmotionDetectorService()
auth = AuthService()
print("Service is ready")


@app.route('/detect-emotion', methods=['POST'])
def detect_emotion_endpoint():
    api_key = request.headers.get('api-key')
    user_id = auth.authenticate_user(api_key)
    if  not api_key or not user_id:    
        return jsonify({"error": "Unauthorized"}), 403
    
    if not auth.user_has_quota(user_id):
        return jsonify({
            "error": {
                "code": "quota_exceeded",
                "message": "Quota exceeded. Please upgrade your plan or wait until next reset."
            }
        }), 429 
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    text = data['text']
    
    try:
        preprocessed_text,predicted_label, probability = detector.detect_emotion(text,user_id)
        auth.consume_quota(user_id)
        return jsonify(
            {"preprocessed_text" : preprocessed_text ,"label": predicted_label, "probability":  probability}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
