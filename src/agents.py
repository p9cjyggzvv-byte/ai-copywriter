import json
from src.utils import ask_llm, get_client


def run_agent(task):
    steps_text = ask_llm(
        [{"role": "user", "content": f"将任务拆成3-5步，每行一步：{task}"}],
        system="任务规划专家"
    )
    steps = [s.strip() for s in steps_text.split(chr(10)) if s.strip()]
    print("📋 拆解步骤:")
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")

    context = ""
    for i, step in enumerate(steps, 1):
        print(f"\n⏳ 执行第{i}步...")
        result = ask_llm(
            [{"role": "user", "content": f"上一步: {context}\n当前: {step}"}],
            system="逐步执行任务"
        )
        context += f"\nStep {i}: {result}"

    return ask_llm(
        [{"role": "user", "content": f"汇总执行结果: {context}"}],
        system="汇总报告"
    )


def function_calling(question):
    client = get_client()
    tools = [{
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    }]
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": question}],
        tools=tools,
        tool_choice="auto",
        max_tokens=1000
    )
    msg = r.choices[0].message
    if msg.tool_calls:
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = str(eval(args["expression"]))
            print(f"🔢 计算: {args['expression']} = {result}")
            r2 = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "user", "content": question},
                    msg,
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                ]
            )
            return r2.choices[0].message.content
    return msg.content
