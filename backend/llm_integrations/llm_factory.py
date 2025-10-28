"""
Factory pattern for LLM client selection
"""

from typing import Literal, Union
from .groq_client import GroqClient
from .deepseek_client import DeepSeekClient
from .openai_client import OpenAIClient


LLMProvider = Literal["groq", "deepseek", "openai"]


class LLMFactory:
    """Factory for creating LLM clients"""

    @staticmethod
    def get_client(provider: LLMProvider) -> Union[GroqClient, DeepSeekClient, OpenAIClient]:
        """
        Get LLM client based on provider name

        Args:
            provider: Provider name ("groq", "deepseek", or "openai")

        Returns:
            Initialized LLM client

        Raises:
            ValueError: If provider is unknown
        """
        if provider == "groq":
            return GroqClient()
        elif provider == "deepseek":
            return DeepSeekClient()
        elif provider == "openai":
            return OpenAIClient()
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                "Must be one of: 'groq', 'deepseek', 'openai'"
            )

    @staticmethod
    def test_all_providers() -> dict:
        """
        Test all LLM providers

        Returns:
            Dict with test results for each provider
        """
        results = {}

        providers = ["groq", "deepseek", "openai"]

        for provider in providers:
            try:
                client = LLMFactory.get_client(provider)
                if client.test_connection():
                    results[provider] = "✅ Connected"
                else:
                    results[provider] = "❌ Connection failed"
            except ValueError as e:
                results[provider] = f"❌ Config error: {str(e)}"
            except Exception as e:
                results[provider] = f"❌ Error: {str(e)}"

        return results


# Test function
if __name__ == "__main__":
    print("="*60)
    print("LLM FACTORY TEST")
    print("="*60)

    # Test factory creation
    print("\n1. Testing factory creation...")
    try:
        groq = LLMFactory.get_client("groq")
        print("✅ Groq client created")

        deepseek = LLMFactory.get_client("deepseek")
        print("✅ DeepSeek client created")

        openai_client = LLMFactory.get_client("openai")
        print("✅ OpenAI client created")

    except Exception as e:
        print(f"❌ Factory creation failed: {e}")

    # Test invalid provider
    print("\n2. Testing invalid provider...")
    try:
        invalid = LLMFactory.get_client("invalid")
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # Test all providers
    print("\n3. Testing all provider connections...")
    print("(This may take a moment...)\n")

    results = LLMFactory.test_all_providers()

    for provider, result in results.items():
        print(f"  {provider:10} : {result}")

    print("\n✅ LLM Factory test completed!")

    # Summary
    success_count = sum(1 for r in results.values() if "✅" in r)
    total = len(results)

    print(f"\nSummary: {success_count}/{total} providers connected successfully")

    if success_count == 0:
        print("\n⚠️  No providers connected. Make sure API keys are set in .env file:")
        print("   - GROQ_API_KEY")
        print("   - DEEPSEEK_API_KEY")
        print("   - OPENAI_API_KEY")
