from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """
    Base interface for all AI model providers.

    Every provider such as Gemini, OpenAI, or a local
    model must implement the generate() method.
    """

    @abstractmethod
    def generate(self, query: str):
        """
        Generate a response for the given query.
        """
        pass