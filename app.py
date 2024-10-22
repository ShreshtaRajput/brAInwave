from flask import Flask, request, render_template, redirect, url_for, jsonify

app = Flask(__name__)

# Initial moisture values
moisture_threshold = 40  
last_checked_moisture = None
message = ""

@app.route('/')
def home():
    return render_template('home.html')

# Route to display the dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    global moisture_threshold
    global last_checked_moisture
    global message
    
    return render_template('dashboard.html', 
                           moisture_threshold=moisture_threshold, 
                           last_checked_moisture=last_checked_moisture,
                           message=message)

@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', moisture_threshold=moisture_threshold)

# Route triggered by the "GET MOISTURE" button
@app.route('/get_moisture', methods=['POST'])
def get_moisture():
    global last_checked_moisture
    global message
    
    # Check if the request contains JSON data (from ESP32)
    if request.is_json:
        data = request.get_json()
        last_checked_moisture = data.get('moisture')  # Get the moisture data
        print(f"Moisture level received: {last_checked_moisture}")
        return jsonify({"status": "Moisture data received"}), 200
    
    # If request is from dashboard (which won't send JSON), just return success
    else:
        print("Dashboard requested moisture data update")
        return redirect(url_for('dashboard'))

@app.route('/update_threshold', methods=['POST'])
def update_threshold():
    global moisture_threshold
    new_threshold = request.form.get('threshold', type=int)
    if new_threshold is not None:
        if 0 <= new_threshold <= 100:
            moisture_threshold = new_threshold
    return redirect(url_for('dashboard'))

@app.route('/water', methods=['GET'])
def water():
    global last_checked_moisture
    global moisture_threshold
    global message
    
    if last_checked_moisture is not None:
        if last_checked_moisture < moisture_threshold:
            message = "Moisture is below the threshold. Watering will be initiated."
            return jsonify({"cmd": "water"}), 200
        else:
            message = f"Moisture is {last_checked_moisture}%, which is more than the threshold ({moisture_threshold}%). No watering needed. Next check will be in 60 seconds."
            return jsonify({"cmd": "no_water"}), 200
    else:
        message = "Moisture data not available."
        return jsonify({"cmd": "no_data"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
