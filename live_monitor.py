# Import all the necessary toolkits
import time
import psutil
import numpy as np
from tensorflow import keras
import joblib
from datetime import datetime, timedelta

print("Starting Live Anomaly Detector...")

# --- Configuration ---
# PASTE THE THRESHOLD VALUE YOU COPIED FROM THE TRAINING SCRIPT HERE
THRESHOLD = 0.1776567276022933  # <-- IMPORTANT: REPLACE THIS WITH YOUR VALUE
PHONE_LOG_FILE = 'phone_presence.log'
PRESENCE_WINDOW_SECONDS = 120 # 2 minutes

# --- Step 1: Load the trained AI model and the scaler ---
try:
    model = keras.models.load_model('anomaly_detector.h5')
    scaler = joblib.load('scaler.gz')
    print("Model and scaler loaded successfully.")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    print("Please make sure 'anomaly_detector.h5' and 'scaler.gz' are in the folder.")
    exit()

# --- Step 2: Helper function to check for recent phone presence ---
def is_phone_recently_present():
    try:
        with open(PHONE_LOG_FILE, 'r') as f:
            # Read the very last line of the file
            last_line = f.readlines()[-1]
        
        # Extract the timestamp from the last line
        last_presence_str = last_line.replace('Phone signal received at: ', '').strip()
        last_presence_time = datetime.strptime(last_presence_str, '%Y-%m-%d %H:%M:%S')

        # Check if the last signal was within our time window
        if datetime.now() - last_presence_time < timedelta(seconds=PRESENCE_WINDOW_SECONDS):
            return 1 # Present
        else:
            return 0 # Not present
    except (FileNotFoundError, IndexError):
        # If the file doesn't exist or is empty, assume phone is not present
        return 0

# --- Step 3: The Main Monitoring Loop ---
print("\n--- Live Monitoring Started ---")
while True:
    try:
        # 1. Collect live data from the laptop
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        process_count = len(psutil.pids())
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_received = net_io.bytes_recv

        # 2. Check for the phone's presence
        phone_present = is_phone_recently_present()

        # 3. Combine the live data into a single feature set
        # The order MUST be the same as in your training data!
        live_features = np.array([
            cpu_usage, 
            ram_usage, 
            process_count, 
            bytes_sent, 
            bytes_received, 
            phone_present
        ]).reshape(1, -1) # Reshape for a single sample

        # 4. Scale the live data using the loaded scaler
        live_features_scaled = scaler.transform(live_features)

        # 5. Get the model's reconstruction of the live data
        reconstruction = model.predict(live_features_scaled, verbose=0)

        # 6. Calculate the reconstruction error (anomaly score)
        anomaly_score = np.mean(np.abs(live_features_scaled - reconstruction))

        # 7. Compare the score to our threshold and print the status
        status = "NORMAL"
        if anomaly_score > THRESHOLD:
            status = "!! ANOMALY DETECTED !!"
        
        print(f"Time: {datetime.now().strftime('%H:%M:%S')} | Status: {status} | Anomaly Score: {anomaly_score:.6f}")

        # Wait for 5 seconds before the next check
        time.sleep(5)

    except KeyboardInterrupt:
        print("\nLive monitoring stopped.")
        break
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
        time.sleep(5)