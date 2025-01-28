import requests

# MyMemory API endpoint
MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"

def translate_text(text, source_lang='en', target_lang='fr'):
    params = {
        "q": text,  # Text to translate
        "langpair": f"{source_lang}|{target_lang}"  # Language pair, e.g., 'en|fr'
    }

    try:
        response = requests.get(MYMEMORY_API_URL, params=params)  # Sending GET request
        response.raise_for_status()  # Raise an exception for HTTP errors
        # Extracting translated text from the response
        return response.json()["responseData"]["translatedText"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with MyMemory API: {e}")

# Example usage:
text_to_translate = "Hello, how are you?"
translated_text = translate_text(text_to_translate, source_lang='en', target_lang='fr')
print(f"Translated Text: {translated_text}")
