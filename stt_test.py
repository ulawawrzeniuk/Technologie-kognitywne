import os
import socket
import time
import pathlib

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

UNITY_IP = "127.0.0.1"
UNITY_PORT = 5005

# Path to output text file
TXT_FILE = pathlib.Path(__file__).parent / "test.txt"

# Clear the file on startup (remove these 2 lines if you want to keep old content)
with open(TXT_FILE, "w", encoding="utf-8") as f:
    pass

print(pathlib.Path(__file__).parent.resolve())


def continuous_recognition(api_key, region):
    speech_config = speechsdk.SpeechConfig(
        subscription=api_key,
        region=region
    )
    speech_config.speech_recognition_language = "pl-PL"

    audio_config = speechsdk.audio.AudioConfig(
        use_default_microphone=True
    )

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Połączenie UDP -> {UNITY_IP}:{UNITY_PORT}")

    done = False

    def stop_cb(evt):
        print(f"Zatrzymano nasłuch: {evt}")
        nonlocal done
        done = True

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text

            print(f"Rozpoznano: {text}")

            # Send text to Unity
            sock.sendto(text.encode("utf-8"), (UNITY_IP, UNITY_PORT))

            # Append text to file
            with open(TXT_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")

            # Stop on voice command
            if "koniec tekstu" in text.lower():
                print("Wykryto komendę kończącą.")
                speech_recognizer.stop_continuous_recognition_async()

    # Register event handlers
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    print("Rozpoczęto ciągłe rozpoznawanie mowy. Mów...")

    speech_recognizer.start_continuous_recognition_async()

    while not done:
        time.sleep(0.5)

    print("Zamykanie programu...")
    sock.close()


load_dotenv()

api_key = os.getenv("api_key")
region = os.getenv("region")

if not api_key or not region:
    print("Błąd: Nie znaleziono kluczy API. Sprawdź plik .env.")
else:
    continuous_recognition(api_key, region)