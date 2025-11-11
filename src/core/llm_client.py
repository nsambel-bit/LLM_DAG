"""LLM client for interacting with OpenRouter API."""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """Client for interacting with LLM via OpenRouter API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 4096,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Model identifier
            max_tokens: Maximum tokens in response
            base_url: API base URL
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens (uses default if None)
            **kwargs: Additional API parameters
            
        Returns:
            Generated text
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected API response format: {str(e)}")
    
    def batch_complete(
        self,
        prompts: list[str],
        temperature: float = 0.3,
        **kwargs
    ) -> list[str]:
        """
        Generate completions for multiple prompts.
        
        Args:
            prompts: List of prompts
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            List of generated texts
        """
        return [
            self.complete(prompt, temperature, **kwargs)
            for prompt in prompts
        ]


def get_llm_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMClient:
    """
    Get configured LLM client from environment variables.
    
    Args:
        api_key: Override API key
        model: Override model
        
    Returns:
        Configured LLMClient
    """
    return LLMClient(
        api_key=api_key,
        model=model or os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet"),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096"))
    )

