import os
from pathlib import Path
from dotenv import load_dotenv

# Twarde odniesienie do ścieżki pliku config.py
# .parent to folder python_scripts, .parent.parent to root (zakładając, że tu leży .env)
env_path = Path(__file__).parent.parent.resolve() / '.env'

# Jawne wskazanie pliku do załadowania
load_dotenv(dotenv_path=env_path)

# Konfiguracja Azure
AZURE_API_KEY = os.getenv("api_key")
AZURE_REGION = os.getenv("region")

# Konfiguracja Sieci UDP
UNITY_IP = "127.0.0.1"
UNITY_PORT = 5005
PYTHON_LISTEN_PORT = 5006