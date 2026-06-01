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

    public void OnNoteFormatSelected(string formatType)
    {
        Debug.Log("Wybrano format notatki: " + formatType);
        ChangeState(AppState.Idle);
    }

    private void StartRecording()
    {
        transcriptionText.text = mockTranscription;
    }
}