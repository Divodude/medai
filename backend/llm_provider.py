import threading
from typing import Optional

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from config import GROQ_API_KEY, GROQ_MODEL, HF_TOKEN


class LLMProvider:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LLMProvider, cls).__new__(cls)
                cls._instance._llm = None
                cls._instance._embeddings = None
        return cls._instance

    def get_llm(self, temperature: float = 0.3) -> ChatGroq:
        """
        Returns a ChatGroq instance.
        """
        if self._llm is None or self._llm.temperature != temperature:
            self._llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model=GROQ_MODEL,
                temperature=temperature
            )
        return self._llm

    def get_embeddings(self) -> HuggingFaceEndpointEmbeddings:
        """
        Returns the HuggingFace Embeddings instance using the API.
        """
        if self._embeddings is None:
            # We use HuggingFace inference API to generate embeddings.
            # fallback to local HuggingFaceEmbeddings if HF_TOKEN is not provided.
            if HF_TOKEN:
                self._embeddings = HuggingFaceEndpointEmbeddings(
                    model="sentence-transformers/all-MiniLM-L6-v2",
                    huggingfacehub_api_token=HF_TOKEN,
                )
            else:
                from langchain_huggingface import HuggingFaceEmbeddings
                self._embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
        return self._embeddings

# Global singleton instance
llm_provider = LLMProvider()

def get_llm(temperature: float = 0.3):
    return llm_provider.get_llm(temperature)

def get_embeddings():
    return llm_provider.get_embeddings()
