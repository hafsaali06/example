import requests

class OpenTTSClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def get_available_languages(self, tts_name=None):
        url = f"{self.base_url}/api/languages"
        params = {'tts_name': tts_name} if tts_name else {}
        response = requests.get(url, params=params)
        return response.json()

    def get_available_voices(self, language=None, locale=None, gender=None, tts_name=None):
        url = f"{self.base_url}/api/voices"
        params = {
            'language': language,
            'locale': locale,
            'gender': gender,
            'tts_name': tts_name
        }
        response = requests.get(url, params=params)
        return response.json()

    def speak_text(self, voice, text, vocoder=None, denoiser_strength=None, cache=True):
        url = f"{self.base_url}/api/tts"
        params = {
            'voice': voice,
            'text': text,
            'vocoder': vocoder,
            'denoiserStrength': denoiser_strength,
            'cache': cache
        }
        response = requests.get(url, params=params)
        return response.content

# Example usage:
client = OpenTTSClient("http://localhost:5500")
available_languages = client.get_available_languages()
print("Available Languages:", available_languages)

available_voices = client.get_available_voices(language="en")
print("Available Voices:", available_voices)

audio_data = client.speak_text(voice="espeak:en", text="Hello, world!")
with open("output.wav", "wb") as f:
    f.write(audio_data)
