"""
Ollama LLM Client

Purpose: Provides interface to Ollama for AI agent reasoning.
Uses Gemma3 model for forensic economic analysis.
"""

import ollama
from typing import Dict, Any, Optional
import json


class OllamaClient:
    """Client for interacting with Ollama LLM (Gemma3)."""

    def __init__(self, model: str = "gemma3:1b", host: str = "http://localhost:11434"):
        """
        Initialize Ollama client.

        Args:
            model: Model name to use (default: gemma3:1b)
            host: Ollama host URL
        """
        self.model = model
        self.host = host
        print(f"[OLLAMA_CLIENT] Initialized with model: {model}")

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat messages to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to stream the response

        Returns:
            Response dictionary with 'message' and 'content'
        """
        try:
            print(f"[OLLAMA_CLIENT] Sending {len(messages)} messages to {self.model}...")

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': temperature,
                },
                stream=stream
            )

            if stream:
                return response
            else:
                content = response['message']['content']
                print(f"[OLLAMA_CLIENT] Received response ({len(content)} chars)")
                return response

        except Exception as e:
            print(f"[OLLAMA_CLIENT] ERROR: {str(e)}")
            raise

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> str:
        """
        Generate a completion from a prompt.

        Args:
            prompt: The prompt text
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature
            json_mode: Whether to request JSON output

        Returns:
            Generated text response
        """
        messages = []

        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })

        messages.append({
            'role': 'user',
            'content': prompt
        })

        if json_mode:
            messages[-1]['content'] += "\n\nRespond with valid JSON only."

        response = self.chat(messages, temperature=temperature)
        return response['message']['content']

    def analyze_with_context(
        self,
        task: str,
        context: Dict[str, Any],
        system_role: str = "You are a forensic economics expert AI agent."
    ) -> str:
        """
        Analyze a task with given context.

        Args:
            task: Description of the task to perform
            context: Context data as dictionary
            system_role: System role description

        Returns:
            Analysis text from the LLM
        """
        # Format context as readable text
        context_str = json.dumps(context, indent=2)

        prompt = f"""Task: {task}

Context Data:
{context_str}

Provide your analysis based on the context data above."""

        return self.generate_completion(
            prompt=prompt,
            system_prompt=system_role,
            temperature=0.7
        )

    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response that may contain extra text.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            # Try direct parse first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re
            json_pattern = r'\{[^{}]*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)

            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

            return None


# Global client instance
_ollama_client = None


def get_ollama_client(model: str = "gemma2:2b") -> OllamaClient:
    """
    Get or create global Ollama client instance.

    Args:
        model: Model name to use

    Returns:
        OllamaClient instance
    """
    global _ollama_client

    if _ollama_client is None:
        _ollama_client = OllamaClient(model=model)

    return _ollama_client
