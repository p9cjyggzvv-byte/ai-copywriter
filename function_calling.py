import sys, os, json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 123*456"}
                },
                "required": ["expression"]
            }
        }
    }
]

def calculate(expression):
    try:
        return str(eval(expression))
    except:
        return "计算错误"

def run_with_tools(user_input):
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": user_input}],
        tools=tools,
        tool_choice="auto",
        max_tokens=1000
    )
    msg = r.choices[0].message
    if msg.tool_calls:
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            if name == "calculate":
                result = calculate(args["expression"])
                print(f"🔢 计算: {args['expression']} = {result}")
                r2 = client.chat.completions.create(
                    model="deepseek-v4-flash",
                    messages=[
                        {"role": "user", "content": user_input},
                        msg,
                        {"role": "tool", "tool_call_id": tc.id, "content": result}
                    ]
                )
                return r2.choices[0].message.content
    return msg.content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python function_calling.py '你的问题'")
        sys.exit(1)
    answer = run_with_tools(sys.argv[1])
    print("💡 回答:", answer)
