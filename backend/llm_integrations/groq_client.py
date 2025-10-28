"""
Groq API client for Llama 3.3 70B
Fast inference with free tier
"""

import os
from typing import Optional
try:
    from groq import Groq
except ImportError:
    print("Warning: groq library not installed. Run: pip install groq")
    Groq = None


class GroqClient:
    """Client for Groq API (Llama 3.3 70B)"""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model name (default: llama-3.3-70b-versatile)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://console.groq.com"
            )

        if Groq is None:
            raise ImportError("groq library not installed. Run: pip install groq")

        self.client = Groq(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional security policy writer.",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using Groq API

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
            raise Exception(f"Groq API Error: {str(e)}")

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
    print("GROQ CLIENT TEST")
    print("="*60)

    try:
        # Initialize client
        client = GroqClient()
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
        prompt = "Write a 2-sentence security policy about SQL injection prevention."

        response = client.generate(prompt, temperature=0.3, max_tokens=200)

        print("\nGenerated Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\n✅ Groq client test completed successfully!")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 To fix this:")
        print("1. Get API key from: https://console.groq.com")
        print("2. Add to .env file: GROQ_API_KEY=your_key_here")
        print("3. Or set environment variable: export GROQ_API_KEY=your_key")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
