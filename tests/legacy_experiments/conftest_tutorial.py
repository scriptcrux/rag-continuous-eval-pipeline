import requests
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample
import pytest

@pytest.fixture
def llm_wrapper():
    llm=ChatOllama(model="llama3.2:latest",temperature=0,format="json")
    langchain_llm=LangchainLLMWrapper(llm)
    return langchain_llm
