#!/usr/bin/env python3
"""AI 文案工具集 — 统一入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print("""AI 文案工具集 v2.0

用法:
  python main.py copy "产品名"              生成文案
  python main.py batch [文件.csv]            批量处理
  python main.py matrix "原文" "平台1,平台2"  一文多发
  python main.py ask 文件 "问题"             文档问答
  python main.py agent "任务描述"            Agent 执行
  python main.py calc "计算式"               计算器
  python main.py web                         启动网页
""")
        return

    cmd = sys.argv[1]

    if cmd == "copy":
        from src.generators import generate_copy
        product = sys.argv[2] if len(sys.argv) > 2 else input("产品名: ")
        result = generate_copy(product)
        print("\n" + "=" * 40)
        print(result)

    elif cmd == "batch":
        from src.generators import batch_generate
        input_file = sys.argv[2] if len(sys.argv) > 2 else "data/projects.csv"
        output_file = sys.argv[3] if len(sys.argv) > 3 else "data/results.csv"
        batch_generate(input_file, output_file)

    elif cmd == "matrix":
        from src.generators import content_matrix
        original = sys.argv[2] if len(sys.argv) > 2 else input("原文: ")
        platforms = sys.argv[3].split(",") if len(sys.argv) > 3 else ["朋友圈", "小红书", "抖音脚本"]
        results = content_matrix(original, platforms)
        for p, r in results.items():
            print(f"\n📱 {p}\n{'─' * 30}\n{r}")

    elif cmd == "ask":
        from src.generators import ask_document
        filepath = sys.argv[2] if len(sys.argv) > 2 else input("文件名: ")
        question = sys.argv[3] if len(sys.argv) > 3 else input("问题: ")
        answer = ask_document(filepath, question)
        print(f"\n💡 {answer}")

    elif cmd == "agent":
        from src.agents import run_agent
        task = sys.argv[2] if len(sys.argv) > 2 else input("任务: ")
        result = run_agent(task)
        print(f"\n📦 结果:\n{result}")

    elif cmd == "calc":
        from src.agents import function_calling
        question = sys.argv[2] if len(sys.argv) > 2 else input("问题: ")
        answer = function_calling(question)
        print(f"💡 {answer}")

    elif cmd == "web":
        os.system("streamlit run app.py")

    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
