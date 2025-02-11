import threading
import time
import random
import json
import csv
import base64
import numpy as np
import paho.mqtt.client as mqtt
from datetime import datetime
import soundfile as sf
from scipy.signal import resample  # Importar la función para remuestrear audio

# MQTT broker configuration
BROKER = "127.0.0.1"
PORT = 1883
DATA_TOPIC = "iot/sensors/data"
VOICE_TOPIC = "iot/sensors/voice"

# Global variable to control traffic
traffic_running = False

# Function to generate data traffic
def generate_data(sensor_id):
    return {
        "sensor_id": sensor_id,
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "timestamp": datetime.now().strftime("%H:%M:%S")  # Formato HH:MM:SS
    }

# Function to generate voice traffic
def generate_audio(wav_file, duration=0.05, target_samplerate=8000):
    # Read the entire audio file
    audio_data, original_samplerate = sf.read(wav_file)
    
    num_samples = int(duration * target_samplerate)
    for start in range(0, len(audio_data), num_samples):
        audio_block = audio_data[start:start + num_samples]
        if len(audio_block) < num_samples:
            break
        # Resample audio block if necessary
        if original_samplerate != target_samplerate:
            audio_block = resample(audio_block, num_samples)
        yield audio_block

# Function to measure performance parameters
def measure_performance(sensor_id):
    packet_loss = round(random.uniform(0, 5), 2)  # % packet loss
    jitter = round(random.uniform(0, 50), 2)      # ms
    latency = round(random.uniform(10, 100), 2)  # ms
    return {
        "sensor_id": sensor_id,
        "packet_loss": packet_loss,
        "jitter": jitter,
        "latency": latency
    }

# Save results to CSV
def save_results(results, traffic_type):
    filename = f"{traffic_type}_{datetime.now().strftime('%Y-%m.%d_%H:%M:%S')}.csv"
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Traffic", "sensor_id", "packet_loss", "jitter", "latency"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")

# Traffic function
def traffic(sensor_id, client, traffic_type, wav_file=None):
    global traffic_running
    while traffic_running:
        if traffic_type == "DATA":
            data = generate_data(sensor_id)
            client.publish(DATA_TOPIC, json.dumps(data))
            time.sleep(5)  # Espera de 5 segundos entre publicaciones de datos
        elif traffic_type == "VOICE":
            for audio_block in generate_audio(wav_file):
                if not traffic_running:
                    break
                audio_encoded = base64.b64encode(audio_block.tobytes()).decode('utf-8')
                voice_message = {
                    "sensor_id": sensor_id,
                    "audio": audio_encoded,
                    "samplerate": 8000,
                    "timestamp": datetime.now().strftime("%H:%M:%S")  # Formato HH:MM:SS
                }
                client.publish(VOICE_TOPIC, json.dumps(voice_message))
                time.sleep(5)  # Espera de 5 segundos entre publicaciones de bloques de audio

# Main menu
def main():
    global traffic_running
    while True:
        print("\nMain Menu")
        print("1: Data traffic")
        print("2: Voice traffic")
        print("3: Exit")

        try:
            option = int(input("Select an option: "))
            if option == 3:
                print("Exiting program...")
                break
            elif option in [1, 2]:
                traffic_type = "DATA" if option == 1 else "VOICE"

                while True:
                    try:
                        num_sensors = int(input("Enter the number of sensors (max 500): "))
                        if 1 <= num_sensors <= 500:
                            break
                        else:
                            print("Error: The number must be between 1 and 500.")
                    except ValueError:
                        print("Error: Enter a valid integer.")

                results = []
                threads = []
                start_time = None

                while True:
                    print("\n1: Start traffic")
                    traffic_option = input("Select an option: ")
                    if traffic_option == "1" and not traffic_running:
                        print("Generating traffic...")
                        traffic_running = True
                        start_time = time.time()
                        client = mqtt.Client()
                        client.connect(BROKER, PORT, 60)

                        wav_file = None
                        if traffic_type == "VOICE":
                            wav_file = "./ejemplo.wav"

                        for sensor_id in range(num_sensors):
                            result = measure_performance(sensor_id)
                            result["Traffic"] = traffic_type
                            results.append(result)

                            thread = threading.Thread(target=traffic, args=(sensor_id, client, traffic_type, wav_file))
                            thread.daemon = True
                            threads.append(thread)
                            thread.start()

                        input("Press Enter to stop traffic...")
                        traffic_running = False
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        print(f"Stopped Traffic. Total generation time: {(elapsed_time/60):.2f} minutes")
                        for thread in threads:
                            thread.join()

                        save_results(results, traffic_type)
                        break
                    else:
                        print("Error: Invalid option. Try again.")
            else:
                print("Error: Invalid option.")
        except ValueError:
            print("Error: Enter a valid number.")

if __name__ == "__main__":
    main()
