import csv
import sys
import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def generate(product, style="朋友圈", count=3):
    """为一个产品生成推广文案"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "你是一个资深营销文案专家。输出简洁、有感染力。"},
                {"role": "user", "content": f"为「{product}」写{count}条{style}推广文案，每条不超过80字。直接输出文案，不要序号。"}
            ],
            temperature=0.8,
            max_tokens=500
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[ERROR] {str(e)}"

# --- 主流程 ---
input_file = sys.argv[1] if len(sys.argv) > 1 else "products.csv"
output_file = sys.argv[2] if len(sys.argv) > 2 else "output.csv"
style = sys.argv[3] if len(sys.argv) > 3 else "朋友圈"
count = int(sys.argv[4]) if len(sys.argv) > 4 else 3

# 读取产品列表
products = []
with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # 跳过表头
    for row in reader:
        if row:
            products.append(row[0].strip())

print(f"📂 读取到 {len(products)} 个产品")
print(f"🎨 风格：{style}  |  每个 {count} 条文案")
print("-" * 40)

# 逐个生成
results = []
for i, product in enumerate(products, 1):
    print(f"⏳ [{i}/{len(products)}] {product}...")
    content = generate(product, style, count)
    results.append([product, style, content.replace(chr(10), " | ")])
    sleep(0.5)  # 礼貌停顿，避免API限流

# 写入结果
with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["产品", "风格", "文案"])
    writer.writerows(results)

print(f"
✅ 完成！结果已保存到 {output_file}")
