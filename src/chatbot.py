"""
AI 客服机器人
=============
基于 RAG 知识库的客服问答机器人，支持多轮对话
"""

import sys
import os
from src.rag import RAG


class ChatBot:
    """AI 客服机器人"""

    def __init__(self):
        self.knowledge = RAG()
        self.history = []

    def load_knowledge(self, filepath):
        """加载知识库（FAQ、产品手册等）"""
        self.knowledge.add_file(filepath)
        print(f"✅ 知识库加载完成：{filepath}")

    def ask(self, question):
        """回答一个问题，带上下文"""
        # 带上历史记录
        context = ""
        if self.history:
            context = "历史对话：\n" + "\n".join(
                [f"用户：{q}\n客服：{a[:50]}..." for q, a in self.history[-3:]]
            )

        full_question = f"{context}\n\n用户新问题：{question}" if context else question
        answer = self.knowledge.query(full_question)
        self.history.append((question, answer))
        return answer

    def chat_loop(self):
        """交互式对话"""
        print("\n" + "=" * 50)
        print("💬 AI 客服机器人")
        print("=" * 50)
        print("输入 'quit' 退出，输入 'clear' 清空历史\n")

        while True:
            question = input("你：").strip()
            if question.lower() == "quit":
                print("👋 再见！")
                break
            if question.lower() == "clear":
                self.history = []
                print("🧹 历史已清空\n")
                continue
            if not question:
                continue

            answer = self.ask(question)
            print(f"🤖 {answer}\n")


def demo():
    """演示：客服机器人"""
    bot = ChatBot()
    # 加载知识库
    kb_files = ["data/knowledge_base.txt"]
    for f in kb_files:
        if os.path.exists(f):
            bot.load_knowledge(f)

    # 测试
    print("\n📝 测试问答：")
    tests = [
        "AI 文案代写怎么收费？",
        "包月服务包含什么？",
    ]
    for q in tests:
        print(f"\n❓ {q}")
        print(f"💡 {bot.ask(q)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        bot = ChatBot()
        for f in ["data/knowledge_base.txt"]:
            if os.path.exists(f):
                bot.load_knowledge(f)
        bot.chat_loop()
    else:
        demo()
