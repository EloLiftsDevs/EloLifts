from flask import Flask, jsonify, request

app = Flask(__name__)

# Basic route
@app.route("/")
def home():
    return "EloLifts basic backend server is up and running!"

# JSON API route
@app.route("/api/hello")
def hello():
    return jsonify(message="Hello from the backend!")

# Route with a URL parameter
@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    return jsonify(id=user_id, name="Example User")

# Handling POST requests with JSON
@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json()
    return jsonify(received=data), 201

if __name__ == "__main__":
    app.run(debug=True)