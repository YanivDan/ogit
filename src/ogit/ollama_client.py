import requests
import json
import logging
from typing import Dict, List, Optional, Any
import time

from .constants import (
    OLLAMA_TAGS_ENDPOINT, OLLAMA_TIMEOUT, CONVENTIONAL_COMMIT_TYPES
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, endpoint: str, timeout: int = OLLAMA_TIMEOUT):
        """
        Initialize Ollama client.
        
        Args:
            endpoint: API endpoint URL
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout
        logger.debug(f"Initialized OllamaClient with endpoint: {endpoint}")

    def send_request(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Send request to Ollama API.
        
        Args:
            payload: Request payload
            
        Returns:
            Response dictionary with 'response' key
        """
        try:
            logger.debug(f"Sending request to Ollama: model={payload.get('model')}")
            start_time = time.time()
            
            response = requests.post(
                self.endpoint, 
                json=payload, 
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue
                try:
                    part = json.loads(line)
                    full_response += part.get("response", "")
                except json.JSONDecodeError:
                    logger.warning(f"Skipped malformed JSON line: {line[:100]}...")
                    continue
            
            duration = time.time() - start_time
            logger.debug(f"Ollama request completed in {duration:.2f}s, response length: {len(full_response)}")
            
            return {"response": full_response.strip()}

        except requests.exceptions.Timeout:
            logger.error(f"Ollama API request timed out after {self.timeout}s")
            return {"response": ""}
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama API. Is Ollama running?")
            return {"response": ""}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            return {"response": ""}
        except Exception as e:
            logger.error(f"Unexpected error in Ollama request: {e}")
            return {"response": ""}

    def get_response(self, data: Dict[str, str]) -> str:
        """
        Get commit message from Ollama.
        
        Args:
            data: Dictionary containing 'model' and 'prompt' keys
            
        Returns:
            Generated commit message
        """
        payload = {
            "model": data["model"],
            "prompt": self._enhance_prompt(data["prompt"]),
            "stream": True
        }
        
        response_data = self.send_request(payload)
        raw_msg = response_data.get("response", "").strip()

        if not raw_msg:
            logger.warning("No response received from Ollama")
            return "No commit message generated."
        
        cleaned_msg = self._clean_response(raw_msg)
        logger.debug(f"Generated commit message: {cleaned_msg[:50]}...")
        return cleaned_msg or "No commit message generated."

    def _enhance_prompt(self, original_prompt: str) -> str:
        """
        Enhance the prompt with conventional commit guidelines.
        
        Args:
            original_prompt: Original prompt
            
        Returns:
            Enhanced prompt
        """
        conventional_types = ", ".join(CONVENTIONAL_COMMIT_TYPES)
        
        enhanced_prompt = f"""{original_prompt}

Please follow conventional commit format: <type>(<scope>): <description>

Available types: {conventional_types}

Guidelines:
- Use imperative mood ("add" not "adds" or "added")
- Keep the first line under 50 characters
- Be specific and concise
- Focus on what the change does, not how it was implemented

Return only the commit message, no explanations or formatting."""
        
        logger.debug("Enhanced prompt with conventional commit guidelines")
        return enhanced_prompt

    def _clean_response(self, msg: str) -> str:
        """
        Clean the response from Ollama.
        
        Args:
            msg: Raw response message
            
        Returns:
            Cleaned commit message
        """
        msg = msg.strip()
        
        # Remove surrounding triple backticks if present
        if msg.startswith("```") and msg.endswith("```"):
            lines = msg.splitlines()
            msg = "\n".join(lines[1:-1]).strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "commit message:", "commit:", "message:", 
            "git commit:", "git commit message:"
        ]
        
        for prefix in prefixes_to_remove:
            if msg.lower().startswith(prefix):
                msg = msg[len(prefix):].strip()
                break
        
        # Remove quotes if the entire message is quoted
        if (msg.startswith('"') and msg.endswith('"')) or (msg.startswith("'") and msg.endswith("'")):
            msg = msg[1:-1].strip()
        
        return msg


def list_ollama_models() -> List[str]:
    """List available models from local Ollama server.
    
    Returns:
        List of available model names
    """
    try:
        logger.debug("Fetching available models from Ollama")
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        models = [m['name'] for m in data.get('models', [])]
        logger.debug(f"Found {len(models)} models: {models}")
        return models
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama to fetch models. Is Ollama running?")
        return []
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching models from Ollama")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error fetching models from Ollama: {e}")
        return []
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Invalid response format from Ollama: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching models from Ollama: {e}")
        return []


def check_ollama_health() -> bool:
    """Check if Ollama is running and accessible.
    
    Returns:
        True if Ollama is healthy
    """
    try:
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=5)
        is_healthy = response.status_code == 200
        logger.debug(f"Ollama health check: {'OK' if is_healthy else 'FAILED'}")
        return is_healthy
    except Exception as e:
        logger.debug(f"Ollama health check failed: {e}")
        return False
