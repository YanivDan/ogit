import requests


class OllamaClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def send_request(self, data):
        response = requests.post(self.endpoint, json=data)
        response.raise_for_status()
        return response.json()

    def get_response(self, data):
        response_data = self.send_request(data)
        return response_data.get('commit_message', 'No commit message generated.')


def list_ollama_models():
    """List available models from local Ollama server."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        # Ollama returns models under 'models' key, each with a 'name'
        return [m['name'] for m in data.get('models', [])]
    except Exception as e:
        print(f"Error fetching models from Ollama: {e}")
        return []