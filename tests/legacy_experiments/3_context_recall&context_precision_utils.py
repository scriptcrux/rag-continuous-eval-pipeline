import pytest
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference,LLMContextRecall
from ragas.dataset_schema import SingleTurnSample
import requests
from utils import get_llm_response,load_test_data



@pytest.fixture
def get_data(request):
    test_data=request.param
    responseDict = get_llm_response(test_data)

    retrieved_context=[doc["page_content"] for doc in responseDict["retrieved_docs"]]

    sample=SingleTurnSample(
        user_input=test_data["question"],
        response=responseDict["answer"],
        retrieved_contexts=retrieved_context,
        reference=test_data["reference"],
    )
    return sample


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented")
async def test_context_precision(llm_wrapper,get_data):
    contex_precision=LLMContextPrecisionWithoutReference(llm=llm_wrapper)
    result=await contex_precision.single_turn_ascore(sample=get_data)
    print(result)


@pytest.mark.asyncio
@pytest.mark.parametrize("get_data",load_test_data(),
    indirect=True)
async def test_context_recall(llm_wrapper,get_data):
    context_recall=LLMContextRecall(llm=llm_wrapper)
    score=await context_recall.single_turn_ascore(sample=get_data)
    assert score> 0.7