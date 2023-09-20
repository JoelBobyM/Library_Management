from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-in')
def signin():
    return render_template('signin.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/iot-input', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        # You can access the JSON data from the request like this:
        # data = request.get_json()
        
        # Perform some processing on the JSON data if needed
        
        # Respond with a status code (e.g., 200 for success)
        print(data)
        return jsonify({"message": "Success"}), 200

    except Exception as e:
        # If there's an error, respond with an appropriate status code (e.g., 400 for bad request)
        return jsonify({"error": "Invalid JSON data"}), 400


if __name__=="__main__":
    app.run(debug=True)
