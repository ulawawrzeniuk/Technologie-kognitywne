class AppState:
    stop_recording = False
    prompt_choice = None
    highlighted_words = set()

    @classmethod
    def reset(cls):
        """Resetuje stan przed rozpoczęciem nowej sesji nagrywania."""
        cls.stop_recording = False
        cls.prompt_choice = None
        cls.highlighted_words.clear()