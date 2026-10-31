import os
import json
import requests

def load_test_data(filename):
    dir=os.path.dirname(__file__)
    filename=os.path.join(dir,"testdata",filename)
    with open(filename,"r") as f:
        test_data=json.load(f)
    return test_data

def get_llm_response(testdata):
    ## making it dynamic
    responseDict = requests.post(
        "https://rahulshettyacademy.com/rag-llm/ask",
        json={
            "question": testdata["question"],
            "chat_history": [],
        },
    ).json()
    return responseDict