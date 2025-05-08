import requests
from requests.exceptions import RequestException
from app.root_logger import get_root_logger


logger = get_root_logger(service_name="silero_tts")

class SileroTTS:
    def __init__(self,
                 url: str,
                 speaker: str = 'baya'
                 ):
        self._url = url
        self._speaker = speaker

    def generate_audio(self, text: str):
        try:
            request_params = {
                'VOICE': self._speaker,
                'INPUT_TEXT': text,
            }
            response = requests.get(
                url=self._url + '/process',
                params=request_params
            )
            response.raise_for_status()
            return response.content
        except RequestException as e:
            logger.error(f"Error Silero TTS: {e}")
            raise
    
    def clear_audio_cache(self):
        try:
            return requests.get(url=self._url + '/clear_cache')
        except requests.exceptions.RequestException:
            return None