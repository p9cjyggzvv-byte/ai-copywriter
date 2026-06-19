import sys, os, json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def ask(prompt, system="You are a helpful assistant."):
    r = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=2000
    )
    return r.choices[0].message.content

def run_agent(task):
    # Step 1: 拆解任务
    steps_prompt = f"""将以下任务拆解成 3-5 个步骤，每个步骤一句话。
任务：{task}
只输出步骤列表，每行一个，不要序号。"""
    steps_text = ask(steps_prompt, "你是一个任务规划专家。")

    print("📋 任务拆解：")
    steps = [s.strip() for s in steps_text.split(chr(10)) if s.strip()]
    for i, s in enumerate(steps, 1):
        print(f"  Step {i}: {s}")

    # Step 2: 逐步执行
    context = ""
    for i, step in enumerate(steps, 1):
        print(f"
⏳ 执行 Step {i}...")
        result = ask(f"上一步结果：{context}

当前任务：{step}", "你是一个执行者，一步步完成任务。")
        print(f"  ✅ {result[:100]}...")
        context += f"
Step {i} ({step}) 结果：{result}"

    # Step 3: 汇总
    final = ask(f"基于以下执行记录，给出最终结果：{context}", "汇总执行结果。")
    return final

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python agent.py '你的任务'")
        sys.exit(1)
    task = sys.argv[1]
    print("=" * 50)
    print("🎯 任务:", task)
    print("=" * 50)
    result = run_agent(task)
    print("
" + "=" * 50)
    print("📦 最终结果:")
    print(result)
