"""
自动化工作流
===========
定时任务、自动分发、批量处理流水线
"""

import os
import csv
import schedule
import time
from datetime import datetime
from src.generators import generate_copy


def daily_content_job():
    """每日内容生成任务"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n⏰ [{today}] 执行每日内容生成任务")

    products_file = "data/products.csv"
    if not os.path.exists(products_file):
        print("⚠️ 无产品列表，跳过")
        return

    results = []
    with open(products_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row.get("产品名称", "").strip()
            if not product:
                continue
            print(f"  📝 生成：{product}")
            content = generate_copy(product)
            results.append([today, product, content])

    # 保存到今日文件
    output_file = f"data/日报_{today}.csv"
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["日期", "产品", "文案"])
        writer.writerows(results)
    print(f"✅ 已保存到 {output_file}")


def weekly_report_job():
    """每周报告任务"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📊 [{today}] 生成周报")

    # 检查本周生成了多少内容
    data_dir = "data/"
    count = 0
    for f in os.listdir(data_dir):
        if f.startswith("日报_") and f.endswith(".csv"):
            with open(os.path.join(data_dir, f), "r", encoding="utf-8") as cf:
                count += sum(1 for _ in csv.reader(cf)) - 1  # 减表头

    print(f"  本周共生成 {count} 条文案")
    return count


def setup_schedule():
    """配置定时任务"""
    # 每天早上 9 点执行
    schedule.every().day.at("09:00").do(daily_content_job)
    # 每周一上午 10 点执行
    schedule.every().monday.at("10:00").do(weekly_report_job)

    print("⏰ 定时任务已配置")
    print("  • 每天 09:00 — 生成当日文案")
    print("  • 每周一 10:00 — 生成周报")
    print("按 Ctrl+C 停止\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


def run_once():
    """手动执行一次"""
    print("🚀 手动执行工作流")
    daily_content_job()
    weekly_report_job()
    print("✅ 工作流执行完毕")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        setup_schedule()
    else:
        run_once()
