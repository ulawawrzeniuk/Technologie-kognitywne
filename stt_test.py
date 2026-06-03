import os
import socket
import time
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

UNITY_IP = "127.0.0.1"
UNITY_PORT = 5005

def continuous_recognition(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "pl-PL"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Połączenie UDP -> {UNITY_IP}:{UNITY_PORT}")

    done = False

    def stop_cb(evt):
        print(f"Zatrzymano nasłuch: {evt}")
        nonlocal done
        done = True

    def recognized_cb(evt):
        # Wysyła do Unity tylko zatwierdzone, ostatecznie rozpoznane zdania (unikamy duplikacji)
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            print(f"Rozpoznano: {text}")
            sock.sendto(text.encode("utf-8"), (UNITY_IP, UNITY_PORT))
            
            if "koniec tekstu" in text.lower():
                print("Wykryto komendę kończącą.")
                speech_recognizer.stop_continuous_recognition_async()

    # Rejestracja event handlerów
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    print("Rozpoczęto ciągłe rozpoznawanie mowy. Mów...")
    
    # Rozpoczęcie nasłuchu w tle
    speech_recognizer.start_continuous_recognition_async()

    # Pętla podtrzymująca działanie programu głównego
    while not done:
        time.sleep(0.5)

    print("Zamykanie programu...")

load_dotenv()
api_key = os.getenv("api_key")
region = os.getenv("region")

if not api_key or not region:
    print("Błąd: Nie znaleziono kluczy API. Sprawdź plik .env.")
else:
    continuous_recognition(api_key, region)