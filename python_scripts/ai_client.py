import asyncio
from notebooklm import NotebookLMClient

async def generate_notes_from_file(filepath, style):
    print("\n[NotebookLM] Rozpoczynam generowanie notatki...")
    async with NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create("Analiza Wykladu VR")
        await client.sources.add_file(notebook.id, filepath, wait=True)
        
        if style == "MAPA":
            prompt_text = """
            Przygotuj notatkę z tego wykładu w formie szczegółowej mapy myśli. 
            Użyj wyłącznie wyraźnych wcięć, wypunktowań i logicznej hierarchii pojęć. 
            Nie pisz ciągłym tekstem. 
            Słowa zawarte pomiędzy znakami << >> są słowami kluczowymi mającymi szczególne znaczenie dla kontekstu notatki.
            """
        else:
            prompt_text  """
            Przeanalizuj cały wykład i stwórz kompletną notatkę do nauki. Zwaracaj szczególna uwage na wyróżnione słowa.

            Struktura notatki:

            # Temat główny

            ## Najważniejsze pojęcia
            Krótkie wyjaśnienia kluczowych terminów.

            ## Szczegółowe omówienie
            Dokładne wyjaśnienie wszystkich zagadnień przedstawionych na wykładzie.

            ## Zależności i mechanizmy
            Wyjaśnij, jak poszczególne pojęcia są ze sobą powiązane oraz jakie występują zależności przyczynowo-skutkowe.

            ## Przykłady
            Zbierz wszystkie przykłady podane podczas wykładu i wyjaśnij, co ilustrują.

            ## Najważniejsze informacje do zapamiętania
            Zestaw najistotniejszych faktów, definicji, wzorów i wniosków.

            Dodatkowe zasady:
            - Zachowaj maksymalną ilość wartości merytorycznej.
            - Usuń dygresje, powtórzenia i wypełniacze językowe.
            - Wyjaśniaj trudne pojęcia prostym językiem.
            - Nie zakładaj wiedzy wykraczającej poza materiał wykładu.
            - Jeśli jakaś informacja jest niejednoznaczna, zaznacz to.
            - Priorytetem jest zrozumiałość, przejrzystość i użyteczność podczas nauki do egzaminu.
            """



        response = await client.chat.ask(notebook.id, prompt_text)
        return response.answer
