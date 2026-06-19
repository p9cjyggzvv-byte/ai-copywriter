"""
AI 数据分析
===========
上传 CSV/Excel，AI 自动分析数据并出报告
"""

import sys
import csv
import io
from src.utils import ask_llm


def analyze_csv(filepath):
    """分析 CSV 文件内容"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    rows = content.strip().split("\n")
    header = rows[0].split(",") if rows else []
    data_rows = rows[1:6]  # 只看前5行做预览

    prompt = f"""分析以下 CSV 数据：

表头：{', '.join(header)}
数据预览（前5行）：
{chr(10).join(data_rows[:5])}
总行数：{len(rows) - 1}

请给出：
1. 数据概况（每列的含义和数据类型）
2. 关键发现（如果有数值列，计算总和/平均值）
3. 建议（这些数据能用来做什么）"""
    return ask_llm(
        [{"role": "user", "content": prompt}],
        system="你是一个数据分析师。输出简洁专业的分析报告。",
        temp=0.3,
        max_tokens=1500
    )


def query_data(question, filepath):
    """基于数据回答问题"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    prompt = f"""基于以下数据回答问题。

数据：
{content[:2000]}

问题：{question}

只基于数据回答，如果数据中没有相关信息就说'数据中未提及'。"""
    return ask_llm(
        [{"role": "user", "content": prompt}],
        system="数据分析师",
        temp=0.2,
        max_tokens=1000
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python src/data_analyzer.py 文件.csv [问题]")
        sys.exit(1)

    filepath = sys.argv[1]
    if len(sys.argv) > 2:
        answer = query_data(sys.argv[2], filepath)
        print(f"\n💡 {answer}")
    else:
        report = analyze_csv(filepath)
        print(f"\n📊 分析报告：\n{report}")
