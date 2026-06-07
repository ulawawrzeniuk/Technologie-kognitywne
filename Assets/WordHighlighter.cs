using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;

[RequireComponent(typeof(TextMeshProUGUI))]
public class WordHighlighter : MonoBehaviour, IPointerClickHandler
{
    private TextMeshProUGUI textMesh;

    // Opcjonalna referencja, aby wysłać to słowo do Twojego Pythona
    public UdpSender udpSender;

    void Awake()
    {
        textMesh = GetComponent<TextMeshProUGUI>();
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        // 1. Znajdź indeks słowa, w które uderzył promień z kontrolera VR
        int wordIndex = TMP_TextUtilities.FindIntersectingWord(textMesh, eventData.position, eventData.pressEventCamera);

        // Jeśli promień w coś trafił (indeks inny niż -1)
        if (wordIndex != -1)
        {
            // 2. Pobierz czysty tekst klikniętego słowa
            string word = textMesh.textInfo.wordInfo[wordIndex].GetWord();

            // Zabezpieczenie przed błędami i wielokrotnym podświetlaniem tego samego słowa
            if (string.IsNullOrWhiteSpace(word) || textMesh.text.Contains($"<mark=#FFFF0088>{word}</mark>"))
                return;

            // 3. Zastosuj efekt zakreślacza (Żółty kolor z 88 wartością Alpha dla lekkiej przezroczystości)
            string highlightedWord = $"<mark=#FFFF0088>{word}</mark>";

            // Prosta zamiana w tekście - podświetli wszystkie wystąpienia tego słowa w obecnym bloku
            textMesh.text = textMesh.text.Replace(word, highlightedWord);

            Debug.Log($"[WordHighlighter] Zaznaczono słowo: {word}");

            // 4. (Opcjonalnie) Przekaż informację do skryptu komunikacyjnego
            if (udpSender != null)
            {
                udpSender.SendData("HIGHLIGHT:" + word);
            }
        }
    }
}