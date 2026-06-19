"""
健壮的 AI 文案生成器
=====================
工程示范：输入检查 + 错误处理 + 日志 + 重试机制
"""

import os
import sys
import logging
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

load_dotenv()


def get_client():
    """获取 API 客户端，带 Key 检查"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        log.error("DEEPSEEK_API_KEY 未设置！")
        log.error("请在 .env 文件中设置你的 API Key")
        sys.exit(1)

    if not api_key.startswith("sk-"):
        log.warning("API Key 格式似乎不对，应该以 sk- 开头")

    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def generate_copy(product, style="朋友圈", count=3, max_retries=3):
    """
    生成推广文案（带重试机制）

    参数:
        product: 产品名
        style: 文案风格
        count: 生成条数
        max_retries: 失败后重试次数

    返回:
        成功返回文案，失败返回错误信息
    """
    # --- 输入检查 ---
    if not product or not product.strip():
        return "错误：产品名不能为空"

    if count < 1 or count > 20:
        return "错误：文案条数请在 1-20 之间"

    valid_styles = ["朋友圈", "小红书", "抖音脚本", "公众号", "微博", "知乎", "淘宝详情"]
    if style not in valid_styles:
        return f"错误：不支持的风格「{style}」，支持的风格：{', '.join(valid_styles)}"

    # --- 构造请求 ---
    log.info(f"开始生成：{product}（{style}，{count}条）")
    client = get_client()

    # --- 带重试的 API 调用 ---
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "你是一个资深营销文案专家。"},
                    {"role": "user", "content": f"为「{product}」写{count}条{style}推广文案，每条不超过80字。"}
                ],
                temperature=0.8,
                max_tokens=500
            )

            content = response.choices[0].message.content
            log.info(f"生成成功，共{len(content)}字")
            return content

        except Exception as e:
            error_msg = str(e)
            log.warning(f"第{attempt}次尝试失败：{error_msg[:60]}")

            if attempt < max_retries:
                wait = attempt * 2  # 递增等待：2秒、4秒、6秒
                log.info(f"等待{wait}秒后重试...")
                sleep(wait)
            else:
                log.error(f"所有{max_retries}次尝试都失败了")
                return f"错误：API 调用失败，{error_msg}"


def batch_generate(products, style="朋友圈", count=3):
    """批量生成，逐个处理并统计结果"""
    results = []
    success = 0
    failed = 0

    log.info(f"开始批量处理：{len(products)} 个产品")

    for i, product in enumerate(products, 1):
        print(f"  [{i}/{len(products)}] {product}...", end=" ")
        content = generate_copy(product, style, count)

        if content.startswith("错误"):
            failed += 1
            print(f"❌ {content}")
        else:
            success += 1
            print("✅")
            results.append([product, style, content])

        sleep(0.5)  # 避免 API 限流

    # 统计报告
    log.info(f"批量完成：成功 {success}，失败 {failed}，共 {len(products)}")
    return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python robust_generator.py '产品名' [风格] [条数]")
        print("示例:")
        print("  python robust_generator.py '手工皮具钱包'")
        print("  python robust_generator.py '咖啡豆' 小红书 5")
        return

    product = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else "朋友圈"
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    result = generate_copy(product, style, count)
    print("\n" + "=" * 40)
    print(result)


if __name__ == "__main__":
    main()
