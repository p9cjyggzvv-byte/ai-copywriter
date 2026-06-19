"""
ReAct Agent
============
思考 → 行动 → 观察 循环，可调用 RAG 知识库回答问题
"""

import sys
import json
import re
from src.utils import ask_llm, get_client
from src.rag import RAG


class ReActAgent:
    """ReAct 模式 Agent"""

    def __init__(self):
        self.knowledge = RAG()
        self.max_steps = 8

    def load_knowledge(self, filepath):
        """加载知识库"""
        self.knowledge.add_file(filepath)

    def run(self, question, verbose=True):
        """运行 Agent"""
        system_prompt = """你是一个能使用工具的 AI 助手。
你有两个工具可用：
1. search_knowledge(query) - 搜索知识库获取信息
2. calculate(expression) - 执行数学计算

每次回答请按以下格式：
思考：<当前思考>
行动：<工具名称>
输入：<工具输入>

或者当可以回答时：
思考：<总结>
最终答案：<完整回答>"""

        full_response = ""
        step = 0

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        while step < self.max_steps:
            step += 1
            if verbose:
                print(f"\n⏳ Step {step}...")

            response = ask_llm(
                messages,
                system=system_prompt,
                temp=0.5,
                max_tokens=500
            )

            if verbose:
                print(f"  🤔 {response[:200]}")

            # 检查是否有最终答案
            if "最终答案" in response:
                answer = response.split("最终答案")[-1].strip().strip("：:").strip()
                if verbose:
                    print(f"\n✅ 最终答案: {answer}")
                return answer

            # 解析工具调用
            action_match = re.search(r"行动[：:]\s*(\w+)", response)
            input_match = re.search(r"输入[：:]\s*(.+)", response)

            if action_match and input_match:
                action = action_match.group(1)
                tool_input = input_match.group(1).strip()

                if action == "search_knowledge":
                    result = self._search(tool_input)
                elif action == "calculate":
                    result = self._calc(tool_input)
                else:
                    result = f"未知工具：{action}"

                if verbose:
                    print(f"  🔧 {action}({tool_input}) → {result[:100]}...")

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"观察结果：{result}"})
            else:
                # 没有工具调用，认为已回答
                if verbose:
                    print(f"\n✅ 回答: {response}")
                return response

        return "已达最大步骤限制，请简化问题。"

    def _search(self, query):
        """搜索知识库"""
        return self.knowledge.query(query)

    def _calc(self, expression):
        """执行计算"""
        try:
            # 提取数学表达式
            numbers = re.findall(r'[\d+\-*/().]+', expression)
            if numbers:
                result = eval(numbers[0])
                return str(result)
            return "无法解析表达式"
        except Exception as e:
            return f"计算错误：{e}"


def demo():
    """演示"""
    agent = ReActAgent()
    agent.load_knowledge("data/knowledge_base.txt")
    print("=" * 50)
    print("🤖 ReAct Agent 演示")
    print("=" * 50)

    questions = [
        "AI 文案代写和工具开发的价格分别是多少？",
        "如果每天写 30 条文案，一个月能赚多少钱？",
    ]
    for q in questions:
        print(f"\n❓ 问题: {q}")
        print(f"{'─' * 40}")
        answer = agent.run(q)
        print(f"{'─' * 40}")
        print(f"💡 {answer}")


if __name__ == "__main__":
    demo()
