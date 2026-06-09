using UnityEngine;
using TMPro;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using UnityEngine.UI;

public class SpeechReceiver : MonoBehaviour
{
    [Header("Ustawienia Sieci")]
    public int port = 5005;

    [Header("Referencje UI")]
    public TMP_Text transcriptionText;
    public ScrollRect scrollRect;

    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isListening = false;

    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();

    void Start()
    {
        StartListening();
    }

    private void StartListening()
    {
        try
        {
            udpClient = new UdpClient(port);
            isListening = true;
            receiveThread = new Thread(ReceiveData)
            {
                IsBackground = true
            };
            receiveThread.Start();
            Debug.Log($"[SpeechReceiver] Rozpoczęto nasłuchiwanie na porcie UDP: {port}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[SpeechReceiver] Błąd krytyczny inicjalizacji UDP: {e.Message}");
        }
    }

    private void ReceiveData()
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, port);
        while (isListening)
        {
            try
            {
                byte[] data = udpClient.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);

                if (!string.IsNullOrWhiteSpace(text))
                {
                    // LOG 1: Potwierdzenie, że sieć fizycznie odebrała bajty z Pythona
                    Debug.Log($"[SpeechReceiver - Sieć] Odebrano pakiet UDP: '{text}'");
                    messageQueue.Enqueue(text);
                }
            }
            catch (SocketException)
            {
                // Oczekiwany błąd przy zamykaniu aplikacji
            }
        }
    }

    void Update()
    {
        bool textAddedThisFrame = false;

        // Przetwarzanie kolejki w głównym wątku Unity
        while (messageQueue.TryDequeue(out string newText))
        {
            // Logika przechwytywania [NOTE] dla finalnej notatki (jeśli ją dodałeś)
            if (newText.StartsWith("[NOTE]"))
            {
                string pureNote = newText.Substring(6);
                AppStateManager stateManager = Object.FindFirstObjectByType<AppStateManager>();
               // if (stateManager != null) stateManager.DisplayFinalNote(pureNote);
                continue;
            }

            if (transcriptionText != null)
            {
                transcriptionText.text += newText + " ";
                textAddedThisFrame = true; // Zaznaczamy, że tekst uległ zmianie
            }
        }

        // Jeśli w tej klatce dopisano tekst, przewiń na dół
        if (textAddedThisFrame && scrollRect != null)
        {
            // Wymuszenie aktualizacji Canvasu przed zmianą pozycji
            Canvas.ForceUpdateCanvases();

            // Ustawienie pozycji scrollbara na sam dół (0 = dół, 1 = góra)
            scrollRect.verticalNormalizedPosition = 0f;
        }
    }

    public void ClearTranscription()
    {
        if (transcriptionText != null)
        {
            transcriptionText.text = "";
            Debug.Log("[SpeechReceiver] Wyczyszczono tekst transkrypcji.");
        }
    }

    void OnApplicationQuit()
    {
        isListening = false;
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }
}