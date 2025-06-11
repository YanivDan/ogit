import requests
import json

class OllamaClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def send_request(self, payload):
        try:
            response = requests.post(self.endpoint, json=payload, stream=True)
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue
                try:
                    part = json.loads(line)
                    full_response += part.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"[WARN] Skipped malformed line: {line}")
                    continue

            return {"response": full_response.strip()}

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to reach Ollama API: {e}")
            return {"response": ""}

    def get_response(self, data):
        payload = {
            "model": data["model"],
            "prompt": data["prompt"]
        }
        response_data = self.send_request(payload)
        raw_msg = response_data.get("response", "").strip()

        return self._clean_response(raw_msg) or "No commit message generated."

    def _clean_response(self, msg):
        # Remove surrounding triple backticks if present
        msg = msg.strip()
        if msg.startswith("```") and msg.endswith("```"):
            lines = msg.splitlines()
            msg = "\n".join(lines[1:-1]).strip()
        return msg

def list_ollama_models():
    """List available models from local Ollama server."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        return [m['name'] for m in data.get('models', [])]
    except Exception as e:
        print(f"Error fetching models from Ollama: {e}")
        return []
