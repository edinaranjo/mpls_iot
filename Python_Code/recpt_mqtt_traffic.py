import paho.mqtt.client as mqtt
import json
import base64
import numpy as np
import soundfile as sf
import time  # Importar la librería time para agregar pausas

# Global variable to control processing
data_processing = True

# Remote broker configuration
REMOTE_BROKER = "0.0.0.0"  # Replace with the actual remote IP
REMOTE_PORT = 1883

def process_audio(payload):
    """
    Processes a binary audio message.
    """
    try:
        # Decode the JSON message (containing Base64-encoded binary data)
        message = json.loads(payload.decode('utf-8', errors='ignore'))
        audio_encoded = message.get("audio", None)
        samplerate = message.get("samplerate", None)

        if audio_encoded is None or samplerate is None:
            raise ValueError("Missing audio data or samplerate in the message")

        # Decode the audio from Base64
        audio_data = base64.b64decode(audio_encoded)

        # Convert binary data to a NumPy array
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        return samplerate, audio_array
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None, None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to the remote MQTT broker.")
        client.subscribe("iot/sensors/#")
    else:
        print(f"Connection failed, code {rc}")

def on_message(client, userdata, msg):
    global data_processing
    if not data_processing:
        print("Processing stopped. Ignoring new messages.")
        return

    try:
        message = json.loads(msg.payload.decode('utf-8', errors='ignore'))
        topic = msg.topic

        if topic.endswith("data"):
            print(f"[DATA] Sensor {message['sensor_id']}: Temp={message['temperature']}C, Hum={message['humidity']}%, Timestamp={message['timestamp']}")
        elif topic.endswith("voice"):
            samplerate, audio_array = process_audio(msg.payload)
            if samplerate and audio_array is not None:
                print(f"[VOICE] Sensor {message['sensor_id']}: Audio received with samplerate {samplerate} Hz, Length={len(audio_array)} samples, Timestamp={message['timestamp']}")
        
        # Agregar una pausa de 5 segundos después de procesar cada mensaje
        time.sleep(0.5)
    except Exception as e:
        print(f"Error processing message: {e}")

def stop_processing():
    global data_processing
    data_processing = False
    print("Data processing stopped.")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(REMOTE_BROKER, REMOTE_PORT, 60)
        print("Starting remote MQTT subscriber. Press Ctrl+C to stop.")
        client.loop_start()

        while True:
            command = input("Type 'stop' to stop processing: ").strip().lower()
            if command == "stop":
                stop_processing()
                break

        client.loop_stop()
        client.disconnect()
        print("Process terminated.")
    except KeyboardInterrupt:
        print("Manual interruption. Terminating process.")
