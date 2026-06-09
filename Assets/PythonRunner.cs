using UnityEngine;
using System.Diagnostics;
using Debug = UnityEngine.Debug;

public class PythonRunner : MonoBehaviour
{
    [Header("Ścieżki bezwzględne")]
    public string pythonInterpreterPath = @"C:\Users\marys\Technologie-kognitywne\python_scripts\venv\Scripts\python.exe";
    public string pythonScriptPath = @"C:\Users\marys\Technologie-kognitywne\python_scripts\main.py";

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

            // Uruchomienie przez CMD wymusi pozostawienie okna otwartego po zakończeniu/błędzie skryptu
            pythonProcess.StartInfo.FileName = "cmd.exe";
            pythonProcess.StartInfo.Arguments = $"/k \"\"{pythonInterpreterPath}\" \"{pythonScriptPath}\"\"";

            pythonProcess.StartInfo.UseShellExecute = true;
            pythonProcess.StartInfo.CreateNoWindow = false;

            pythonProcess.Start();
            Debug.Log("[PythonRunner] Uruchomiono proces CMD. Sprawdź okno konsoli na pulpicie.");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[PythonRunner] Błąd C#: {e.Message}");
        }
    }

    void OnApplicationQuit()
    {
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            pythonProcess.Kill();
        }
    }
}