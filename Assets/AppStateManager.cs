using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class AppStateManager : MonoBehaviour
{
    public enum AppState
    {
        Idle,
        Recording,
        Summary
    }

    [Header("Biezacy stan aplikacji")]
    public AppState currentState = AppState.Idle;

    [Header("Referencje do paneli UI")]
    public GameObject startPanel;
    public GameObject recordingPanel;
    public GameObject summaryPanel;

    [Header("Referencje do elementow tekstowych")]
    public TextMeshProUGUI transcriptionText;

    private string mockTranscription = "To jest przykladowa transkrypcja wykladu. Uzytkownik bedzie mogl zaznaczac ten tekst za pomoca kontrolerow VR.";

    [Header("Podsumowanie")]
    public TextMeshProUGUI finalNoteText;

//    public void DisplayFinalNote(string noteData)
//    {
//        if (finalNoteText != null)
//        {
//            finalNoteText.text = noteData;
//            ChangeState(AppState.Summary);
//        }
//        else
//        {
//            Debug.LogError("[AppStateManager] Błąd: Referencja finalNoteText jest pusta w Inspektorze!");
//        }
//    }

    void Start()
    {
        ChangeState(AppState.Idle);
    }

    public void ChangeState(AppState newState)
    {
        currentState = newState;

        startPanel.SetActive(false);
        recordingPanel.SetActive(false);
        summaryPanel.SetActive(false);

        switch (currentState)
        {
            case AppState.Idle:
                startPanel.SetActive(true);
                break;

            case AppState.Recording:
                recordingPanel.SetActive(true);
                StartRecording();
                break;

            case AppState.Summary:
                summaryPanel.SetActive(true);
                break;
        }
    }

    public void OnStartRecordingButtonClicked()
    {
        ChangeState(AppState.Recording);
    }

    public void OnStopRecordingButtonClicked()
    {
        ChangeState(AppState.Summary);
    }

    [Header("Wybór formatu notatki")]
    public TMP_Dropdown formatDropdown;
    public UdpSender udpSender;

    // Tę metodę przypiszemy do nowego przycisku "Generuj"
    public void OnGenerateButtonClicked()
    {
        if (formatDropdown == null || udpSender == null)
        {
            Debug.LogError("[AppStateManager] Brak referencji do Dropdownu lub UdpSender w Inspektorze!");
            return;
        }

        // TMP_Dropdown przechowuje wybór jako liczbę (indeks). 0 to pierwsza opcja, 1 to druga.
        if (formatDropdown.value == 0)
        {
            // Zakładamy, że indeks 0 to "MAPA"
            udpSender.SendGenerateMapa();
            Debug.Log("[AppStateManager] Wysłano sygnał: GENERATE_MAPA");
        }
        else if (formatDropdown.value == 1)
        {
            // Zakładamy, że indeks 1 to "TEKST"
            udpSender.SendGenerateTekst();
            Debug.Log("[AppStateManager] Wysłano sygnał: GENERATE_TEXT");
        }

        // Zmiana stanu na Idle (lub możesz stworzyć nowy stan AppState.Loading, jeśli planujesz ekran ładowania)
        ChangeState(AppState.Idle);
    }

    private void StartRecording()
    {
        // Jeśli chcesz mieć testowy tekst tylko, gdy aplikacja nie jest połączona,
        // zrób warunek. W innym razie, wyczyść pole:

        SpeechReceiver receiver = Object.FindFirstObjectByType<SpeechReceiver>();
        if (receiver != null)
        {
            receiver.ClearTranscription();
        }
        else
        {
            transcriptionText.text = mockTranscription; // Fallback w razie braku skryptu sieciowego
        }
    }
}