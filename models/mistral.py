import requests
import json

api_key = 'DcCuwA1kbtGMShFRunnTJi6OtVgjQxGG'

def call_chat_endpoint(data, api_key=api_key):
    url = "https://codestral.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

def call_fim_endpoint(data, api_key=api_key):
    url = "https://codestral.mistral.ai/v1/fim/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"
    
prompt="""Sure, here is a simple function in Python that adds up two numbers:

def add_two_numbers(num1, num2):
    return num1 + num2

You can use this function like this:
result = add_two_numbers(5, 3)
print(result)  # Outputs: 8

This function takes two arguments, num1 and num2, and returns their sum.\ndef test_add_two_numbers():""" 

suffix="" 

data = { "model": "codestral-latest", "prompt": prompt, "suffix": suffix, "temperature": 0 }

response = call_fim_endpoint(data)
print(response)

prompt = "Please write me a function that adds up two numbers"
data = {
    "model": "codestral-latest",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0
}

response = call_chat_endpoint(data)
print(response)