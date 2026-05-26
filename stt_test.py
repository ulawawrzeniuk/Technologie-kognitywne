import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk


def speak_to_microphone(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "pl-PL"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    #set timeout durations
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "5000")
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "5000")

    print("powiedz cos")
    
    while True:
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Rozpoznano: {}".format(speech_recognition_result.text))
            if "koniec tekstu" in speech_recognition_result.text.lower():
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