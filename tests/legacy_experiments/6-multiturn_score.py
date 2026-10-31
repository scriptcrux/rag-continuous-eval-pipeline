from ragas.metrics import Faithfulness, TopicAdherenceScore
import pytest
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample, MultiTurnSample
import requests
from ragas.dataset_schema import SingleTurnSample
import pytest
import os
from ragas.messages import HumanMessage, AIMessage


@pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "get_data", load_topic_adherence("parameterize_data_faithfulness.json"), indirect=True
# )
async def test_faithfulness(llm_wrapper, get_data):
    topic_score = TopicAdherenceScore(llm=llm_wrapper)

    score = await topic_score.multi_turn_ascore(get_data)
    print(f"score: {score}")
    assert score > 0.8


@pytest.fixture
def get_data(request):
    # test_data = request.param
    # response_dict = get_llm_response(test_data=test_data)

    conversations = [
        HumanMessage(
            content="how many articles are there in the selenium webdriver python course?"
        ),
        AIMessage(
            content="There are 23 articles in the Selenium WebDriver Python course."
        ),
        HumanMessage(
            content="how many downloadable resources are there in this course?"
        ),
        AIMessage(
            content="There are 4 downloadable resources in the Selenium WebDriver Python course."
        ),
    ]
    # as its a multiple chat, so there will be multiple references
    reference = [
        """
        The AI should:
    1. Give results related to the selenium webdriver python course
    2. There are 23 articles and 9 downloadable resources in the course]
        """
    ]

    # earlier user input was just query , now we have chat history as well
    sample = MultiTurnSample(user_input=conversations, reference_topics=reference)
    return sample
