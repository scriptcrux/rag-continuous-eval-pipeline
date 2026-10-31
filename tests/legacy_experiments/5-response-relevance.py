from ragas.metrics import Faithfulness, ResponseRelevancy, FactualCorrectness
import pytest
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
import requests
from ragas.dataset_schema import SingleTurnSample
import pytest
import os
from utils import get_llm_response, load_test_data
from ragas import evaluate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_data", load_test_data("parameterize_data_combine.json"), indirect=True
)
async def test_relevancy_factual(llm_wrapper, get_data):
    metrics = [ResponseRelevancy(llm=llm_wrapper), FactualCorrectness(llm=llm_wrapper)]

    # we use this when we have multiple metrics and evaluate set of metrics, convert this to ragas data set format
    eval_dataset = EvaluationDataset([get_data])

    #  takes data set and metrics
    results = evaluate(dataset=eval_dataset, metrics=metrics)

    print(f"results: {results}")
    # assert score > 0.8


@pytest.fixture
def get_data(request):
    test_data = request.param
    response_dict = get_llm_response(test_data=test_data)

    print(f"response_dict: {response_dict}")

    retrieved_contexts = [
        doc["page_content"] for doc in response_dict.get("retrieved_docs", [])
    ]

    print(f"User Input: {test_data['question']}")
    print(f"Model Response: {response_dict['answer']}")
    print(f"Retrieved Contexts: {retrieved_contexts}")
    print(f"Reference: {test_data['reference']}")

    sample = SingleTurnSample(
        user_input=test_data["question"],
        response=response_dict["answer"],
        retrieved_contexts=retrieved_contexts,
        reference=test_data["reference"],
    )
    return sample
