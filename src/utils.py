import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )


def ask_llm(messages, system="You are a helpful assistant.", temp=0.7, max_tokens=2000):
    client = get_client()
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": system}, *messages],
        temperature=temp,
        max_tokens=max_tokens
    )
    return r.choices[0].message.content
