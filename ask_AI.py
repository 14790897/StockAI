import requests


def ask_AI(
    system_prompt,
    messages,
    model="claude-3-haiku-20240307",
    max_tokens=2000,
    temperature=0.5,
):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": messages,
    }
    response = requests.post(
        "https://api.anthropic.com/v1/messages", headers=headers, json=data
    )
    response_json = response.json()
    return response_json["content"][0]["text"]
