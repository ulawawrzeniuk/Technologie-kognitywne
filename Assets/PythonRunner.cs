using UnityEngine;
using System.Diagnostics;
using Debug = UnityEngine.Debug;

public class PythonRunner : MonoBehaviour
{
    [Header("Ścieżki bezwzględne")]
    [Tooltip("Ścieżka do pliku python.exe na Twoim komputerze, np. C:\\Python310\\python.exe; lub w srodowisku wirtualnym C:\\Users\\sciezka\\do\\projektu\\venv\\Scripts\\python.exe")]
    public string pythonInterpreterPath = @"";

    [Tooltip("Ścieżka do Twojego pliku main.py, np. C:\\Users\\...\\python_scripts\\main.py")]
    public string pythonScriptPath = @"";

    private Process pythonProcess;

    public void StartPythonScript()
    {
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            Debug.LogWarning("[PythonRunner] Skrypt Pythona już działa.");
            return;
        }

        try
        {
            pythonProcess = new Process();
            pythonProcess.StartInfo.FileName = pythonInterpreterPath;
            pythonProcess.StartInfo.Arguments = $"\"{pythonScriptPath}\"";

            // Konfiguracja okna procesu
            pythonProcess.StartInfo.UseShellExecute = true; // Zostaw na true, by widzieć okno konsoli Pythona podczas testów
            pythonProcess.StartInfo.CreateNoWindow = false;

            pythonProcess.Start();
            Debug.Log("[PythonRunner] Pomyślnie uruchomiono skrypt Pythona.");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[PythonRunner] Błąd uruchamiania Pythona. Sprawdź ścieżki! Szczegóły: {e.Message}");
        }
    }

    void OnApplicationQuit()
    {
        // Sprzątanie: Zabijamy proces Pythona, żeby nie został "osierocony" w tle
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            pythonProcess.Kill();
            Debug.Log("[PythonRunner] Zamknięto proces Pythona po wyjściu z aplikacji.");
        }
    }
}