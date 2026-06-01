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

    // Bezpieczna kolejka do przekazywania tekstu między wątkami
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
            receiveThread = new Thread(ReceiveData);
            receiveThread.IsBackground = true;
            receiveThread.Start();
            Debug.Log("SpeechReceiver nasłuchuje na porcie UDP: " + port);
        }
        catch (System.Exception e)
        {
            Debug.LogError("Nie można otworzyć portu UDP: " + e.Message);
        }
    }

    // Ten kod wykonuje się w tle i nie blokuje płynności VR
    private void ReceiveData()
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, port);
        while (isListening)
        {
            try
            {
                byte[] data = udpClient.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);

                // Zamiast zmieniać UI, wrzucamy tekst do bezpiecznej kolejki
                messageQueue.Enqueue(text);
            }
            catch (SocketException)
            {
                // Zignoruj błąd zamykania gniazda podczas wyłączania gry
            }
        }
    }

    // Główny wątek Unity, który ma prawo edytować UI
    void Update()
    {
        // Sprawdzamy, czy w kolejce czekają nowe słowa od Pythona
        while (messageQueue.TryDequeue(out string newText))
        {
            Debug.Log("Otrzymano z Azure: " + newText); // To dowiedzie, że dane dotarły

            if (transcriptionText != null)
            {
                transcriptionText.text = newText;
            }
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