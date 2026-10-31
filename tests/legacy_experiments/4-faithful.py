import pytest
from ragas.metrics import Faithfulness



@pytest.mark.asyncio
@pytest.mark.parametrize("get_data",load_test_data("parameterize_data_faithfulness.json"),indirect=True)
async def test_faithfulness(llm_wrapper,get_data):
    faithful=Faithfulness(llm=llm_wrapper)
    result=await faithful.single_turn_ascore(sample=get_data)
    assert result>0.7
    

@pytest.fixture
def get_data(request):
    test_data=request.param
    response_dict = get_llm_response(test_data=test_data)

    retrieved_contexts = [
        doc["page_content"] for doc in response_dict.get("retrieved_docs", [])
    ]

    sample=SingleTurnSample(
        user_input=test_data["question"],
        response=response_dict["answer"],
        retrieved_contexts=retrieved_contexts,
    )
    return sample
