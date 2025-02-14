from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend server is running!"}), 200

@app.route("/proxy", methods=["POST"])
def proxy_backend():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    return jsonify({"message": "POST request received", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
