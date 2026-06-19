import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def ask_document(content, question):
    prompt = f"""请基于以下文档内容回答问题。

文档内容：
---
{content[:3000]}
---

问题：{question}

要求：
1. 只基于文档内容回答，如果文档中没有相关信息，请明确说文档中没有提到
2. 用中文回答
3. 回答要简洁准确"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "你是一个文档分析师，严格基于提供的文档回答问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return resp.choices[0].message.content
    except Exception as e:
        return '[ERROR] ' + str(e)

if len(sys.argv) < 3:
    print('用法: python ask_doc.py 文件名 "你的问题"')
    print('示例: python ask_doc.py my_notes.txt "这篇文章主要讲了什么？"')
    sys.exit(1)

filepath = sys.argv[1]
question = sys.argv[2]

if not os.path.exists(filepath):
    print('文件不存在: ' + filepath)
    sys.exit(1)

content = read_file(filepath)
print()
print('=' * 50)
print('📄 文档问答')
print('=' * 50)
print('文档: ' + filepath)
print('字数: ' + str(len(content)))
print('问题: ' + question)
print('=' * 50)
print()

answer = ask_document(content, question)
print('💡 回答:')
print(answer)
print()
