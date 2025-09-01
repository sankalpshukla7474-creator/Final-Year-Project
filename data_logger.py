# Correct Code for data_logger.py
import psutil
import time
import csv
import os
from datetime import datetime

LOG_INTERVAL = 5
OUTPUT_FILE = 'system_log.csv'
HEADER = ['timestamp', 'cpu_usage_percent', 'ram_usage_percent', 'active_processes', 'net_bytes_sent', 'net_bytes_received']

file_exists = os.path.exists(OUTPUT_FILE)

try:
    with open(OUTPUT_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(HEADER)
            print(f"Created a new log file: {OUTPUT_FILE}")

        print("Starting data logging... Press Ctrl+C to stop.")

        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            process_count = len(psutil.pids())
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_received = net_io.bytes_recv

            log_data = [timestamp, cpu_usage, ram_usage, process_count, bytes_sent, bytes_received]

            writer.writerow(log_data)
            csvfile.flush()
            print(f"Logged data at {timestamp}")
            time.sleep(LOG_INTERVAL - 1)

except KeyboardInterrupt:
    print("\nLogging stopped by user. Your data is saved in 'system_log.csv'.")
except Exception as e:
    print(f"An error occurred: {e}")