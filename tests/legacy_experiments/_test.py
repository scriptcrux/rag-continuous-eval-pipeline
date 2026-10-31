import pytest
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference,LLMContextRecall
from ragas.dataset_schema import SingleTurnSample
import requests

@pytest.mark.asyncio
async def test_context_precision():
    llm=ChatOllama(model="llama3.2:latest",temperature=0,format="json")

    langchain_llm=LangchainLLMWrapper(llm)

    contex_precision=LLMContextPrecisionWithoutReference(llm=langchain_llm)

    responseDict=requests.post('https://rahulshettyacademy.com/rag-llm/ask',json={
        question:"How many articles are there in the Selenium webdriver python course?",
        chat_history:[],
    })

    sample=SingleTurnSample(
        user_input="How many articles are there in the Selenium webdriver python course?",
        response=responseDict["answer"],
        retrieved_contexts=[
            responseDict["retrieved_docs"][0]["page_content"],
            responseDict["retrieved_docs"][1]["page_content"],
            responseDict["retrieved_docs"][2]["page_content"],
        ],
    )

    result=await contex_precision.single_turn_ascore(sample=sample)
    print(result)


@pytest.mark.asyncio
async def test_context_recall():

    llm=ChatOllama(model="llama3.2:latest",temperature=0,format="json")

    langchain_llm=LangchainLLMWrapper(llm)

    context_recall=LLMContextRecall(llm=langchain_llm)

    sample=SingleTurnSample(
        user_input=question,
        retrieved_contexts=[
            responseDict["retrieved_docs"][0]["page_content"],
            responseDict["retrieved_docs"][1]["page_content"],
            responseDict["retrieved_docs"][2]["page_content"],
        ],
        # added as 23 as total count is 23
        reference="23",
    )


    score=await context_recall.single_turn_ascore(sample)
    assert score> 0.7