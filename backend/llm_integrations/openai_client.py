"""
OpenAI API client for GPT-4o-mini
Main orchestrator model
"""

import os
from typing import Optional
try:
    from openai import OpenAI
except ImportError:
    print("Warning: openai library not installed. Run: pip install openai")
    OpenAI = None


class OpenAIClient:
    """Client for OpenAI API (GPT-4o-mini)"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://platform.openai.com"
            )

        if OpenAI is None:
            raise ImportError("openai library not installed. Run: pip install openai")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are an expert security policy writer specializing in compliance frameworks.",
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using OpenAI API

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")

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
    print("OPENAI CLIENT TEST")
    print("="*60)

    try:
        # Initialize client
        client = OpenAIClient()
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
        prompt = "Write a 2-sentence executive summary about cybersecurity policy."

        response = client.generate(prompt, temperature=0.3, max_tokens=200)

        print("\nGenerated Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\n✅ OpenAI client test completed successfully!")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 To fix this:")
        print("1. Get API key from: https://platform.openai.com")
        print("2. Add to .env file: OPENAI_API_KEY=your_key_here")
        print("3. Or set environment variable: export OPENAI_API_KEY=your_key")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
