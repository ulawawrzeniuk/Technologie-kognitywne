import asyncio
from notebooklm import NotebookLMClient


async def main():
    # ============================================================
    # KROK 1
    # Łączymy się z NotebookLM używając zapisanej wcześniej sesji
    # (tej, którą utworzyłaś przez "notebooklm login")
    # ============================================================
    async with NotebookLMClient.from_storage() as client:

        # ========================================================
        # KROK 2
        # Tworzymy nowy notebook
        # ========================================================
        notebook = await client.notebooks.create(
            "Analiza dokumentu PDF"
        )

        print(f"Utworzono notebook:")
        print(f"ID: {notebook.id}")
        print(f"Tytuł: {notebook.title}")

        # ========================================================
        # KROK 3
        # Ścieżka do pliku, który chcesz wgrać
        # ZMIEŃ na własną ścieżkę
        # ========================================================
        pdf_path = "dokument.pdf"

        # ========================================================
        # KROK 4
        # Wgrywamy plik do NotebookLM
        #
        # wait=True oznacza:
        # "czekaj aż NotebookLM skończy analizować plik"
        # ========================================================
        await client.sources.add_file(
            notebook.id,
            pdf_path,
            wait=True
        )

        print("Plik został zaimportowany.")

        # ========================================================
        # KROK 5
        # Zadajemy pytanie NotebookLM
        #
        # W praktyce prosimy o stworzenie szczegółowej notatki
        # na podstawie przesłanego dokumentu.
        # ========================================================
        response = await client.chat.ask(
            notebook.id,
            """
            Przygotuj szczegółową notatkę z tego dokumentu.

            Uwzględnij:
            - główne tezy,
            - najważniejsze wnioski,
            - kluczowe pojęcia,
            - krótkie podsumowanie na końcu.
            """
        )

        # ========================================================
        # KROK 6
        # Wyświetlamy notatkę zwróconą przez NotebookLM
        # ========================================================
        print("\n" + "=" * 80)
        print("NOTATKA Z NOTEBOOKLM")
        print("=" * 80)

        print(response.answer)

        # ========================================================
        # KROK 7 (opcjonalny)
        # Zapisujemy notatkę do pliku TXT
        # ========================================================
        with open("notatka.txt", "w", encoding="utf-8") as f:
            f.write(response.answer)

        print("\nNotatka została zapisana do pliku: notatka.txt")


if __name__ == "__main__":
    asyncio.run(main())