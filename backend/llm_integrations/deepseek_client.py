"""
DeepSeek API client for DeepSeek R1
Strong reasoning capabilities
"""

import os
import requests
from typing import Optional


class DeepSeekClient:
    """Client for DeepSeek API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Initialize DeepSeek client

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            model: Model name (default: deepseek-chat)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if not self.api_key:
            raise ValueError(
                "DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://platform.deepseek.com"
            )

        self.base_url = "https://api.deepseek.com/v1"
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a security policy expert with strong analytical reasoning.",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using DeepSeek API

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("DeepSeek API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"DeepSeek API Error: {str(e)}")

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
            return "successful" in response.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("="*60)
    print("DEEPSEEK CLIENT TEST")
    print("="*60)

    try:
        # Initialize client
        client = DeepSeekClient()
        print("\n✅ Client initialized successfully")

        # Test connection
        print("\nTesting API connection...")
        if client.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed")
            exit(1)

        # Test generation
        print("\nTesting text generation...")
        prompt = "Write a 2-sentence security policy about runtime application security."

        response = client.generate(prompt, temperature=0.3, max_tokens=200)

        print("\nGenerated Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\n✅ DeepSeek client test completed successfully!")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 To fix this:")
        print("1. Get API key from: https://platform.deepseek.com")
        print("2. Add to .env file: DEEPSEEK_API_KEY=your_key_here")
        print("3. Or set environment variable: export DEEPSEEK_API_KEY=your_key")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
