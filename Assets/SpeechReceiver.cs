using UnityEngine;
using TMPro;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class SpeechReceiver : MonoBehaviour
{
    [Header("Ustawienia Sieci")]
    public int port = 5005;

    [Header("Referencje UI")]
    public TMP_Text transcriptionText;

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
        // Przetwarzanie kolejki w głównym wątku Unity
        while (messageQueue.TryDequeue(out string newText))
        {
            // LOG 2: Potwierdzenie przekazania danych do wątku głównego
            Debug.Log($"[SpeechReceiver - UI] Przetwarzanie tekstu w Update: '{newText}'");

            if (transcriptionText != null)
            {
                transcriptionText.text += newText + " ";
                Debug.Log($"[SpeechReceiver - UI] Tekst dopisany do obiektu: {transcriptionText.name}");
                transcriptionText.ForceMeshUpdate();

            }
            else
            {
                // LOG AWARYJNY: Jeśli zapomniałeś przeciągnąć obiekt w Inspektorze
                Debug.LogError("[SpeechReceiver - BŁĄD] Referencja 'transcriptionText' jest PUSTA (Null) w Inspektorze! Tekst nie ma gdzie się wyrenderować.");
            }
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
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }
    }
}