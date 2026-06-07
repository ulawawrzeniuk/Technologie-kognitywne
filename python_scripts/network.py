import socket
import threading
from python_scripts.app_state import AppState
from python_scripts.config import PYTHON_LISTEN_PORT, UNITY_IP, UNITY_PORT

def _udp_listener():
    """Wewnętrzna funkcja działająca w tle, czekająca na komendy z Unity."""
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(("127.0.0.1", PYTHON_LISTEN_PORT))
    print(f"[Python - Sieć] Nasłuchuje komend z Unity na porcie {PYTHON_LISTEN_PORT}...")
    
    while True:
        try:
            listen_sock.settimeout(1.0)
            data, addr = listen_sock.recvfrom(1024)
            message = data.decode('utf-8')
            
            if message == "STOP_RECORDING":
                print("\n[Python - Sieć] Otrzymano sygnał STOP z Unity! Zamykam nagrywanie.")
                AppState.stop_recording = True
            elif message == "GENERATE_MAPA":
                print("\n[Python - Sieć] Wybrano mapę myśli.")
                AppState.prompt_choice = "MAPA"
            elif message == "GENERATE_TEXT":
                print("\n[Python - Sieć] Wybrano ciągły tekst.")
                AppState.prompt_choice = "TEXT"
            elif message.startswith("HIGHLIGHT:"):
                word = message.split(":")[1]
                AppState.highlighted_words.add(word)
                print(f"\n[Python - Sieć] Do podświetlenia dodano: {word}")
                
            # Zamykamy pętlę dopiero gdy nagrywanie jest wyłączone I wybrano format
            if AppState.stop_recording and AppState.prompt_choice is not None:
                break
                
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[Python - BŁĄD UDP] Nieoczekiwany wyjątek w listenerze: {e}")
            
    listen_sock.close()

def start_listener_thread():
    """Uruchamia wątek nasłuchujący komend UDP."""
    listener_thread = threading.Thread(target=_udp_listener, daemon=True)
    listener_thread.start()
    return listener_thread

def send_to_unity(message):
    """Otwiera na moment gniazdo, wysyła wiadomość do Unity i je zamyka."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode("utf-8"), (UNITY_IP, UNITY_PORT))
        sock.close()
    except Exception as e:
        print(f"[Python - Sieć] Błąd wysyłania do Unity: {e}")