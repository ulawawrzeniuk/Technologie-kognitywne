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
            prompt_text = """
            Przygotuj bardzo szczegółową notatkę z tego wykładu w formie profesjonalnego, ciągłego tekstu. 
            Podziel tekst na czytelne, spójne akapity. 
            Absolutnie nie używaj wypunktowań ani list.
            Słowa zawarte pomiędzy znakami << >> są słowami kluczowymi mającymi szczególne znaczenie dla kontekstu notatki.
            """

        response = await client.chat.ask(notebook.id, prompt_text)
        return response.answer