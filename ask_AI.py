import os
import requests
from dotenv import load_dotenv

load_dotenv()


def ask_AI(
    system_prompt,
    messages,
    max_tokens=2000,
    temperature=0.5,
):
    # 从环境变量读取 API 密钥和请求地址
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL", "https://api.openai.com/v1/chat/completions")
    api_model = os.getenv("API_MODEL", "gpt-4")

    if not api_key:
        raise ValueError(
            "API key not found. Please set the ANTHROPIC_API_KEY environment variable."
        )

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    data = {
        "model": api_model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": messages},
        ],
        "stream": False,
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None
    try:
        response_json = response.json()
        print("response_json", response_json)
    except ValueError:
        print("Failed to parse JSON response")
        print("Response content:", response.text)
        return None

    if "choices" not in response_json or len(response_json["choices"]) == 0:
        print("Unexpected API response format")
        print("Response JSON:", response_json)
        return None

    return response_json["choices"][0]["message"]["content"]


# 示例用法
if __name__ == "__main__":
    system_prompt = "You are a helpful assistant."
    messages = "What is the weather like today?"

    try:
        response = ask_AI(system_prompt, messages)
        print("AI Response:", response)
    except Exception as e:
        print(f"An error occurred: {e}")
