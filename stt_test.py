import os
import socket
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

UNITY_IP = "127.0.0.1"
UNITY_PORT = 5005


def speak_to_microphone(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "pl-PL"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    #set timeout durations
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "5000")
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "5000")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP connection -> {UNITY_IP}:{UNITY_PORT}")

    print("powiedz cos")
    
    while True:
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = speech_recognition_result.text
            print("Rozpoznano: {}".format(text))

            sock.sendto(text.encode("utf-8"), (UNITY_IP, UNITY_PORT))

            if "koniec tekstu" in text.lower():
                print("Koniec rozpoznawania")
                break
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("Nie rozpoznano mowy: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Rozpoznawanie anulowane: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Błąd: {}".format(cancellation_details.error_details))
                print("Upewnij się, że klucz API i region są poprawne.")
load_dotenv()

api_key = os.getenv("api_key")
region = os.getenv("region")

speak_to_microphone(api_key, region)