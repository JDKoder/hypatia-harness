import requests

class OllamaWrapper:
    def __init__(self, base_url='http://localhost:11434/api/chat'):
        self.base_url = base_url

    def _make_request(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def generate_text(self, prompt, max_tokens=100):
        data = {'prompt': prompt, 'max_tokens': max_tokens}
        return self._make_request('generate', data)

    def tokenize_text(self, text):
        data = {'text': text}
        return self._make_request('tokenize', data)

    def detokenize_text(self, tokens):
        data = {'tokens': tokens}
        return self._make_request('detokenize', data)

    def stream_text(self, prompt):
        data = {'prompt': prompt}
        response = requests.post(f"{self.base_url}/generate", stream=True, json=data)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8')        