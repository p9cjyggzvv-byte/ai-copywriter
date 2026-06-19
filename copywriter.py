from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
if len(sys.argv) > 1:
    product = sys.argv[1]
else:
    product = input("请输入你的产品/服务名称：")
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个资深营销文案专家。输出简洁、有感染力、适合中文社交平台。"},
        {"role": "user", "content": f"为「{product}」写3条朋友圈推广文案，每条不超过80字，风格轻松自然。直接输出文案，不要序号和说明。"}
    ],
    temperature=0.8,
    max_tokens=500
)
print()
print("=" * 40)
print("✨ 生成的文案：")
print("=" * 40)
print(response.choices[0].message.content)
print("=" * 40)
