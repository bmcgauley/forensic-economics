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

    def generate_structured_completion(
        self,
        prompt: str,
        system_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON completion with schema enforcement.

        Args:
            prompt: The prompt text
            system_prompt: System prompt for context
            schema: JSON schema dict for output validation
            temperature: Sampling temperature (lower = more consistent)
            max_retries: Number of retry attempts if JSON parsing fails

        Returns:
            Parsed JSON dict matching the schema

        Raises:
            ValueError: If unable to generate valid JSON after retries
        """
        # Add schema instructions to prompt
        schema_str = json.dumps(schema, indent=2)

        enhanced_prompt = f"""{prompt}

CRITICAL INSTRUCTIONS:
You MUST respond with ONLY a valid JSON object containing your ACTUAL ANALYSIS DATA.

DO NOT output the schema definition itself.
DO NOT output markdown code fences.
DO NOT output any explanatory text.

The JSON object must have these fields:
- "key_findings": array of 2-3 strings (your actual findings about this case)
- "risk_factors": array of 1-2 strings (your actual risk factors)
- "assumptions": array of 1-2 strings (your actual assumptions)
- "confidence_level": string, one of: "high", "medium", or "low"
- "recommendation": string, max 300 chars (your actual recommendation)

EXAMPLE FORMAT (DO NOT COPY THIS CONTENT, USE YOUR OWN ANALYSIS):
{{
  "key_findings": ["Finding 1 about this specific case", "Finding 2 about this specific case"],
  "risk_factors": ["Risk factor 1 for this case"],
  "assumptions": ["Assumption 1 made in analysis"],
  "confidence_level": "medium",
  "recommendation": "Your recommendation for this specific case"
}}

Now provide YOUR JSON object with your ACTUAL analysis:"""

        for attempt in range(max_retries + 1):
            try:
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': enhanced_prompt}
                ]

                # Make API call
                print(f"[OLLAMA_CLIENT] Requesting structured JSON (attempt {attempt + 1}/{max_retries + 1})...")
                response = self.chat(messages, temperature=temperature)
                response_text = response['message']['content'].strip()

                # Try to parse JSON
                try:
                    # First try direct parse
                    result = json.loads(response_text)
                    print(f"[OLLAMA_CLIENT] Successfully parsed JSON response")
                    return result
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown or surrounding text
                    import re

                    # Remove markdown code fences
                    cleaned = re.sub(r'```json\s*', '', response_text)
                    cleaned = re.sub(r'```\s*$', '', cleaned)
                    cleaned = cleaned.strip()

                    # Try to find JSON object
                    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(0))
                        print(f"[OLLAMA_CLIENT] Extracted and parsed JSON from response")
                        return result

                    # If we couldn't parse, log and retry
                    print(f"[OLLAMA_CLIENT] Failed to parse JSON (attempt {attempt + 1}): {response_text[:200]}")
                    if attempt < max_retries:
                        print(f"[OLLAMA_CLIENT] Retrying...")
                        continue
                    else:
                        raise ValueError(f"Could not parse JSON from response after {max_retries + 1} attempts: {response_text[:200]}")

            except Exception as e:
                if attempt < max_retries:
                    print(f"[OLLAMA_CLIENT] Error on attempt {attempt + 1}: {e}, retrying...")
                    continue
                else:
                    print(f"[OLLAMA_CLIENT] All retry attempts failed: {e}")
                    raise


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
