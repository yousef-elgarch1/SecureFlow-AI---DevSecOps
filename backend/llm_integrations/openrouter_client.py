"""
OpenRouter API client for DeepSeek R1 (FREE)
Provides access to DeepSeek R1 via OpenRouter's free tier
"""

import os
import requests
from typing import Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # dotenv not required for test


class OpenRouterClient:
    """Client for OpenRouter API (DeepSeek R1)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-r1:free"
    ):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model name (default: deepseek/deepseek-r1:free)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://openrouter.ai"
            )

        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional security policy writer.",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using OpenRouter API (DeepSeek R1)

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/AI_Devsecops",  # Optional
                "X-Title": "AI DevSecOps Policy Generator"  # Optional
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            # Debug: print response structure
            if 'choices' not in data or not data['choices']:
                print(f"DEBUG: Unexpected response structure: {data}")
                raise Exception(f"Invalid response format: {data}")

            return data['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API Error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Response parsing error: {str(e)}. Response: {data}")

    def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            True if connection successful
        """
        try:
            response = self.generate(
                "Say 'Connection successful'",
                temperature=0,
                max_tokens=10
            )
            print(f"Response received: {response[:100]}")
            return "successful" in response.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("OPENROUTER CLIENT TEST (DeepSeek R1)")
    print("=" * 60)

    try:
        # Initialize client
        client = OpenRouterClient()
        print("\nClient initialized successfully")

        # Test connection
        print("\nTesting API connection...")
        if client.test_connection():
            print("Connection successful!")
        else:
            print("Connection failed")
            exit(1)

        # Test generation
        print("\nTesting text generation with DeepSeek R1...")
        prompt = "Write a 2-sentence security policy about SQL injection prevention."

        response = client.generate(prompt, temperature=0.3, max_tokens=200)

        print("\nGenerated Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\nOpenRouter (DeepSeek R1) client test completed successfully!")

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nTo fix this:")
        print("1. Get API key from: https://openrouter.ai")
        print("2. Add to .env file: OPENROUTER_API_KEY=your_key_here")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
