"""
LLM Client - Interface for Ollama
=================================
Provides a unified interface to interact with local LLM models via Ollama.
Supports multiple models and streaming responses.
"""

import ollama
import json
import os


class LLMClient:
    """Client for interacting with Ollama local LLM models"""
    
    def __init__(self, model: str = "llama3", temperature: float = 0.7, max_tokens: int = 2048):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._verify_model()
    
    def _verify_model(self):
        """Verify that the model is available"""
        try:
            available_models = ollama.list()
            model_names = []
            
            if hasattr(available_models, 'models'):
                model_names = [m.model for m in available_models.models]
            elif isinstance(available_models, dict) and 'models' in available_models:
                model_names = [m.get('name', '').split(':')[0] for m in available_models.get('models', [])]
            
            # Check if model is available
            model_base = self.model.split(':')[0]
            if model_base not in model_names:
                print(f"Warning: Model '{self.model}' not found. Available: {model_names}")
                print(f"Attempting to use '{self.model}' anyway...")
                
        except Exception as e:
            print(f"Warning verifying model: {e}")
    
    def ask(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """Send a prompt to the LLM and get a response"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ask_json(self, prompt: str) -> dict:
        """Send a prompt and parse JSON response"""
        json_prompt = f"""{prompt}

Return your response as valid JSON only. No additional text."""
        
        response = self.ask(json_prompt)
        
        # Try to parse JSON
        try:
            # Handle potential markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {str(e)}", "raw_response": response}
    
    def ask_stream(self, prompt: str):
        """Stream response from LLM"""
        try:
            stream = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def change_model(self, model: str):
        """Change the active model"""
        self.model = model
        self._verify_model()
    
    @staticmethod
    def list_models() -> list:
        """List available models"""
        try:
            response = ollama.list()
            if hasattr(response, 'models'):
                return [{"name": m.model, "size": getattr(m, 'size', 0)} for m in response.models]
            elif isinstance(response, dict) and 'models' in response:
                return response.get('models', [])
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []


def get_default_client() -> LLMClient:
    """Get a default LLM client with environment variables"""
    model = os.getenv("OLLAMA_MODEL", "llama3")
    temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "2048"))
    
    return LLMClient(model=model, temperature=temperature, max_tokens=max_tokens)

