"""
Cloud AI Interface
==================

Abstraction layer for interacting with cloud AI services.
Supports Claude (Anthropic) and GPT (OpenAI) with automatic fallback.

Environment Variables:
    ANTHROPIC_API_KEY: Claude API key
    OPENAI_API_KEY: OpenAI API key
    RTAI_PRIMARY_MODEL: Primary model to use (default: claude)
    RTAI_FALLBACK_MODEL: Fallback model if primary fails (default: gpt)
"""

import os
import logging
from typing import Optional, List, Dict, Any
from enum import Enum
import time

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    CLAUDE = "claude"
    GPT = "gpt"
    GPT_MINI = "gpt-mini"


class AIInterface:
    """
    Unified interface for cloud AI services.

    Handles API calls, rate limiting, error handling, and fallback logic.
    """

    def __init__(self,
                 primary_provider: str = None,
                 fallback_provider: str = None,
                 anthropic_api_key: str = None,
                 openai_api_key: str = None):
        """
        Initialize AI interface.

        Args:
            primary_provider: Primary AI provider ('claude', 'gpt')
            fallback_provider: Fallback provider if primary fails
            anthropic_api_key: Claude API key (or from env)
            openai_api_key: OpenAI API key (or from env)
        """
        self.primary_provider = primary_provider or os.getenv('RTAI_PRIMARY_MODEL', 'claude')
        self.fallback_provider = fallback_provider or os.getenv('RTAI_FALLBACK_MODEL', 'gpt')

        # API keys
        self.anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Seconds between requests

        # Initialize clients
        self.anthropic_client = None
        self.openai_client = None

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize API clients for available providers."""
        # Initialize Anthropic (Claude)
        if self.anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
                logger.info("✓ Claude (Anthropic) client initialized")
            except ImportError:
                logger.warning("anthropic package not installed. Install with: pip install anthropic")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")

        # Initialize OpenAI (GPT)
        if self.openai_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_key)
                logger.info("✓ OpenAI (GPT) client initialized")
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

    def _rate_limit(self):
        """Enforce minimum time between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def complete(self,
                 prompt: str,
                 system_prompt: str = None,
                 max_tokens: int = 2000,
                 temperature: float = 0.7,
                 provider: str = None) -> Optional[str]:
        """
        Get completion from AI model.

        Args:
            prompt: User prompt/question
            system_prompt: System instructions (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            provider: Force specific provider ('claude', 'gpt', or None for default)

        Returns:
            AI response text, or None if all attempts fail
        """
        provider = provider or self.primary_provider

        # Try primary provider
        try:
            response = self._complete_with_provider(
                provider=provider,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            if response:
                return response
        except Exception as e:
            logger.warning(f"Primary provider ({provider}) failed: {e}")

        # Try fallback provider
        if self.fallback_provider and self.fallback_provider != provider:
            try:
                logger.info(f"Falling back to {self.fallback_provider}...")
                response = self._complete_with_provider(
                    provider=self.fallback_provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                if response:
                    return response
            except Exception as e:
                logger.error(f"Fallback provider ({self.fallback_provider}) failed: {e}")

        logger.error("All AI providers failed")
        return None

    def _complete_with_provider(self,
                                provider: str,
                                prompt: str,
                                system_prompt: str = None,
                                max_tokens: int = 2000,
                                temperature: float = 0.7) -> Optional[str]:
        """Execute completion with specific provider."""
        self._rate_limit()

        if provider == 'claude':
            return self._complete_claude(prompt, system_prompt, max_tokens, temperature)
        elif provider in ['gpt', 'gpt-mini']:
            return self._complete_gpt(prompt, system_prompt, max_tokens, temperature, mini=(provider == 'gpt-mini'))
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _complete_claude(self,
                        prompt: str,
                        system_prompt: str = None,
                        max_tokens: int = 2000,
                        temperature: float = 0.7) -> Optional[str]:
        """Get completion from Claude (Anthropic)."""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": "claude-3-5-sonnet-20241022",  # Latest Claude model
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response = self.anthropic_client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _complete_gpt(self,
                     prompt: str,
                     system_prompt: str = None,
                     max_tokens: int = 2000,
                     temperature: float = 0.7,
                     mini: bool = False) -> Optional[str]:
        """Get completion from GPT (OpenAI)."""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY.")

        # Choose model
        if mini:
            model = "gpt-4o-mini"  # Cheaper, faster option
        else:
            model = "gpt-4o"  # Latest GPT-4 model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def analyze_json(self,
                    prompt: str,
                    system_prompt: str = None,
                    max_tokens: int = 2000) -> Optional[Dict]:
        """
        Get structured JSON response from AI.

        Useful for getting structured data like pattern analysis results.

        Args:
            prompt: Prompt asking for JSON response
            system_prompt: System instructions
            max_tokens: Max tokens

        Returns:
            Parsed JSON dict, or None if failed
        """
        import json

        # Add JSON instruction to prompt
        enhanced_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown or explanation."

        response = self.complete(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for structured output
        )

        if not response:
            return None

        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            return None

    def is_available(self, provider: str = None) -> bool:
        """
        Check if AI provider is available.

        Args:
            provider: Provider to check (or None for primary)

        Returns:
            True if provider is initialized and ready
        """
        provider = provider or self.primary_provider

        if provider == 'claude':
            return self.anthropic_client is not None
        elif provider in ['gpt', 'gpt-mini']:
            return self.openai_client is not None
        else:
            return False


# Singleton instance
_ai_interface_instance: Optional[AIInterface] = None


def get_ai_interface() -> AIInterface:
    """
    Get singleton AIInterface instance.

    Returns:
        Configured AIInterface
    """
    global _ai_interface_instance

    if _ai_interface_instance is None:
        _ai_interface_instance = AIInterface()

    return _ai_interface_instance
