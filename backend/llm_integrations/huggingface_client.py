"""
Hugging Face Inference API client for DeepSeek R1 (FREE & UNLIMITED)
No API key required for public models
"""

import requests
from typing import Optional


class HuggingFaceClient:
    """Client for Hugging Face Inference API (DeepSeek R1)"""

    def __init__(
        self,
        model: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
    ):
        """
        Initialize Hugging Face client

        Args:
            model: Model name on Hugging Face
                   Options:
                   - deepseek-ai/DeepSeek-R1-Distill-Llama-8B (fast, free)
                   - deepseek-ai/DeepSeek-R1-Distill-Qwen-7B (alternative)
        """
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional security policy writer.",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using Hugging Face Inference API

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # DeepSeek R1 reasoning takes time
            )

            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                if 'generated_text' in data[0]:
                    return data[0]['generated_text']
                elif 'text' in data[0]:
                    return data[0]['text']

            # If model is loading, wait and retry
            if isinstance(data, dict) and 'error' in data:
                if 'loading' in data['error'].lower():
                    print("  Model is loading, please wait 20 seconds and retry...")
                    import time
                    time.sleep(20)
                    return self.generate(prompt, system_prompt, temperature, max_tokens)
                else:
                    raise Exception(f"Hugging Face API Error: {data['error']}")

            return str(data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Hugging Face API Error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            True if connection successful
        """
        try:
            print("Testing Hugging Face Inference API (may take 20s if model is loading)...")
            response = self.generate(
                "Say 'Connection successful'",
                temperature=0,
                max_tokens=10
            )
            print(f"Response: {response[:100]}")
            return len(response) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("HUGGING FACE CLIENT TEST (DeepSeek R1 Distilled)")
    print("=" * 60)

    try:
        # Initialize client (NO API KEY NEEDED!)
        client = HuggingFaceClient()
        print(f"\nUsing model: {client.model}")
        print("Note: First request may take 20-30 seconds (model loading)")
        print("Subsequent requests are faster\n")

        # Test connection
        print("Testing API connection...")
        if client.test_connection():
            print("\nConnection successful!")
        else:
            print("\nConnection failed")
            exit(1)

        # Test generation
        print("\nTesting security policy generation...")
        prompt = "Write a 2-sentence security policy about SQL injection prevention."

        response = client.generate(prompt, temperature=0.3, max_tokens=200)

        print("\nGenerated Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\nHugging Face (DeepSeek R1) client test completed!")
        print("\nThis API is:")
        print("  - FREE (no cost)")
        print("  - UNLIMITED (no rate limits)")
        print("  - NO API KEY required")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
