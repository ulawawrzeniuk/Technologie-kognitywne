import os
import time
import pathlib
import asyncio
import azure.cognitiveservices.speech as speechsdk

# Importy własnych modułów
from config import AZURE_API_KEY, AZURE_REGION
from app_state import AppState
from network import start_listener_thread, send_to_unity
from ai_client import generate_notes_from_file

def get_next_filename(base_dir):
    i = 1
    while True:
        filename = os.path.join(base_dir, f"badany_{i:02d}.txt")
        if not os.path.exists(filename):
            return filename
        i += 1

def inject_highlights(filepath):
    if not AppState.highlighted_words:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        for word in AppState.highlighted_words:
            content = content.replace(word, f"<< {word} >>")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[Python] Wstrzyknięto znaczniki do pliku dla słów: {AppState.highlighted_words}")
    except Exception as e:
        print(f"[Python - BŁĄD PLIKU] Nie udało się nadpisać znaczników: {e}")

def run_pipeline():
    if not AZURE_API_KEY or not AZURE_REGION:
        print("Brak kluczy API. Skonfiguruj plik .env.")
        return

    AppState.reset()
    start_listener_thread()

    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region=AZURE_REGION)
    speech_config.speech_recognition_language = "pl-PL"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # --- BEZPIECZNE ZARZĄDZANIE ŚCIEŻKAMI ---
    # __file__ to main.py
    # .parent to katalog python_scripts
    # .parent.parent to katalog główny projektu
    project_root = pathlib.Path(__file__).parent.parent.resolve()
    
    transkrypcje_dir = project_root / "results" / "transkrypcje"
    notatki_dir = project_root / "results" / "notatki"

    # Tworzenie folderów (parents=True tworzy również folder 'results', jeśli go nie ma)
    transkrypcje_dir.mkdir(parents=True, exist_ok=True)
    notatki_dir.mkdir(parents=True, exist_ok=True)

    # Generowanie ścieżki pliku transkrypcji
    output_filepath = get_next_filename(str(transkrypcje_dir))
    print(f"Dane badanego zostaną zapisane w: {output_filepath}")
    # ----------------------------------------
    
    def speech_recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            print(f"Rozpoznano: {text}")
            send_to_unity(text)
            with open(output_filepath, "a", encoding="utf-8") as f:
                f.write(text + "\n")

    speech_recognizer.recognized.connect(speech_recognized_cb)
    speech_recognizer.start_continuous_recognition()
    
    print("Mów do mikrofonu (Naciśnij 'Zakończ wykład' w VR, aby zatrzymać)...")
    
    # Oczekujemy na sygnał STOP_RECORDING z Unity
    while not AppState.stop_recording:
        time.sleep(0.5)
        
    speech_recognizer.stop_continuous_recognition()
    print("Zakończono nasłuchiwanie. Czekam na wybór rodzaju notatki (kliknij przycisk formatu w VR)...")

    # Modyfikacja pliku po nagrywaniu
    inject_highlights(output_filepath)
    
    # Oczekujemy na wybór GENERATE_MAPA lub GENERATE_TEXT z Unity
    while AppState.prompt_choice is None:
        time.sleep(0.5)
        
    print(f"Przekazuję do AI z promptem: {AppState.prompt_choice}...")
    
    try:
        notatka = asyncio.run(generate_notes_from_file(output_filepath, AppState.prompt_choice))
        print("\n=== GOTOWA NOTATKA ===")
        print(notatka)
        
        # --- ZAPIS NOTATKI W OSOBNYM FOLDERZE ---
        # 1. Wyciągamy samą nazwę pliku z transkrypcji (np. badany_01)
        base_filename = os.path.basename(output_filepath).replace(".txt", "")
        
        # 2. Tworzymy nową nazwę i łączymy z katalogiem results/notatki/
        note_filename = f"{base_filename}_notatka_{AppState.prompt_choice.lower()}.txt"
        note_filepath = os.path.join(str(notatki_dir), note_filename)
        
        with open(note_filepath, "w", encoding="utf-8") as f:
            f.write(notatka)
        # ----------------------------------------
            
        send_to_unity("[NOTE]" + notatka)
        print(f"\nZapisano pliki:\nTranskrypcja: {output_filepath}\nNotatka: {note_filepath}")
        
    except Exception as e:
        print(f"Błąd NotebookLM: {e}")

if __name__ == "__main__":
    run_pipeline()