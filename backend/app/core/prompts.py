"""
Centralized prompt management for hot take generation.
Contains unified prompts that work across all agent types.
"""
from enum import Enum


class StylePrompts:
    """Unified collection of style-based prompts that work for all agents."""

    BASE_PROMPTS = {
        "controversial": "You are a provocative opinion generator. Create bold, controversial takes that challenge conventional wisdom. Be edgy but thoughtful.",
        "sarcastic": "You are a sarcastic commentator. Generate witty, sarcastic hot takes with a sharp sense of humor.",
        "optimistic": "You are an optimistic contrarian. Generate positive, uplifting hot takes that find the good in everything.",
        "pessimistic": "You are a cynical realist. Generate pessimistic hot takes that highlight the worst-case scenarios.",
        "absurd": "You are an absurdist philosopher. Generate completely ridiculous and absurd hot takes that make people laugh.",
        "analytical": "You are a deep analytical thinker. Generate hot takes that break down complex topics with nuanced analysis.",
        "philosophical": "You are a modern philosopher. Generate hot takes that question fundamental assumptions about life and society.",
        "witty": "You are a clever wordsmith. Generate hot takes that are clever, punchy, and memorable.",
        "contrarian": "You are a professional contrarian. Always take the opposite stance from popular opinion, but back it up with reasoning.",
    }


class NewsContextPrompts:
    """Unified prompt for incorporating news context into hot takes."""

    NEWS_SUFFIX = " When provided with recent news context, incorporate those current events into your hot take to make it timely and relevant. Use the news to support your perspective or provide counterpoints."


class AgentType(Enum):
    """Enumeration of available agent types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class PromptManager:
    """Central manager for retrieving unified prompts for all agent types."""

    @staticmethod
    def get_base_prompt(style: str) -> str:
        """
        Get the base prompt for a specific style.

        Args:
            style: The desired style for the hot take

        Returns:
            The appropriate base prompt string
        """
        return StylePrompts.BASE_PROMPTS.get(style, StylePrompts.BASE_PROMPTS["controversial"])

    @staticmethod
    def get_news_context_suffix() -> str:
        """
        Get the unified news context suffix.

        Returns:
            The news context suffix
        """
        return NewsContextPrompts.NEWS_SUFFIX

    @staticmethod
    def get_full_prompt(agent_type: AgentType, style: str, with_news: bool = False) -> str:
        """
        Get the complete prompt for a specific style and news context requirement.
        Note: agent_type is kept for backward compatibility but not used.

        Args:
            agent_type: The type of agent (kept for compatibility)
            style: The desired style for the hot take
            with_news: Whether to include news context instructions

        Returns:
            The complete prompt string
        """
        base_prompt = PromptManager.get_base_prompt(style)

        if with_news:
            news_suffix = PromptManager.get_news_context_suffix()
            return base_prompt + news_suffix

        return base_prompt

    @staticmethod
    def get_available_styles() -> list[str]:
        """
        Get the list of all available styles.

        Returns:
            Sorted list of available style names
        """
        return sorted(list(StylePrompts.BASE_PROMPTS.keys()))

    @staticmethod
    def get_all_available_styles() -> list[str]:
        """
        Get all available styles (same as get_available_styles for consistency).

        Returns:
            Sorted list of all available style names
        """
        return PromptManager.get_available_styles()


# Convenience constants
DEFAULT_STYLE = "controversial"
SUPPORTED_AGENTS = [AgentType.OPENAI, AgentType.ANTHROPIC]