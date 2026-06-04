import os
import time
import socket
import pathlib
import asyncio
import threading
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from notebooklm import NotebookLMClient

UNITY_IP = "127.0.0.1"
UNITY_PORT = 5005
PYTHON_LISTEN_PORT = 5006  # Port, na którym Python słucha Unity

stop_recording = False

def get_next_filename(base_dir):
    i = 1
    while True:
        filename = os.path.join(base_dir, f"badany_{i:02d}.txt")
        if not os.path.exists(filename):
            return filename
        i += 1

async def generate_notes_from_file(filepath):
    print("\n[NotebookLM] Rozpoczynam generowanie notatki...")
    async with NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create("Analiza Wykladu VR")
        await client.sources.add_file(notebook.id, filepath, wait=True)
        response = await client.chat.ask(
            notebook.id,
            """
            Przygotuj szczegółową notatkę z tego wykładu.
            Uwzględnij: główne tezy, najważniejsze wnioski, kluczowe pojęcia, krótkie podsumowanie na końcu.
            """
        )
        return response.answer

def udp_listener():
    """Ten wątek działa w tle i czeka na kliknięcie przycisku w Unity"""
    global stop_recording
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(("127.0.0.1", PYTHON_LISTEN_PORT))
    print(f"[Python] Nasłuchuje komend z Unity na porcie {PYTHON_LISTEN_PORT}...")
    
    while not stop_recording:
        try:
            listen_sock.settimeout(1.0)
            data, addr = listen_sock.recvfrom(1024)
            message = data.decode('utf-8')
            if message == "STOP_RECORDING":
                print("\n[Python] Otrzymano sygnał STOP z Unity! Zamykam nagrywanie.")
                stop_recording = True
        except socket.timeout:
            continue
        except Exception as e:
            pass
    listen_sock.close()

def run_pipeline(api_key, region):
    global stop_recording
    stop_recording = False
    
    # Uruchamiamy ucho nasłuchujące kliknięć z Unity
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()

    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "pl-PL"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    current_dir = str(pathlib.Path(__file__).parent.resolve())
    output_filepath = get_next_filename(current_dir)
    print(f"Dane badanego zostaną zapisane w: {output_filepath}")
    
    # Funkcja wyzwalana automatycznie, gdy Azure rozpozna zdanie
    def speech_recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            print("Rozpoznano: {}".format(text))
            sock.sendto(text.encode("utf-8"), (UNITY_IP, UNITY_PORT))
            with open(output_filepath, "a", encoding="utf-8") as f:
                f.write(text + "\n")

    # Podpinamy funkcję pod Azure i zaczynamy ciągłe słuchanie
    speech_recognizer.recognized.connect(speech_recognized_cb)
    speech_recognizer.start_continuous_recognition()
    
    print("Mów do mikrofonu (Naciśnij 'Zakończ wykład' w VR, aby wygenerować notatkę)...")
    
    # Główna pętla po prostu kręci się i czeka, aż flaga stop_recording zmieni się na True
    while not stop_recording:
        time.sleep(0.5)
        
    # Sprzątanie po zakończeniu
    speech_recognizer.stop_continuous_recognition()
    print("Zakończono nasłuchiwanie. Przekazuję do AI...")
    
    try:
        notatka = asyncio.run(generate_notes_from_file(output_filepath))
        print("\n=== GOTOWA NOTATKA ===")
        print(notatka)
        
        note_filepath = output_filepath.replace(".txt", "_notatka.txt")
        with open(note_filepath, "w", encoding="utf-8") as f:
            f.write(notatka)
            
        final_message = "[NOTE]" + notatka
        sock.sendto(final_message.encode("utf-8"), (UNITY_IP, UNITY_PORT))
        print(f"\nZapisano pliki: {output_filepath} oraz {note_filepath}")
        
    except Exception as e:
        print(f"Błąd NotebookLM: {e}")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("api_key")
    region = os.getenv("region")
    if not api_key or not region:
        print("Brak kluczy API")
    else:
        run_pipeline(api_key, region)